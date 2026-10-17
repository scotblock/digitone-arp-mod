"""Actual native publication, complete rejection and owner/admission checks."""
from pathlib import Path
import json,struct,sys
prefix=Path('work/test-E09A-consumer-chord-contracts.py').read_text().split('checks=[];init();')[0]
exec(compile(prefix,'E10-publisher-fixtures','exec'))
from emu import cfisa
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_D0
core=json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text())
cfg=json.loads(Path('work/os144/PC_ONLY-E10-step-publication.json').read_text())
blob=Path('work/os144/PC_ONLY-E10-step-engine.bin').read_bytes();code=Path('work/os144/PC_ONLY-E10-step-publication.bin').read_bytes();X=core['state']
ROOT=E+0x3000;DATA=KIT+0x5ce;OFFSETS=E+0x2000
for p in [ROOT,OFFSETS,0x419f0000,core['base'],X,cfg['base']]:m.ensure(p)
u.mem_write(core['base'],blob);u.mem_write(cfg['base'],code);m.install_isa_patches_scoped(code,cfg['base'])
audit={};exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0],audit)
offset=0
while offset<len(code):
 ins=cfisa.decode(lambda x:int.from_bytes(code[offset+x:offset+x+2],'big'),cfg['base']+offset)
 assert ins.length and not ins.flags&(cfisa.FPU|cfisa.LINEF|cfisa.ILLEGAL) and not audit['move_restriction'](int.from_bytes(code[offset:offset+2],'big')),(offset,ins)
 offset+=ins.length

def reset():
 init();u.mem_write(X,blob[X-core['base']:X-core['base']+64]);put(0x419f0de0,ROOT);put(ROOT+0xff8,0x40193b90);put(ROOT+0x1008,DATA)
 u.mem_write(OFFSETS,bytes([0,1,2,3,4,5,6,7]+[-1&255]*8))
 return [DATA,8,0xdb,0x80000080,OFFSETS,1]

def publish(args):return invoke(cfg['base'],args)
checks=[]
args=reset();assert publish(args)==1
assert [get(X+x) for x in [4,8,20,24,28]]==[1,8,0xdb,0x80000080,DATA]
assert bytes(u.mem_read(X+32,16))==bytes(u.mem_read(OFFSETS,16))
checks.append('Complete enable/length/rest-mask/root-scale/offset block is published natively.')
for label,index,value in [('bad length',1,0),('too long',1,17),('mask overflow',2,0x10000),('bad flag',5,2),('invalid root',3,0x8000008c),('invalid scale',3,0x80001200),('missing valid bit',3,0x80),('reserved word bits',3,0x80002080),('stale UI owner',0,DATA+0xa4),('bad source span',4,0x47fffff1)]:
 args=reset();args[index]=value;before=bytes(u.mem_read(X,64));assert publish(args)==0 and bytes(u.mem_read(X,64))==before,label
 checks.append(label+' rejected without mutation')
for value in [-25,25]:
 args=reset();u.mem_write(OFFSETS+15,bytes([value&255]));before=bytes(u.mem_read(X,64));assert publish(args)==0 and bytes(u.mem_read(X,64))==before
checks.append('Last offset is validated before any field changes; both signed bounds are checked.')
args=reset();put(S+8,1);put(S+336,DATA);put(X+28,DATA);assert publish(args)==1
checks.append('A live edit to the same consumed owner is admitted.')
args=reset();put(S+8,1);put(S+336,DATA+0xa4);put(X+28,DATA+0xa4);before=bytes(u.mem_read(X,64));assert publish(args)==0 and bytes(u.mem_read(X,64))==before
checks.append('UI selection cannot replace the sequence belonging to another active pattern.')
args=reset();put(X+12,15);put(X+16,15);args[1]=3;assert publish(args)==1 and get(X+12)==0 and get(X+16)==2
checks.append('Shortening length bounds both playback and editor cursors.')
args=reset();put(0x47be2840,0x434f4c44);before=bytes(u.mem_read(X,64));assert publish(args)==0 and bytes(u.mem_read(X,64))==before
checks.append('COLD admission rejects settings publication.')
for sr in [0x201f,0x2310,0x2700]:
 args=reset();u.mem_write(STACK,struct.pack('>I',0xdeadbee0)+b''.join(struct.pack('>I',x) for x in args))
 u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,STACK);u.emu_start(cfg['base'],0xdeadbee0,count=50000)
 assert u.reg_read(UC_M68K_REG_D0)==1 and u.reg_read(UC_M68K_REG_SR)==sr
checks.append('Original interrupt level and condition flags are restored.')
out={'passed':True,'PC_only':True,'strict_ColdFire_decode_and_MOVE_checked':True,'checks':checks,'groups':len(checks),'limits':cfg['limits']+['Native UI binding, settings and playback state are explicit isolated fixtures.']}
Path('outputs/Digitone-E10-PC-step-publication.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
