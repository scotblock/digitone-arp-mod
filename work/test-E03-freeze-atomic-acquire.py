from pathlib import Path
exec(Path('work/validate-E03-continuous-queue-action.py').read_text().split('\ntry:\n for name')[0])
A=0x47f41000
# Diagnostic scratch code only: preserve D2/D3, mask IRQs, snapshot gate, call existing setter(0), restore.
code=bytes.fromhex('2f022f0340c246fc27002639419950a442a74eb9400eb524588f200346c2261f241f4e75')
r={'PC_only':True,'cases':[],'code_hex':code.hex(),'code_bytes':len(code),'firmware_patch_installed':False,'limits':['Scratch instruction sequence is not placed in a firmware image or certified owned executable region.','Masks CPU interrupts for acquisition; it does not stop DMA or certify that no producer had already passed the gate.','Lease/storage ownership and USB queue cleanup remain outside this isolated test.']}
for gate in [0,1]:
 for sr in [0x2000,0x2300,0x2700]:
  m=make();m.ensure(A);m.uc.mem_write(A,code);call(m,0x400eb524,[gate],stack_top=STACK,limit=1000)
  m.uc.mem_write(STACK,u32(0xdeadbee0));m.uc.reg_write(UC_M68K_REG_SR,sr);m.uc.reg_write(UC_M68K_REG_A7,STACK);m.uc.reg_write(UC_M68K_REG_D2,0x12345678);m.uc.reg_write(UC_M68K_REG_D3,0x98765432)
  m.uc.emu_start(A,A+10,count=1000);assert (m.uc.reg_read(UC_M68K_REG_SR)&0x2700)==0x2700
  m.uc.emu_start(A+10,0xdeadbee0,count=1000)
  assert m.uc.reg_read(UC_M68K_REG_D0)==gate and int.from_bytes(m.uc.mem_read(0x419950a4,4),'big')==0
  assert (m.uc.reg_read(UC_M68K_REG_SR)&0x2700)==sr and m.uc.reg_read(UC_M68K_REG_D2)==0x12345678 and m.uc.reg_read(UC_M68K_REG_D3)==0x98765432
  r['cases'].append({'initial_gate':gate,'initial_SR':hex(sr),'acquire_interrupt_mask':7,'final_gate':0,'caller_interrupt_level_restored':True,'saved_gate_returned':True,'saved_registers_preserved':True})
r['passed']=True
Path('outputs/Digitone-OS1.44E03-freeze-atomic-acquire-checks.json').write_text(json.dumps(r,indent=2));print('PASS atomic acquire',len(r['cases']),len(code))
