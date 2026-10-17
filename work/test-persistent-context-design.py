"""PC specification only: no firmware loading, patching or binary output."""
from dataclasses import dataclass
from pathlib import Path
import json
@dataclass(frozen=True)
class Snapshot:
    root: int
    scale: int
    source: int
    def __post_init__(self):
        assert 0 <= self.root <= 127 and -1 <= self.scale <= 34 and 0 <= self.source < 4
    def word(self): return 0x80000000 | self.root | ((self.scale+1)<<7) | (self.source<<13)

# Explicit allocation extent; stock record stride/count stay unchanged.
REGIONS = {'events':(32,128,4),'held':(544,512,4),'sequencer':(2592,4,4),
           'queue':(2608,64,4),'accepted':(2864,4,16)}
TRAILER=2928
REQUEST=0x14100+TRAILER

def key(address):
    for name,base,count,stride in [('events',0x4199da94,128,72),
        ('sequencer',0x419a304c,4,72),('queue',0x431dbfb8,64,20),
        ('accepted',0x41345f08,4,72)]:
        d=address-base
        if 0<=d<count*stride and d%stride==0:return name,d//stride
    for track in range(4):
        d=address-(0x431d1758+track*0x2a18+0x414)
        if 0<=d<128*72 and d%72==0:return 'held',track*128+d//72
    return None

class Sidecar:
    def __init__(self):
        self.entries={};self.accepted={};self.ready=True;self.busy=0;self.capture_fault=False
    def capture(self, root, scale, source):
        if not self.ready or self.busy or self.capture_fault:return None
        return Snapshot(root,scale,source)
    def initialize(self,k,snapshot=None): self.entries[k]=snapshot
    def candidate(self,k):
        if k and k[0]=='accepted':
            a=self.accepted.get(k[1]);return a[1] if a else None
        return self.entries.get(k)
    def copy(self,dst,src):
        assert not(dst and dst[0]=='accepted'), 'retained destination needs explicit accepted-identity commit'
        self.entries[dst]=self.candidate(src)
    def reclaim(self,k): self.entries.pop(k,None)
    def accept(self,track,identity,event,new_identity=True):
        if new_identity:self.accepted[track]=(identity,self.entries.get(event))
    def pitch(self,track,identity,active=True,synth=True,arp=True,selected=True):
        if not(self.ready and active and synth and arp and selected):return None
        a=self.accepted.get(track)
        return a[1] if a and a[0]==identity else None
    def ordinary_reset(self):
        # Only queued pool-event entries are reclaimed by a modeled drain.
        for k in list(self.entries):
            if k[0]=='events':self.reclaim(k)
    def setup_reentry(self):
        # Persistent feature state is never reconstructed from payload counts.
        # This does not model or certify stock pool reconstruction.
        return None

checks=[]
def check(label,ok):
    assert ok,label
    checks.append(label)

ranges=[(o,o+n*s,name) for name,(o,n,s) in REGIONS.items()]
check('layout excludes 32-byte header and has no overlapping entries',all(a>=32 for a,b,n in ranges) and all(b<=c or d<=a for i,(a,b,n) in enumerate(ranges) for c,d,m in ranges[i+1:]))
check('exact extent and unchanged rounded allocation',max(b for a,b,n in ranges)==TRAILER and REQUEST==0x14c70 and (1<<(REQUEST-1).bit_length())==0x20000)
for name,base,count,stride in [('events',0x4199da94,128,72),('sequencer',0x419a304c,4,72),('queue',0x431dbfb8,64,20),('accepted',0x41345f08,4,72)]:
    check(name+' exact address mapping',all(key(base+i*stride)==(name,i) for i in range(count)))
    check(name+' rejects interior addresses',all(key(base+i*stride+1) is None for i in range(count)))
check('all 512 held template addresses mapped',all(key(0x431d1758+t*0x2a18+0x414+n*72)==('held',t*128+n) for t in range(4) for n in range(128)))
check('unrecognized temporary address rejected',key(0x30001000) is None)
s=Sidecar();a=s.capture(0,0,0);b=s.capture(2,5,1)
h=('held',60);e=('events',0);q=('queue',0)
s.initialize(h,a);s.copy(e,h);s.accept(0,7,e)
s.initialize(h,b)
check('cache replacement leaves queued and accepted snapshots independent',s.entries[e]==a and s.pitch(0,7)==a)
s.reclaim(e);s.initialize(e)
check('recycled event cannot inherit prior context',s.entries[e] is None)
s.initialize(q,a);s.copy(e,q);s.reclaim(q);s.initialize(q,b)
check('queue-to-event transfer survives immediate node reuse',s.entries[e]==a)
s.busy=1
check('busy update blocks new capture but preserves accepted notes',s.capture(2,5,1) is None and s.pitch(0,7)==a)
s.capture_fault=True;s.busy=0
check('pattern capture failure preserves existing immutable snapshot',s.capture(2,5,1) is None and s.pitch(0,7)==a)
s.initialize(e,None);s.accept(0,7,e,False)
check('additive or rejected input preserves accepted snapshot',s.pitch(0,7)==a)
s.accept(0,8,e)
check('contextless new identity replaces old snapshot with fallback',s.pitch(0,8) is None and s.pitch(0,7) is None)
s.initialize(e,a);s.accept(0,9,e);s.initialize(('events',1),b);s.accept(1,9,('events',1))
check('remapped continuing tick uses destination accepted context',s.pitch(1,9)==b and s.pitch(0,9)==a)
s.ordinary_reset();s.setup_reentry()
check('reset/reentry preserves retained context and cached candidates',s.pitch(0,9)==a and s.entries[h]==b)
check('empty active arp rejects retained context without clearing it',s.pitch(0,9,active=False) is None and s.pitch(0,9)==a)
check('sustain lifetime retains context until actual empty-list state',s.pitch(1,9,active=True)==b and s.pitch(1,9,active=False) is None)
check('missing source copy explicitly clears destination',s.copy(e,('unknown',0)) is None and s.entries[e] is None)
s.ready=False
check('unready layout blocks capture and output context',s.capture(0,0,0) is None and s.pitch(1,9) is None)
words={Snapshot(r,c,t).word() for r in range(128) for c in range(-1,35) for t in range(4)}
check('all 18432 value encodings unique and nonzero',len(words)==18432 and 0 not in words)
result={'kind':'PC specification, not firmware execution','passed':len(checks),'checks':checks,'trailer_bytes':TRAILER,'request_hex':hex(REQUEST),'address_classes_assumed':'bounded candidates; exhaustive firmware coverage remains unproved','not_tested':['actual allocator','atomic hook ordering','cold setup failure continuation','pattern writer completeness','unknown event producers/copies','hardware']}
Path('outputs/Digitone-persistent-sidecar-design-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
