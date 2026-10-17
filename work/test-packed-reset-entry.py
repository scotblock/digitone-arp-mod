"""Direct initializer-entry equivalence; no outer shutdown/startup claim."""
import pathlib,struct,json
exec(pathlib.Path('work/cache-context-environment.py').read_text())
from emu.harness import call
info=json.loads(pathlib.Path('work/packed-context-build.json').read_text())
images=[pathlib.Path('work/cache-context-overlay.bin').read_bytes(),pathlib.Path('work/packed-context-overlay.bin').read_bytes()]
entries=[0x47be0666,info['layout']['reset']['address']]
loops=[0x47be0752,info['instruction_map'][str(0x47be0752)]]
cases=[]
for mode in ['ready','not_ready','magic','version','size','null_pointer','bad_argument']:
 results=[]
 for idx,image in enumerate(images):
  def installed(s):
   s.m.uc.mem_write(RAM,image)
   s.m.install_isa_patches_scoped(image[:info['code_bytes'] if idx else 1892],RAM)
   if not idx:s.m.install_isa_patches_scoped(image[2368:],RAM+2368)
  s=Session('work/cache-fresh-trace-prepared.snap',syx=str(SYX),ddr=DDR,hle=False,on_machine=installed)
  try:
   uc=s.m.uc;stack=0x47fdff00;s.m.ensure(stack)
   uc.mem_write(BSS+16,bytes([0xa5])*(0xb70-16))
   if mode=='not_ready':uc.mem_write(BSS+12,u32(0))
   if mode in ['magic','version','size']:uc.mem_write(BSS+['magic','version','size'].index(mode)*4,u32(0))
   if mode=='null_pointer':uc.mem_write(PTR,u32(0))
   before=bytes(uc.mem_read(PTR,0xb74));uc.reg_write(UC_M68K_REG_SR,0x2700)
   args=[157 if mode=='bad_argument' else 158]
   if mode in ['ready','not_ready']:
    call(s.m,entries[idx],args,stack_top=stack,limit=300000)
    assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
    assert list(struct.unpack('>IIII',uc.mem_read(BSS,16)))==[0x534c4332,2,0xb70,1]
    assert bytes(uc.mem_read(BSS+16,0xb70-16))==bytes(0xb70-16)
   else:
    uc.mem_write(stack,u32(0xdeadbee0)+u32(args[0]));uc.reg_write(UC_M68K_REG_A7,stack)
    uc.emu_start(entries[idx],loops[idx],count=300000)
    assert uc.reg_read(UC_M68K_REG_PC)==loops[idx]
    assert bytes(uc.mem_read(PTR,0xb74))==before
   regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]
   values=[uc.reg_read(r) for r in regs]
   uc.mem_write(stack-0x200,bytes.fromhex('40c7'));uc.emu_start(stack-0x200,stack-0x1fe,count=1)
   sr=uc.reg_read(UC_M68K_REG_D7)&0xffff
   # Internal failure-loop stack includes relocated call return literals.
   if mode not in ['ready','not_ready']:
    for j,v in enumerate(values):
     if idx==0 and str(v) in info['instruction_map']:values[j]=info['instruction_map'][str(v)]
   assert bytes(uc.mem_read(RAM,len(image)))==image
   results.append((values,sr,bytes(uc.mem_read(PTR,0xb74)),bytes(uc.mem_read(0x4199d590,0x2914))))
  finally:s.close()
 assert results[0]==results[1],mode
 cases.append({'mode':mode,'match':True,'returned_ready':mode in ['ready','not_ready'],'failure_loop_without_context_mutation':mode not in ['ready','not_ready']})
out={'passed':True,'firmware_modified':False,'cases':cases,'limits':['Direct entry invocation on a prepared stopped PC guest; not an executed loader/bootstrap integration.','The inherited initializer hook is not retargeted by this test.','No concurrent producers, scheduler quiescence, physical cache or device-state proof.']}
pathlib.Path('outputs/Digitone-packed-context-reset-entry.json').write_text(json.dumps(out,indent=2));print('PASS',len(cases),'direct reset-entry cases')
