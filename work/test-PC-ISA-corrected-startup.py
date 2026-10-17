from pathlib import Path
import json
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
s=Path('work/test-E04-native-startup-delay.py').read_text()
old="for name,syx,imgfile in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:"
assert old in s
cases=[]
for name,card in [('E04_default','work/os144-emulator-E02-engine/plusdrive.img'),('E04_restored','work/os144/PC_ONLY-saved-mirror-valid_first.img'),('E04_bad_pointer','work/os144-emulator-E02-engine/plusdrive.img'),('E04_post_stock_bad_magic','work/os144/PC_ONLY-saved-mirror-valid_first.img')]:
 cases.append((name,'outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/PC_ONLY-E04-ISA-corrected-main.bin',card))
s=s.replace(old,'for name,syx,imgfile,cardfile in '+repr(cases)+':')
s=s.replace("name=='E04'","name.startswith('E04')")
s=s.replace("root=Path('work/native-delay-'+name)","root=Path('work/ISA-corrected-startup-'+name)")
s=s.replace('Digitone-E04-native-startup-delay-checks.json','Digitone-E04-PC-ISA-startup-checks.json')
s=s.replace("work/os144/fallback-final-payload.bin","work/os144/PC_ONLY-E04-ISA-corrected-payload.bin")
s=s.replace("  root=Path(","  source=Path(cardfile)\n  row['card_source']=cardfile\n  root=Path(",1)
anchor='  done=0;timer=Dtims(m,channels=(1,),clear_stale=False)'
addition=r'''  row['strict_instruction_checks']={};row['strict_failures']=[];row['initializer_calls']=[];row['restore_events']=[];row['capture_inputs']=[]
  def install_strict(mm,stage):
   def strict(uc,pc,size,data):
    ins=cfisa.decode(lambda off:int.from_bytes(uc.mem_read(pc+off,2),'big'),pc)
    bad=move_restriction(int.from_bytes(uc.mem_read(pc,2),'big'))
    if bad or ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) or (ins.flags&cfisa.PRIV and not uc.reg_read(UC_M68K_REG_SR)&0x2000):
     row['strict_failures'].append({'pc':hex(pc),'op':ins.op,'reason':bad,'stage':stage});raise AssertionError(row['strict_failures'][-1])
    key=stage+':'+ins.op;row['strict_instruction_checks'][key]=row['strict_instruction_checks'].get(key,0)+1
   for lo,hi in [(0x4029c4b0,0x4029c51d),(0x47be0000,0x47be06f7),(0x47be08a4,0x47be09bb)]:mm.uc.hook_add(UC_HOOK_CODE,strict,begin=lo,end=hi)
   def entering(uc,pc,size,data):
    if name=='E04_bad_pointer':uc.mem_write(0x47be1000,struct.pack('>I',0xffffffff))
   mm.uc.hook_add(UC_HOOK_CODE,entering,begin=0x47be08a4,end=0x47be08a4)
   def stock(uc,pc,size,data):
    sp=uc.reg_read(UC_M68K_REG_A7);row['initializer_calls'].append({'stage':stage,'argument':int.from_bytes(uc.mem_read(sp+4,4),'big'),'sr':hex(uc.reg_read(UC_M68K_REG_SR))})
    if name=='E04_post_stock_bad_magic':uc.mem_write(0x47be1004,bytes(4))
   mm.uc.hook_add(UC_HOOK_CODE,stock,begin=0x47be0642,end=0x47be0642)
   def restore(uc,pc,size,data):row['restore_events'].append({'pc':hex(pc),'d0':hex(uc.reg_read(UC_M68K_REG_D0)),'d2':hex(uc.reg_read(UC_M68K_REG_D2))})
   for pc in [0x400a838c,0x400a8402,0x400a83f4,0x400a8410]:mm.uc.hook_add(UC_HOOK_CODE,restore,begin=pc,end=pc)
   def capture(uc,pc,size,data):
    from unicorn.m68k_const import UC_M68K_REG_A3,UC_M68K_REG_D4
    source=uc.reg_read(UC_M68K_REG_A3);track=uc.reg_read(UC_M68K_REG_D4)
    row['capture_inputs'].append({'stage':stage,'source':hex(source),'track':track,'root':bytes(uc.mem_read(source+track*0x3d0+0x3cb,1)).hex(),'scale':bytes(uc.mem_read(source+track*0x3d0+0x3ce,1)).hex()})
   mm.uc.hook_add(UC_HOOK_CODE,capture,begin=0x400947ec,end=0x400947ec)
  install_strict(m,'cold')
'''
assert anchor in s;s=s.replace(anchor,addition+anchor)
s=s.replace("   held['ev']=ev","   held['ev']=ev\n   install_strict(mm,'intro')")
s=s.replace("  save(m,paths.cold,", "  row['private_after_cold']=bytes(m.uc.mem_read(0x47be1000,32)).hex()\n  row['candidate_after_cold']=bytes(m.uc.mem_read(0x47be1a24,16)).hex()\n  save(m,paths.cold,")
s=s.replace("  row['passed']=True", "  assert not row['strict_failures'] and len(row['initializer_calls'])==1\n  assert row['initializer_calls'][0]['argument']==158\n  disabled=name in ['E04_bad_pointer','E04_post_stock_bad_magic']\n  assert row['private_after_cold'][:8]==('00000000' if disabled else '47bccf04')\n  assert row['private_after_cold'][32:40]==('00000000' if disabled else '00000001')\n  row['passed']=True")
exec(compile(s,'PC-ISA-corrected-startup','exec'))
