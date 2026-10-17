"""Read-only executable space screening; no blank-run ownership claims."""
exec(open('work/disassemble.py').read().split('out=[]')[0])
import hashlib,json
md.skipdata=True
windows={}
for lo,hi in [(0x4000045c,0x400004b2),(0x400004b2,0x400004e8),(0x4000053e,0x40000568)]:
 windows[hex(lo)]=[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)]
# Only padding before the known initialized-data boundary is inventoried.
runs=[]
for value in (0,255):
 start=None
 for k,x in enumerate(b[:0x40242000-base]):
  if x==value and start is None:start=k
  if x!=value and start is not None:
   if k-start>=64:runs.append({'start':hex(base+start),'end_exclusive':hex(base+k),'length':k-start,'byte':value,'ownership':'unproven'})
   start=None
 if start is not None and k+1-start>=64:runs.append({'start':hex(base+start),'end_exclusive':hex(base+k+1),'length':k+1-start,'byte':value,'ownership':'unproven'})
result={'image_sha256':hashlib.sha256(b).hexdigest(),'image_start':hex(base),'image_end_exclusive':hex(base+len(b)),'initialized_data_source_start':'0x40242000','initialized_data_source_split':'0x402478f0','startup_clear_range':['0x40242000','0x431dc690'],'append_at_current_end_erased_at_startup':0x40242000<=base+len(b)<0x431dc690,'startup_disassembly':windows,'padding_runs':sorted(runs,key=lambda x:x['length'],reverse=True),'explicit_allocation_candidate':{'stock_request':hex(0x14100),'metadata_request':hex(0x14c70),'with_4096_byte_code_reservation':hex(0x15c70),'code_offset':hex(0x14c70),'code_end_offset_exclusive':hex(0x15c70),'status':'owned only if explicitly allocated; executable status and installation unverified'},'firmware_modified':False}
pathlib.Path('outputs/Digitone-executable-space-screening.json').write_text(json.dumps(result,indent=2));print('padding runs',len(runs));print('largest',result['padding_runs'][:8]);print('startup');print('\n'.join(sum(windows.values(),[])))
