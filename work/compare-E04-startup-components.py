from pathlib import Path
import json,struct,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom
base=0x40000400
stock=Path('work/os144/section-3.bin').read_bytes()
e04=Path('work/os144/emulator-E04-main.bin').read_bytes()
controls=[]
for name,copy,init in [('copy_only',True,False),('initializer_fixture',False,True),('copy_initializer',True,True)]:
 image=bytearray(stock)
 if copy:
  image.extend(e04[len(stock):])
  image[0x40000538-base:0x4000053e-base]=e04[0x40000538-base:0x4000053e-base]
 if init:image[0x400ffed0-base:0x400ffed6-base]=e04[0x400ffed0-base:0x400ffed6-base]
 path=Path('work/os144/PC_ONLY-'+name+'-main.bin');path.write_bytes(image)
 controls.append((name,'outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx',str(path)))
handoff=bootrom.load_handoff('work/os144/E04-loader-handoff.bin')
Path('outputs/Digitone-E04-inherited-cache-input.json').write_text(json.dumps({'controls':{hex(k):hex(v) for k,v in handoff['ctlregs'].items()},'boot_flags':hex(handoff['boot_flags']),'source':'saved exact E04 loader handoff','not_physical_readback':True},indent=2)+'\n')
s=Path('work/test-E04-native-startup-delay.py').read_text()
old="for name,syx,imgfile in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:"
assert old in s
s=s.replace(old,'for name,syx,imgfile in controls:')
s=s.replace("dest=Path('outputs/Digitone-E04-native-startup-delay-checks.json')","dest=Path('outputs/Digitone-E04-startup-component-controls.json')")
s=s.replace("root=Path('work/native-delay-'+name)","root=Path('work/component-control-'+name)")
s=s.replace("if name=='E04':", "if name!='stock':")
anchor="  done=0;timer=Dtims(m,channels=(1,),clear_stale=False)"
assert anchor in s
s=s.replace(anchor,"""  # Carry the loader's actual modeled cache-control values only. RAM/MMIO
  # and reset registers are still the matched direct-MAIN fixture.
  m.ctlregs.update(handoff['ctlregs'])
  row['inherited_cache_controls']={hex(k):hex(v) for k,v in m.ctlregs.items()}
  row['host_seeded_private_context']=name=='initializer_fixture'
  if name=='initializer_fixture':
   m.load(payload,0x47be0000);m.load(bytes(0xb74),0x47be1000)
   m.load(struct.pack('>5I',0x47bccf04,0x534c4332,2,0xb70,0),0x47be1000)
  done=0;timer=Dtims(m,channels=(1,),clear_stale=False)""")
s=s.replace("event={'pc':hex(pc),'estimated_instructions':done,'sr':hex(uc.reg_read(UC_M68K_REG_SR))}","event={'pc':hex(pc),'estimated_instructions':done,'sr':hex(uc.reg_read(UC_M68K_REG_SR)),'CACR':hex(m.ctlregs.get(2,0))}")
s=s.replace("0x4000055a,0x400fbd14", "0x4000055a,0x40000568,0x400fbd14")
s=s.replace("if name!='stock':assert bytes(m.uc.mem_read(0x47be0000,len(payload)))==payload", "if name!='stock':\n   assert bytes(m.uc.mem_read(0x47be0000,len(payload)))==payload\n   row['private_header_at_cold_end']=list(struct.unpack('>4I',m.uc.mem_read(0x47be1004,16)))")
exec(compile(s,'PC-only-component-controls','exec'))
