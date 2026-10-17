from pathlib import Path
exec(Path('work/audit-E02-startup-failure.py').read_text().split('\ntry:\n for mode')[0])
stock=Path('work/os144/section-3.bin').read_bytes()
base=0x419f20a0;end=0x429f20a0
r={'PC_only':True,'scope':'Stock 1.44 heap configuration and captured-state allocator calls, intact allocator metadata','initial_globals':{hex(a):hex(struct.unpack_from('>I',stock,a-0x40000400)[0]) for a in range(0x40240058,0x40240074,4)},'cases':[],'failure':None}
try:
 for size in [16,64,4096,0x100000,0x1000000,0x1000001,0x2000000]:
  m=machine();ret=call(m,0x400e9444,[size],stack_top=STACK,limit=500000)
  returned=m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
  assert returned and (ret==0 or base<=ret<end)
  r['cases'].append({'request_bytes':size,'returned':returned,'result':hex(ret),'inside_heap_or_null':True})
 r['passed']=True
except BaseException:
 import traceback;r['passed']=False;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44-heap-bounds-checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
