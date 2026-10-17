from pathlib import Path
source=Path('work/test-os144-real-selector-caller.py').read_text().split('\ntry:\n')[0]
exec(compile(source,'caller-replay-functions','exec'))
OUT=Path('outputs/Digitone-OS1.44-real-selector-context.json')
result={'firmware_modified':False,'startup_hook_installed':False,'cases':[],'failure':None,'limits':['Uses one stock-generated eligible caller state with a deliberately non-chromatic sidecar word; stock event/selection fields are unaltered.','No timing, scheduler/DMA continuation or complete playback integration.']}
capture=captures['caller_states'][0];word=0x800040bd
rows=json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']
pcs=next(x['pitch_classes'] for x in rows if x['raw_scale']==0)
try:
 for fault in [None,'magic','version','size','ready','null_pointer']:
  a=replay(capture,'stock',word_override=word,fault=fault);b=replay(capture,'helpers',word_override=word,fault=fault)
  points_a={x['pc']:x for x in a['boundaries']};points_b={x['pc']:x for x in b['boundaries']}
  case={'fault':fault,'word':hex(word),'stock':a,'helpers':b};result['cases'].append(case)
  assert a['selector_entries']==b['selector_entries'] and a['event_final']==b['event_final']
  assert a['stock_region_hashes']==b['stock_region_hashes']
  for pc in ['0x4009e694','0x4009e738']:assert points_a[pc]==points_b[pc],(fault,pc)
  pc='0x4009e890';x,y=points_a[pc],points_b[pc];note=x['regs']['D6']>>16
  expected=note if fault else min((n for n in range(128) if (n-61)%12 in pcs),key=lambda n:(abs(n-note),n))
  assert y['regs']['D6']==expected<<16
  assert {k:v for k,v in x['regs'].items() if k!='D6'}=={k:v for k,v in y['regs'].items() if k!='D6'}
  assert x['SR']==y['SR'] and x['stack64']==y['stack64'] and x['event72']==y['event72']
  if fault:assert a['boundaries']==b['boundaries'] and b['helper_hits'].get('quantize',0)==0
  else:
   assert note==57 and expected==56 and b['helper_hits'].get('quantize',0)==1
   case['final_boundary_register_differences']={k:[points_a['0x4009d7d8']['regs'][k],points_b['0x4009d7d8']['regs'][k]] for k in x['regs'] if points_a['0x4009d7d8']['regs'][k]!=points_b['0x4009d7d8']['regs'][k]}
  case.update(passed=True,stock_note=note,helper_note=expected,selector_and_commit_boundaries_identical=True,pitch_other_registers_status_stack_and_event_identical=True)
  print('PASS',fault,note,'->',expected,flush=True);OUT.write_text(json.dumps(result,indent=2))
 result['passed']=True
except BaseException:
 result['failure']=traceback.format_exc();print(result['failure'],flush=True)
finally:
 result['firmware_sha256_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();OUT.write_text(json.dumps(result,indent=2))
