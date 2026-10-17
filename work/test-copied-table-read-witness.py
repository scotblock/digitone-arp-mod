"""Observe actual lookup loads from the startup-created snapshot, no reinjection."""
import pathlib
text=pathlib.Path('work/test-native-arp-overlays.py').read_text()
prefix='\n'.join(x for x in text.split('def run(mode):')[0].splitlines() if not x.startswith('subprocess.run('))
exec(prefix)
from unicorn import UC_HOOK_MEM_READ
blob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes();TABLE=RAM+1904
paths=ExperimentalPaths(str(pathlib.Path('work/fast-table-cold-emulator').resolve()),SYX.name,paths.devices_dir);os.environ.update(paths.env())
OUT=pathlib.Path('outputs/Digitone-copied-table-read-witness.json')
body=text[text.index('def run(mode):'):text.index('\ntry:\n if os.environ')]
body=body.replace("uc.mem_write(RAM,blob);uc.mem_write(PTR,bytes(0xb74))\n   uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))","assert bytes(uc.mem_read(RAM,len(blob)))==blob and rd(uc,BSS+12)==1")
body=body.replace("original==stock[pc-base:pc-base+length]","original==bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((length-6)//2)")
body=body.replace("uc.mem_write(pc,bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((length-6)//2))","# Startup hooks are restored, never reinstalled.")
body=body.replace('m.install_isa_patches_scoped(blob,RAM)','m.install_isa_patches_scoped(blob[:1892],RAM)')
body=body.replace("  m=session.m;uc=m.uc;m.ensure(RAM)","""  m=session.m;uc=m.uc;m.ensure(RAM)
  result['table_reads']=[];result['table_before_sha256']=hashlib.sha256(bytes(uc.mem_read(TABLE,420))).hexdigest()
  def table_read(uc,access,address,n,value,d):
   item={'ms':session.now_ms(),'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(address),'size':n,'value':bytes(uc.mem_read(address,n)).hex(),'controls':{hex(k):hex(v) for k,v in m.ctlregs.items()}}
   assert layout['quantize']['address']<=uc.reg_read(UC_M68K_REG_PC)<layout['quantize']['address']+178,item
   assert n==1 and bytes(uc.mem_read(address,n))==blob[address-RAM:address-RAM+n]
   result['table_reads'].append(item)
  uc.hook_add(UC_HOOK_MEM_READ,table_read,begin=TABLE,end=TABLE+419)
""")
exec(compile(body,'copied-table-read-witness','exec'));run('scale-fixture')
q=report['runs'][0];assert q['halted'] is None and all(q['checks'].values()) and q['table_reads']
assert len(q['table_reads'])==len(q['quantize_calls'])
report['firmware_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();assert report['firmware_before']==report['firmware_after']
report['passed']=True;persist();print('PASS actual table loads',len(q['table_reads']),'ms',q['ms'],flush=True)
