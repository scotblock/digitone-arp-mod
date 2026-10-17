from pathlib import Path
exec(Path('work/audit-E02-startup-failure.py').read_text().split('\ntry:\n for mode')[0])
from unicorn import UC_HOOK_CODE
class Asm:
 def __init__(self):self.code=bytearray();self.labels={};self.fix=[]
 def emit(self,s):self.code.extend(bytes.fromhex(s))
 def label(self,s):self.labels[s]=len(self.code)
 def branch(self,op,label):p=len(self.code);self.emit(op+'0000');self.fix.append((p,label))
 def done(self):
  for p,label in self.fix:self.code[p+2:p+4]=(self.labels[label]-p-2).to_bytes(2,'big',signed=True)
  return bytes(self.code)
ENTRY=0x47f40000;TRAMP=0x47be0642;EXPECTED=BSS-0x14100
a=Asm();a.emit('4fefffc048d77fff40c03f40003c46fc2700426f003e')
a.emit('202f00440c800000009e');a.branch('6600','disable')
a.emit('203947be10000c80'+u32(EXPECTED).hex());a.branch('6600','disable')
for address,value in [(BSS,0x534c4332),(BSS+4,2),(BSS+8,0xb70)]:
 a.emit('2039'+u32(address).hex()+'0c80'+u32(value).hex());a.branch('6600','disable')
a.emit('3f7c0001003e42b947be10102f3c00000b6042a7487947be10144eb9400fbb204fef000c');a.branch('6000','stock')
a.label('disable');a.emit('42b947be1000')
a.label('stock');a.emit('302f003c46c02f2f00444eb9'+u32(TRAMP).hex()+'588f2f40000046fc27004a6f003e');a.branch('6700','return')
a.emit('203947be10000c80'+u32(EXPECTED).hex());a.branch('6600','disable_after')
for address,value in [(BSS,0x534c4332),(BSS+4,2),(BSS+8,0xb70)]:
 a.emit('2039'+u32(address).hex()+'0c80'+u32(value).hex());a.branch('6600','disable_after')
a.emit('23fc0000000147be1010');a.branch('6000','return')
a.label('disable_after');a.emit('42b947be1000')
a.label('return');a.emit('302f003c46c04cd77fff4fef00404e75');code=a.done()
out={'PC_only':True,'prototype_address':hex(ENTRY),'bytes':len(code),'replaces_firmware':False,'cases':[],'failure':None,'limits':['Scratch machine-code prototype, not placed in the helper image or firmware. Captured stock state; no timers/IRQ/DMA concurrency.','Code-copy corruption, bus exceptions and non-returning stock initializer are not recovered by this design. Pointer disable presumes ownership of its fixed RAM word, still under audit.']}
try:
 for mode in ['valid','unready','bad_magic','bad_version','bad_size','null_pointer','out_of_region_pointer','misaligned_pointer','bad_argument','pointer_changes_during_stock','header_changes_during_stock']:
  for sr in [0x2000,0x2300,0x2700]:
   m=machine();uc=m.uc;m.load(code,ENTRY);m.install_isa_patches_scoped(code,ENTRY);uc.mem_write(BSS+12,u32(0 if mode=='unready' else 1));before=bytes(uc.mem_read(BSS,0xb70));arg=157 if mode=='bad_argument' else 158
   if mode.startswith('bad_') and mode!='bad_argument':uc.mem_write(BSS+{'bad_magic':0,'bad_version':4,'bad_size':8}[mode],u32(0))
   if mode in ['null_pointer','out_of_region_pointer','misaligned_pointer']:uc.mem_write(PTR,u32({'null_pointer':0,'out_of_region_pointer':0xffffffff,'misaligned_pointer':EXPECTED+1}[mode]))
   before=bytes(uc.mem_read(BSS,0xb70));stock_calls=[]
   def entered(uc,pc,n,d):
    stock_calls.append({'sr_IPL':(uc.reg_read(UC_M68K_REG_SR)>>8)&7})
    if mode=='pointer_changes_during_stock':uc.mem_write(PTR,u32(0xffffffff))
    if mode=='header_changes_during_stock':uc.mem_write(BSS,u32(0))
   uc.hook_add(UC_HOOK_CODE,entered,begin=TRAMP,end=TRAMP)
   uc.mem_write(STACK,u32(0xdeadbee0)+u32(arg));uc.reg_write(UC_M68K_REG_SR,sr);uc.reg_write(UC_M68K_REG_A7,STACK)
   preserved={reg:uc.reg_read(reg) for reg in [UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]}
   uc.emu_start(ENTRY,0xdeadbee0,count=400000);assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and uc.reg_read(UC_M68K_REG_A7)==STACK+4
   assert len(stock_calls)==1 and stock_calls[0]['sr_IPL']==(sr>>8)&7 and uc.reg_read(UC_M68K_REG_SR)&0x2700==sr
   assert all(uc.reg_read(reg)==value for reg,value in preserved.items())
   valid=mode in ['valid','unready'];assert int.from_bytes(uc.mem_read(PTR,4),'big')==(EXPECTED if valid else 0)
   if valid:assert bytes(uc.mem_read(BSS+12,0xb70-12))==u32(1)+bytes(0xb70-16)
   elif mode not in ['pointer_changes_during_stock','header_changes_during_stock']:assert bytes(uc.mem_read(BSS,0xb70))==before
   # Compare the actual initializer's pool writes/return against its stock trampoline on the same capture.
   control=machine();ret=call(control,TRAMP,[arg],stack_top=STACK,limit=400000)
   assert uc.reg_read(UC_M68K_REG_D0)==ret and bytes(uc.mem_read(0x419ebe2c,158*72+128))==bytes(control.uc.mem_read(0x419ebe2c,158*72+128))
   out['cases'].append({'mode':mode,'incoming_IPL':(sr>>8)&7,'returned':True,'stock_pool_and_return_match':True,'context_ready':valid})
  print('PASS fallback',mode,flush=True)
 out['passed']=True
except BaseException:
 import traceback;out['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(out['failure'],flush=True)
Path('outputs/Digitone-OS1.44-startup-fallback-design-checks.json').write_text(json.dumps(out,indent=2))
if out['failure']:raise SystemExit(1)
