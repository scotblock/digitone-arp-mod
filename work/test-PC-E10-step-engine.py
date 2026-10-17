"""Execute native E09A consumer and step engine, bounding stock exits."""
from pathlib import Path
import json,struct,sys
prefix=Path('work/test-E09A-consumer-chord-contracts.py').read_text().split('checks=[];init();')[0]
exec(compile(prefix,'E10-native-consumer-fixture','exec'))
from emu import cfisa
audit={};exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0],audit)
cfg=json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text())
code=Path('work/os144/PC_ONLY-E10-step-engine.bin').read_bytes();X=cfg['state']
for p in range(cfg['base'],cfg['base']+len(code),4096):m.ensure(p)
u.mem_write(cfg['base'],code)
for patch in cfg['patches']:
 assert bytes(u.mem_read(patch['site'],6)).hex()==patch['before']
 u.mem_write(patch['site'],bytes.fromhex(patch['after']))
for r in cfg['regions']:
 data=code[r['base']-cfg['base']:r['base']-cfg['base']+r['bytes']];pos=0
 while pos<len(data):
  ins=cfisa.decode(lambda x:int.from_bytes(data[pos+x:pos+x+2],'big'),r['base']+pos)
  assert ins.length>0 and not ins.flags&(cfisa.FPU|cfisa.LINEF|cfisa.ILLEGAL) and not audit['move_restriction'](int.from_bytes(data[pos:pos+2],'big')),(r,pos,ins)
  pos+=ins.length
 m.install_isa_patches_scoped(data,r['base'])

def sequence(offsets,mask=None,word=0x80000080,owner=None,enabled=True):
 u.mem_write(X,code[X-cfg['base']:X-cfg['base']+64])
 for off,value in [(4,int(enabled)),(8,len(offsets)),(20,(1<<len(offsets))-1 if mask is None else mask),(24,word),(28,KIT+0x5ce if owner is None else owner)]:put(X+off,value)
 u.mem_write(X+32,bytes([v&255 for v in offsets]))

def run_steps(chord,offsets,mask=None,word=0x80000080,steps=None,owner=None,enabled=True):
 init();sequence(offsets,mask,word,owner,enabled);event(chord,now=100000000)
 rows=[]
 for i in range(steps or len(offsets)):
  if i:event([],kind=3,now=100000000+i*900000)
  target=consume();note=u.mem_read(A+20,1)[0] if target==A else None
  if target==A:retire()
  rows.append(note)
 return rows

checks=[]
notes=run_steps([60],list(range(8)));assert notes==[60,62,64,65,67,69,71,72],notes
checks.append({'case':'C Ionian scale degrees','notes':notes})
notes=run_steps([62],list(range(8)),word=0x80000082);assert notes==[62,64,66,67,69,71,73,74],notes
checks.append({'case':'D Ionian scale degrees','notes':notes})
notes=run_steps([60],[0,1,2,3],mask=0b0101,steps=8);assert notes==[60,None,64,None,60,None,64,None],notes
assert get(X+48)==4 and get(S+280)==0
checks.append({'case':'rests advance time and wrap without allocating descriptors','notes':notes})
notes=run_steps([60],[-1,-2,0,1]);assert notes==[59,57,60,62],notes
checks.append({'case':'signed negative scale offsets','notes':notes})
notes=run_steps([127],[1,-1,0]);assert notes==[None,125,127],notes
checks.append({'case':'outside MIDI range is a rest, not byte wrapping','notes':notes})
notes=run_steps([67,60,64],[0,1,2]);assert notes==[60,65,71],notes
checks.append({'case':'offsets follow ascending chord selection','notes':notes})
notes=run_steps([60],[0,7],owner=KIT+0x672);assert notes==[60,60],notes
checks.append({'case':'other pattern owner cannot use stored offsets','notes':notes})
notes=run_steps([60],[7,7],enabled=False);assert notes==[60,60],notes
checks.append({'case':'disabled sequencer preserves ordinary arp','notes':notes})
notes=run_steps([60],[0,1],mask=0,steps=5);assert notes==[None]*5 and get(S+280)==0
checks.append({'case':'all-rest pattern remains silent and never claims arena','notes':notes})
put(TP,2);event([],kind=3,now=110000000);assert consume()==E and get(S+8)==get(S+16)==get(X+12)==0
checks.append({'case':'Stop clears generation and sequence cursor'})
init();sequence([0,1,2]);event([60]);assert consume()==A
before=bytes(u.mem_read(A,64));cursor=get(X+12);event([],kind=3,now=100900000);assert consume()==E
assert get(X+12)==cursor and bytes(u.mem_read(A,64))==before;retire()
checks.append({'case':'busy arena does not advance sequence or overwrite note'})
event([60],now=102000000);assert consume()==A and u.mem_read(A+20,1)[0]==60;retire()
checks.append({'case':'fresh sequenced trig restarts at step one'})
out={'passed':True,'PC_only':True,'native_code_executed':True,'checks':checks,'groups':len(checks),
     'limits':cfg['limits']+['Descriptors, clock, scale word and sequence configuration are fixtures. Stock consumer exits are bounded; no audio/MIDI port delivery test here.']}
Path('outputs/Digitone-E10-PC-step-engine.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
