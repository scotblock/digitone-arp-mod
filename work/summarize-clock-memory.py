import pathlib,json,hashlib
root=pathlib.Path('outputs');summary={'firmware_modified':False,'core_clock':{'verified_actual_hz':None,'firmware_bus_calibration_hz':132000000,'inferred_intended_core_hz':264000000,'previous_sensitivity_assumption_hz':250000000,'unknowns':['Hardware serial-boot reset configuration','Board oscillator/reference clock','Later computed clock writers not globally certified']},'cache':{'instruction_bytes':8192,'data_bytes':8192,'ways':4,'sets':128,'line_bytes':16,'observed_CACR':'0xa50ce100','observed_ACR0':'0x4007e020','data_DDR_policy':'copyback 0x40000000..0x47ffffff','data_default_policy':'cache-inhibited precise','instruction_default_policy':'cacheable'},'scenarios':[],'offline_data_cost_sensitivity':[]}
for f in ['Digitone-cache-sensitivity-20.json','Digitone-memory-sensitivity-40.json','Digitone-cache-stock-40.json']:
 j=json.loads((root/f).read_text());assert j['failure'] is None and j['firmware_before']==j['firmware_after']
 for r in j['runs']:
  assert r['clock']['decode_mismatches']==0
  d=r['render_deadline'];c=d['worst_cycles']
  summary['scenarios'].append({'file':f,'mode':r['mode'],'I_fill_extra_cycles':r['clock']['icache']['miss_penalty'],'completed_renders':d['runs'],'worst_cycles':c,'worst_us_at_250MHz':c/250,'render_margin_us':(d['period_cycles']-c)/250,'render_late':d['late'],'DMA':r['DMA_summary'],'valid_context_fixtures':len(r.get('candidate_fixture',[]))})
r=json.loads((root/'Digitone-memory-sensitivity-40.json').read_text())['runs'][0]
for p in [0,4,8,16,20]:
 costs=[w['wall_cycles']+p*(w.get('fills',0)+w.get('dirty_evictions',0)) for w in r['data_cache_windows']]
 summary['offline_data_cost_sensitivity'].append({'extra_cycles_per_fill_and_dirty_eviction':p,'worst_cycles':max(costs),'late_at_250MHz':sum(v>166667 for v in costs),'late_at_conditional_264MHz':sum(v>176000 for v in costs),'note':'Offline projection of same 250 MHz scheduling trace; not a rerun at 264 MHz and not measured DDR costs'})
summary['worst_render_data_accesses']=max(r['data_cache_windows'],key=lambda w:w['wall_cycles'])
p=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
summary['sysex_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();summary['MAIN_OS_sha256']=hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()
assert summary['sysex_sha256']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
assert summary['MAIN_OS_sha256']=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
(root/'Digitone-clock-and-memory-summary.json').write_text(json.dumps(summary,indent=2))
print('All three timing result files passed integrity and decoder checks; summary saved.')
