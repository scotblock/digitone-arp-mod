"""Full existing OS-entry test with the optimized image and table observations."""
import pathlib
source=pathlib.Path('work/test-native-cold-arp.py').read_text()
source=source.replace("exec(source.split('def run(mode):')[0])", "source='\\n'.join(x for x in source.splitlines() if not x.startswith('subprocess.run('))\nexec(source.split('def run(mode):')[0])\nfrom unicorn import UC_HOOK_MEM_READ\nblob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()\nTABLE=RAM+1904\nTABLE_END=TABLE+420\nTABLE_BYTES=blob[1904:2324]\nassert len(blob)==2324")
source=source.replace('work/native-cold-arp-emulator','work/fast-table-cold-emulator')
source=source.replace('outputs/Digitone-native-cold-arp-results.json','outputs/Digitone-fast-table-cold-startup.json')
source=source.replace('m.install_isa_patches_scoped(blob,RAM)','m.install_isa_patches_scoped(blob[:1892],RAM)')
needle=" rec['initial_ready']=hex(rd(uc,BSS+12))"
extra="""
 rec['table_copy_writes']=[];rec['cache_handoff']=[];rec['table_reads']=[]
 rec['table_intact_on_stage_entry']=bytes(uc.mem_read(TABLE,420))==TABLE_BYTES
 def table_write(uc,access,address,n,value,d):
  physical=0x40000000+(address-0x40000000)%DDR
  if TABLE<=physical<TABLE_END:
   item={'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(address),'physical':hex(physical),'size':n,'value':hex(value)}
   rec['table_copy_writes'].append(item)
   assert stage=='ladder' and STAGE<=uc.reg_read(UC_M68K_REG_PC)<STAGE+len(boot),item
 def table_read(uc,access,address,n,value,d):
  if len(rec['table_reads'])<100:
   rec['table_reads'].append({'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(address),'size':n,'cache_controls':{hex(k):hex(v) for k,v in m.ctlregs.items()}})
 for k in range(8):uc.hook_add(UC_HOOK_MEM_WRITE,table_write,begin=TABLE+k*DDR,end=TABLE_END-1+k*DDR)
 uc.hook_add(UC_HOOK_MEM_READ,table_read,begin=TABLE,end=TABLE_END-1)
 def cache_checkpoint(uc,pc,n,d):
  item={'pc':hex(pc),'d0':hex(uc.reg_read(UC_M68K_REG_D0)),'table_intact':bytes(uc.mem_read(TABLE,420))==TABLE_BYTES,'controls_before':{hex(k):hex(v) for k,v in m.ctlregs.items()}}
  rec['cache_handoff'].append(item)
  assert item['table_intact'],item
  if pc==0x40000568:
   assert m.ctlregs.get(2)==0xa50ce100 and m.ctlregs.get(4)==0x4007e020,item
 for pc in [0x4000053e,0x40000554,0x4000055a,0x40000564,0x40000568]:uc.hook_add(UC_HOOK_CODE,cache_checkpoint,begin=pc,end=pc)
 def first_resident(uc,pc,n,d):
  if 'first_resident_execution' not in rec:
   rec['first_resident_execution']={'pc':hex(pc),'table_intact':bytes(uc.mem_read(TABLE,420))==TABLE_BYTES,'controls':{hex(k):hex(v) for k,v in m.ctlregs.items()}}
   assert m.ctlregs.get(2)==0xa50ce100 and m.ctlregs.get(4)==0x4007e020
 uc.hook_add(UC_HOOK_CODE,first_resident,begin=RAM,end=RAM+1891)
"""
source=source.replace(needle,needle+extra)
source=source.replace("  assert rec['code_intact']", "  rec['table_intact']=bytes(uc.mem_read(TABLE,420))==TABLE_BYTES\n  assert rec['table_intact']\n  assert rec['code_intact']")
source=source.replace(" report['passed']=True", " assert len(report['startup']['stages'][0]['table_copy_writes'])==105\n report['lookup_table']={'address':hex(TABLE),'bytes':420,'copy_longs':105,'sha256':hashlib.sha256(TABLE_BYTES).hexdigest(),'overlay_bytes':len(blob),'overlay_copy_longs':len(blob)//4}\n report['passed']=True")
exec(compile(source,'fast-table-cold-startup','exec'))
