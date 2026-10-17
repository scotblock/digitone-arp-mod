from pathlib import Path
import json
s=Path('work/test-E04-native-startup-delay.py').read_text()
old="for name,syx,imgfile in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:"
assert old in s
cases=[]
for state,card in [('factory','work/os144-emulator-E02-engine/plusdrive.img'),('saved_stock','work/user-session-audio/stock/plusdrive.img')]:
 for mode,syx,image in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:
  cases.append((state+'_'+mode,syx,image,card))
s=s.replace(old,'for name,syx,imgfile,cardfile in '+repr(cases)+':')
s=s.replace("name=='E04'","name.endswith('E04')")
s=s.replace("root=Path('work/native-delay-'+name)","root=Path('work/source-startup-'+name)")
s=s.replace("dest=Path('outputs/Digitone-E04-native-startup-delay-checks.json')","dest=Path('outputs/Digitone-E04-source-startup-checks.json')")
s=s.replace("  root=Path(","  source=Path(cardfile)\n  row['card_source']=cardfile\n  root=Path(",1)
s=s.replace("from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A7,UC_M68K_REG_SR","from unicorn.m68k_const import *")
addition=r'''  row['source_writes']=[];row['source_last_writes']={};row['source_write_counts']={};row['pattern_pointer_writes']=[];row['producer_entries']=[];row['captures']=[];row['startup_order']=[]
  watched_fields={base+t*0x3d0+off for base in [0x407fd414,0x40813531] for t in range(4) for off in [0x3cb,0x3ce]}
  def install_source_watch(mm,stage):
   def read(address,size):
    try:return bytes(mm.uc.mem_read(address,size)).hex()
    except Exception:return None
   def fieldwrite(uc,access,address,size,value,data):
    end=address+size
    fields=[f for f in watched_fields if address<=f<end]
    if not fields:return
    event={'stage':stage,'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(address),'size':size,'value':hex(value),'estimated_instructions':done}
    for f in fields:
     key=hex(f);row['source_last_writes'][key]=event;row['source_write_counts'][key]=row['source_write_counts'].get(key,0)+1
    if len(row['source_writes'])<200:row['source_writes'].append(event)
   for base in [0x407fd414,0x40813531]:
    for t in range(4):
     lo=base+t*0x3d0+0x3c8;mm.uc.hook_add(UC_HOOK_MEM_WRITE,fieldwrite,begin=lo,end=lo+7)
   def ptrwrite(uc,access,address,size,value,data):
    if len(row['pattern_pointer_writes'])<200:row['pattern_pointer_writes'].append({'stage':stage,'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(address),'size':size,'value':hex(value),'estimated_instructions':done})
   mm.uc.hook_add(UC_HOOK_MEM_WRITE,ptrwrite,begin=0x4138f210,end=0x4138f223)
   def phase(uc,pc,size,data):row['startup_order'].append({'stage':stage,'pc':hex(pc),'estimated_instructions':done})
   for pc in [0x400ffed0,0x40091b0c]:mm.uc.hook_add(UC_HOOK_CODE,phase,begin=pc,end=pc)
   def producer(uc,pc,size,data):
    sp=uc.reg_read(UC_M68K_REG_A7)
    words=[int.from_bytes(uc.mem_read(sp+i*4,4),'big') for i in range(7)]
    if len(row['producer_entries'])<100:row['producer_entries'].append({'stage':stage,'pc':hex(pc),'return':hex(words[0]),'args':[hex(x) for x in words[1:]],'estimated_instructions':done,'current_pointer':read(0x4138f214,4)})
   mm.uc.hook_add(UC_HOOK_CODE,producer,begin=0x4009451e,end=0x4009451e)
   def capture(uc,pc,size,data):
    source=uc.reg_read(UC_M68K_REG_A3);track=uc.reg_read(UC_M68K_REG_D4)
    fields={}
    for t in range(4):
     for label,off in [('root',0x3cb),('scale',0x3ce)]:
      addr=source+t*0x3d0+off;fields[str(t)+'_'+label]={'address':hex(addr),'byte':read(addr,1),'last_guest_writer':row['source_last_writes'].get(hex(addr))}
    row['captures'].append({'stage':stage,'pc':hex(pc),'estimated_instructions':done,'source':hex(source),'track':track,'event':hex(uc.reg_read(UC_M68K_REG_A2)),'current_pointer':read(0x4138f214,4),'source_fields':fields,'source_tail':read(source+0x16111,3),'private_ready':read(0x47be1010,4) if name.endswith('E04') else None})
   mm.uc.hook_add(UC_HOOK_CODE,capture,begin=0x400947ec,end=0x400947ec)
  install_source_watch(m,'cold')
'''
anchor='  done=0;timer=Dtims(m,channels=(1,),clear_stale=False)'
assert anchor in s;s=s.replace(anchor,addition+anchor)
s=s.replace("   held['ev']=ev","   held['ev']=ev\n   install_source_watch(mm,'intro')")
exec(compile(s,'E04-source-startup','exec'))
