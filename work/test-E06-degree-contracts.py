from pathlib import Path
import json,sys,struct,hashlib,random,traceback
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine,call
native_call=call
def call(m,entry,args,**kw):return native_call(m,entry,[x&0xffffffff for x in args],**kw)
from unicorn.m68k_const import *
cfg=json.loads(Path('outputs/Digitone-E06-PC-candidate-layout.json').read_text());payload=Path('work/os144/E06-PC-payload.bin').read_bytes();main=Path('work/os144/E06-PC-main.bin').read_bytes();PB=0x47be0000;STACK=0x47fdff00;SITE=0x40098116;PATTERN=0x47bc0000
rows={r['raw_scale']:r['pitch_classes'] for r in json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']}
def signed(v):return v-0x100000000 if v&0x80000000 else v
def oracle(base,offset,octave,word):
 fallback=base+offset+octave;raw=((word>>7)&63)-1;root=word&127
 if not word>>31 or word&0x7fff8000 or raw not in range(35) or not 0<=base<128 or not -128<=offset<=127:return fallback
 pcs=rows[raw];anchor=min((n for n in range(128) if (n-root)%12 in pcs),key=lambda n:(abs(n-base),n));pc=(anchor-root)%12;rank=pcs.index(pc)+offset;cycles,index=divmod(rank,len(pcs));result=anchor-pc+12*cycles+pcs[index]+octave
 return result if 0<=result<256 else -1
m=Machine(ddr=0x08000000)
for a in [0x40000400,PB,0x47bccf04,STACK,PATTERN]:m.ensure(a)
for a in range(0x40000000,0x40000400+len(main),0x1000):m.ensure(a)
for a in range(PB,PB+len(payload),0x1000):m.ensure(a)
m.uc.mem_write(0x40000400,main);m.uc.mem_write(PB,payload);u=m.uc
u32=lambda n:struct.pack('>I',n&0xffffffff)
for r in cfg['regions']:
 code=main[r['base']-0x40000400:r['base']-0x40000400+r['bytes']] if r['base']<PB else payload[r['base']-PB:r['base']-PB+r['bytes']];p=0
 while p<len(code):
  i=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),r['base']+p);assert i.length>0 and p+i.length<=len(code) and not i.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big')),(r['name'],hex(r['base']+p),i)
  p+=i.length
 m.install_isa_patches_scoped(code,r['base'])
count=0;examples=[]
for raw in range(35):
 for root in [0,2,11,60,62,127]:
  word=0x80000000|root|((raw+1)<<7)
  for base in range(128):
   for offset in [-24,-8,-7,-1,0,1,7,8,24]:
    octave=12 if base%2 else 0;want=oracle(base,offset,octave,word);got=signed(call(m,cfg['degree_address'],[base+offset+octave,word,base,offset,octave],stack_top=STACK,limit=10000));assert got==want,(raw,root,base,offset,octave,got,want);count+=1
for word in [0,0x8000003c,0x800080bc,0x8000123c,0xffffffff]:
 for base in [0,60,127,128,255]:
  for offset in [-129,-128,-1,0,1,127,128]:
   got=signed(call(m,cfg['degree_address'],[base+offset,word,base,offset,0],stack_top=STACK,limit=10000));assert got==oracle(base,offset,0,word);count+=1
for root,raw in [(60,0),(62,0),(60,5),(60,17)]:
 word=0x80000000|root|((raw+1)<<7);notes=[]
 for offset in range(8):notes.append(signed(call(m,cfg['degree_address'],[root+offset,word,root,offset,0],stack_top=STACK,limit=10000)))
 examples.append({'root':root,'raw_scale':raw,'offsets':list(range(8)),'notes':notes})
assert examples[0]['notes']==[60,62,64,65,67,69,71,72] and examples[1]['notes']==[62,64,66,67,69,71,73,74]
# Actual tail insertion ABI, with a native caller frame and retained identities.
regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)];abi=[]
old=bytes.fromhex('75290116d081d082');new=main[SITE-0x40000400:SITE-0x40000400+8]
for mode in ['valid','chromatic','unready','bad_header','identity_mismatch']:
 for track in range(4):
  for offset in [-24,-7,-1,0,1,7,24]:
   for sr in [0x2010,0x231f,0x2700]:
    snapshots=[];word=0x80000080|60|(track<<13);identity=0x419c38c0+track*0x504;record=0x47be1b34+track*16
    for overlay in [False,True]:
     u.mem_write(0x47be1000,bytes(0xb74));u.mem_write(0x47be1000,u32(0x47bccf04));u.mem_write(0x47be1004,struct.pack('>IIII',0x534c4332,2,0xb70,0 if mode=='unready' else 1));u.mem_write(record,struct.pack('>IIII',identity,word if mode!='chromatic' else (0x8000003c|(track<<13)),0,0x80000000|track))
     if mode=='bad_header':u.mem_write(0x47be1004,u32(0))
     u.mem_write(PATTERN+0x116,bytes([offset&255]));u.mem_write(STACK,bytes(64));u.mem_write(STACK+40,u32(track));u.mem_write(STACK+44,u32(identity+4 if mode=='identity_mismatch' else identity));u.mem_write(SITE,new if overlay else old)
     for j,r in enumerate(regs):u.reg_write(r,0x11223000+j*0x100)
     u.reg_write(UC_M68K_REG_D0,60);u.reg_write(UC_M68K_REG_D1,12);u.reg_write(UC_M68K_REG_A1,PATTERN);u.reg_write(UC_M68K_REG_A7,STACK);u.reg_write(UC_M68K_REG_SR,sr);before=bytes(u.mem_read(0x47be1000,0xb74));u.emu_start(SITE,SITE+8,count=10000);assert u.reg_read(UC_M68K_REG_PC)==SITE+8;assert bytes(u.mem_read(0x47be1000,0xb74))==before
     values=[u.reg_read(r) for r in regs];snapshots.append(values)
    expected=oracle(60,offset,12,word) if mode=='valid' else 60+offset+12;assert signed(snapshots[1][0])==expected,(mode,track,offset,snapshots[1][0],expected)
    assert snapshots[0][1:]==snapshots[1][1:],(mode,track,offset)
    abi.append({'mode':mode,'track':track,'offset':offset,'SR':hex(sr),'result':expected,'other_registers_and_stack_match_stock':True,'metadata_unchanged':True})
u.mem_write(SITE,new);assert bytes(u.mem_read(PB,0x1000))==payload[:0x1000]
out={'PC_only':True,'passed':True,'strict_new_and_existing_regions_passed':True,'oracle_cases':count,'tail_ABI_cases':len(abi),'examples':examples,'ABI':abi,'E05_preserved':hashlib.sha256(Path('outputs/Digitone_OS1.44E05_SCALE_ARP_PC_ONLY.syx').read_bytes()).hexdigest()=='17fbe13d6b2aad9c096df7ac20fd4499a7bb0951e146fd0fd0aaeace4037e474','limits':['Tail ABI uses explicit stopped native frames and retained metadata fixtures; actual producer ordering remains the E05 contract.','Output outside unsigned-byte range cancels before stock truncation. Stock final MIDI range and transpose handling remain downstream.','Physical timing remains unverified.']}
Path('outputs/Digitone-E06-degree-contracts.json').write_text(json.dumps(out,indent=2));print('PASS',count,'degree cases,',len(abi),'native tail ABI cases; C/D major examples correct')
