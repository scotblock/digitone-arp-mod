"""OS 1.42 reserved-RAM route: read-only firmware, ephemeral PC overlays."""
import pathlib,json,hashlib
h={};exec(pathlib.Path('work/test-actual-capture-and-pitch.py').read_text().split('\nchecks=[];cases=[];OWNER=')[0],h)
t={};exec(pathlib.Path('work/trace-intervening-startup.py').read_text().split('\nm,owner=fresh()')[0],t)
s=t['s'];n=t['n'];b=t['b'];base=t['base'];checks=[];cases=[]
def check(label,ok):assert ok,label;checks.append(label)
RAM=0x47be0000;RAMEND=0x47c00000;ALIAS=RAM+0x08000000;BSS=RAM+0x1004;PTR=BSS-4;STAGE=base+len(b)
# Move existing helpers into .run; separate pointer adapts their existing offset
# convention without replacing or enlarging the stock allocator's owner.
layout={};off=0
for name,old in h['names'].items():
 if name in ['init_preflight','init_ready']:continue
 code=h['fixtures'][old];layout[name]={'old':old,'address':RAM+off,'size':len(code)};off+=len(code)
runblob=bytearray()
for name,item in layout.items():
 original=h['fixtures'][item['old']];code=bytearray(original)
 # Absolute references may target an internal return label, not only an entry.
 for j in range(0,len(original)-3,2):
  value=int.from_bytes(original[j:j+4],'big')
  for otheritem in layout.values():
   if otheritem['old']<=value<otheritem['old']+otheritem['size']:
    code[j:j+4]=(otheritem['address']+value-otheritem['old']).to_bytes(4,'big');break
 code=bytes(code).replace(bytes.fromhex('4199d590'),PTR.to_bytes(4,'big'));runblob.extend(code)
INIT=RAM+len(runblob);init=n['initcode'];TRAMP=INIT+len(init)
init=init.replace(n['TRAMP2'].to_bytes(4,'big'),TRAMP.to_bytes(4,'big')).replace(bytes.fromhex('4199d590'),PTR.to_bytes(4,'big'))
runblob.extend(init);runblob.extend(n['tramp']);runblob.extend(bytes((-len(runblob))%4));runblob=bytes(runblob)
check('code and contexts fit reserved budget',RAM+len(runblob)<=PTR and BSS+0xb70<RAMEND)
# Boot order follows Elekloader core, translated into the existing assembler.
a=h['Asm']();a.emit('41f9'+(STAGE+0x100).to_bytes(4,'big').hex()+'43f9'+RAM.to_bytes(4,'big').hex()+'203c'+(len(runblob)//4).to_bytes(4,'big').hex());a.label('copy');a.emit('22d85380');a.branch('6600','copy')
a.emit('43f9'+PTR.to_bytes(4,'big').hex()+'203c'+((0xb70+4)//4).to_bytes(4,'big').hex());a.label('zero');a.emit('42995380');a.branch('6600','zero')
# Build metadata header and private compatibility pointer; ready remains zero.
a.emit('23fc'+(BSS-0x14100).to_bytes(4,'big').hex()+PTR.to_bytes(4,'big').hex())
for addr,value in [(BSS,0x534c4332),(BSS+4,2),(BSS+8,0xb70)]:a.emit('23fc'+value.to_bytes(4,'big').hex()+addr.to_bytes(4,'big').hex())
h['absolute'](a,'4ef9',0x40001df4);boot=a.done();assert len(boot)<=0x100
check('stock early hook matches Elekloader signature',b[0x40000538-base:0x4000053e-base].hex()=='4eb940001df4')
check('stock entry establishes DDR stack top',b[0x400004f2-base:0x400004f8-base].hex()=='2e7c48000000')
check('reserved region leaves four MB below entry stack top',0x48000000-RAMEND==0x400000)
check('reserved region excludes clear and heap',RAM>0x431dc690 and RAM>0x429a38c0)
# Literal screen is deliberately not a global ownership proof.
hits={}
for label,lo,hi in [('cached',RAM,RAMEND),('uncached',ALIAS,ALIAS+0x20000)]:
 hits[label]=[{'offset':hex(base+i),'value':hex(int.from_bytes(b[i:i+4],'big'))} for i in range(0,len(b)-3,2) if lo<=int.from_bytes(b[i:i+4],'big')<hi]
# Fetch overlays only. Stock startup clear and initializer remain original.
def fetch(pc):
 m=s['active']
 if pc==0x40000538:return bytes.fromhex('4eb9')+STAGE.to_bytes(4,'big')
 if pc==0x400f0504:return bytes.fromhex('4ef9')+INIT.to_bytes(4,'big')+bytes.fromhex('4e714e71')
 if STAGE<=pc<STAGE+len(boot):return boot[pc-STAGE:pc-STAGE+16]
 if RAM<=pc<RAM+len(runblob):return bytes(m.read(pc+j,1) for j in range(min(16,RAM+len(runblob)-pc)))
 return b[pc-base:pc-base+16]
s['placedfetch']=fetch;s['RANGES'].extend([(STAGE,STAGE+len(boot)),(RAM,RAM+len(runblob))]);s['loop_pcs'][0x400004d2]=0x400004de
# Observe readiness while stock initializer mutates its own pool.
def observe(m,pc):
 if pc in getattr(m,'startup_stops',[]):m.stop_pc=pc;raise t['Stop']()
 if 0x400f050e<=pc<0x400f05d0:
  assert m.read(BSS+12,4)==0 and m.sr&0xff00==0x2700
s['observe_placed']=observe
src=t['src'].replace("   elif m=='nop':pass","   elif m in ('nop','tpf'):pass\n   elif m=='sgt':self.put(ops[0],1,255 if not self.sr&4 and not (bool(self.sr&8)^bool(self.sr&2)) else 0)")
exec('if True:\n'+src,s)
def fresh():
 m=n['machine']();m.__class__=t['StartupMachine'];m.hardware={};m.mmio_writes=[];m.startup_stops=[];m.run=s['run'].__get__(m,t['StartupMachine']);s['active']=m
 m.map(0x47fe0000,0x20000);m.reg['a7']=0x48000000;m.map(0x80000000,0x10000);m.map(0,4);m.map(RAM-16,0x2000+32);m.map(STAGE,0x100+len(runblob));m.map(0x4199d590,4)
 for j,v in enumerate(runblob):m.write(STAGE+0x100+j,1,v)
 for j in range(0x2000):m.write(RAM+j,1,0xa5)
 m.write(RAM-1,1,0x5a);m.write(BSS+0xb70,1,0x5a);m.write(0x4199d590,4,0);m.map(0xfc044000,4);return m
m=fresh();m.startup_stops=[0x40000568]
try:m.run(0x40000538)
except t['Stop']:pass
check('copied helpers survive full stock clear',bytes(m.read(RAM+j,1) for j in range(len(runblob)))==runblob)
check('bootstrap leaves stock owner unallocated',m.read(0x4199d590,4)==0)
check('private pointer addresses reserved header',m.read(PTR,4)+0x14100==BSS)
check('cold metadata unready with contexts cleared',m.read(BSS+12,4)==0 and all(m.read(BSS+j,1)==0 for j in range(12,0xb70)))
check('boot destination guards preserved',m.read(RAM-1,1)==0x5a and m.read(BSS+0xb70,1)==0x5a)
check('stock cache handoff instructions execute after copy',any(selector==2 and value==0xa50ce100 for selector,value in m.controls))
bootsteps=len(m.steps);m.reg['a7']=0x48000000;m.startup_stops=[0x4009bcc4];before=len(m.steps)
try:m.run(0x4009bcb8)
except t['Stop']:pass
stockowner=m.read(0x4199d590,4)
check('full stock initializer returns to actual caller',m.stop_pc==0x4009bcc4)
check('stock initializer allocates ordinary owner',stockowner==0x419a38c0)
check('separate contexts ready after stock return',m.read(BSS+12,4)==1)
check('stock records retain original stride and links',all(m.read(stockowner+j*0x504+16,4)==(stockowner+(j+1)*0x504 if j<63 else 0) for j in range(64)))
check('stock initialization preserves reserved code',bytes(m.read(RAM+j,1) for j in range(len(runblob)))==runblob)
initsteps=len(m.steps)-before;m.startup_stops=[]
# Actual capture and membership instructions now run from reserved RAM.
PAT=0x29000000;m.map(PAT,4*0x3d0);scale=json.loads(pathlib.Path('outputs/Digitone-OS1.42-scale-map.json').read_text());rows={x['raw_scale']:x['pitch_classes'] for x in scale['scales']}
for track in range(4):
 m.write(PAT+track*0x3d0+0x3cb,1,60+track);m.write(PAT+track*0x3d0+0x3ce,1,0)
 word=m.run(layout['capture']['address'],(PAT,track));check('reserved capture preserves source track '+str(track),word==0x80000000|(60+track)|(1<<7)|(track<<13))
 for note in [0,1,61,64,126,127]:
  got=m.run(layout['quantize']['address'],(note,word));want=min((j for j in range(128) if (j-(60+track))%12 in rows[0]),key=lambda j:(abs(j-note),j));check(f'reserved quantizer track {track} note {note}',got==want)
 # Fixed pool candidate storage cannot mutate original event contents.
 event=0x4199da94+track*72;eventbytes=bytes(m.read(event+j,1) for j in range(72));m.run(layout['candidate_store']['address'],(event,word));check('reserved candidate uses separate sidecar '+str(track),m.read(BSS+32+track*4,4)==word and bytes(m.read(event+j,1) for j in range(72))==eventbytes)
# Reentry must erase stale snapshots without moving the stock owner.
m.write(BSS+32,4,0xffffffff);m.startup_stops=[0x4009bcc4]
try:m.run(0x4009bcb8)
except t['Stop']:pass
check('initializer reentry erases stale context',m.read(BSS+32,4)==0 and m.read(BSS+12,4)==1)
check('initializer reentry preserves stock owner and private pointer',m.read(0x4199d590,4)==stockowner and m.read(PTR,4)==BSS-0x14100)
check('original SysEx unchanged',hashlib.sha256(pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx').read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
check('firmware main unchanged',hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
r={'checks':checks,'check_count':len(checks),'firmware_modified':False,'placement':{'region':[hex(RAM),hex(RAMEND)],'uncached_alias':[hex(ALIAS),hex(ALIAS+0x20000)],'code_bytes':len(runblob),'bootstrap_bytes':len(boot),'metadata_bytes':0xb70,'private_pointer':hex(PTR),'metadata':hex(BSS),'occupied_end':hex(BSS+0xb70),'source_fixture':hex(STAGE)},'layout':layout,'literal_screen':hits,'execution':{'startup_instructions':bootsteps,'initializer_instructions':initsteps,'stock_owner':hex(stockowner),'stock_clear_interval':['0x40242000','0x431dc690'],'stock_heap_interval':['0x419a38c0','0x429a38c0']},'limits':['No full OS1.42 settled run or global computed-pointer/stack/DMA ownership proof.','Arp tests cover relocated capture, pool candidate store and quantizer, not complete queued/live producer coverage or full pitch insertion.','Copies use a supplied already-decoded RAM extension; no repacking or full loader execution.','CPU cache registers recorded, physical execution/cache coherence not emulated.','All fixtures are PC-only; stock firmware files unchanged.']}
pathlib.Path('outputs/Digitone-reserved-RAM-route-results.json').write_text(json.dumps(r,indent=2));print(json.dumps({'checks':len(checks),'placement':r['placement'],'execution':r['execution'],'literal_hits':{k:len(v) for k,v in hits.items()}},indent=2))
