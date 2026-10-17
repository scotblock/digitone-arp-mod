from pathlib import Path
import json
s=Path('work/test-E04-native-startup-delay.py').read_text()
old="for name,syx,imgfile in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:"
assert old in s
s=s.replace(old,"for name,syx,imgfile in [('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:")
s=s.replace("root=Path('work/native-delay-'+name)","root=Path('work/pre-logo-hooks-'+name)")
s=s.replace("dest=Path('outputs/Digitone-E04-native-startup-delay-checks.json')","dest=Path('outputs/Digitone-E04-pre-logo-hook-checks.json')")
anchor="  done=0;timer=Dtims(m,channels=(1,),clear_stale=False)"
addition="""  row['hook_counts']={};row['first_hook_entries']=[];row['intro_exit_seen']=False
  def install_hook_watch(mm,stage):
   port=json.loads(Path('work/os144/helper-port.json').read_text())
   watched={k:v['address'] for k,v in port['layout'].items()}
   watched['startup_fallback']=0x47be08a4
   def hit(uc,pc,size,data,label):
    phase='after_intro_exit' if row['intro_exit_seen'] else 'before_intro_exit'
    key=stage+':'+phase+':'+label;row['hook_counts'][key]=row['hook_counts'].get(key,0)+1
    if row['hook_counts'][key]<=2:
     sp=uc.reg_read(UC_M68K_REG_A7)
     row['first_hook_entries'].append({'name':label,'stage':stage,'phase':phase,'pc':hex(pc),'caller':bytes(uc.mem_read(sp,4)).hex(),'sr':hex(uc.reg_read(UC_M68K_REG_SR)),'pointer':bytes(uc.mem_read(0x47be1000,4)).hex(),'ready':int.from_bytes(uc.mem_read(0x47be1010,4),'big')})
   for label,address in watched.items():mm.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,size,data,label=label:hit(uc,pc,size,data,label),begin=address,end=address)
   mm.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,size,data:row.__setitem__('intro_exit_seen',True),begin=0x40091b0c,end=0x40091b0c)
  install_hook_watch(m,'cold')
"""
assert anchor in s;s=s.replace(anchor,addition+anchor)
s=s.replace("   held['ev']=ev","   held['ev']=ev\n   install_hook_watch(mm,'intro')")
exec(compile(s,'E04-pre-logo-hook-attribution','exec'))
