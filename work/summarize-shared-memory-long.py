import pathlib,json,hashlib
out=pathlib.Path('outputs');j=json.loads((out/'Digitone-shared-memory-long-comparison.json').read_text())
assert j['failure'] is None and len(j['runs'])==2 and 'firmware_after' in j
assert j['firmware_before']==j['firmware_after']
s={'firmware_modified':False,'fsys_assumption_hz':j['fsys_assumption_hz'],'requested_playback_ms':1000,'elapsed_wall_seconds':j['elapsed_seconds'],'runs':[],'model_checks':json.loads((out/'Digitone-shared-memory-model-checks.json').read_text())}
for r in j['runs']:
 assert r['halted'] is None and r['clock']['decode_mismatches']==0
 assert not any(x['flags']&7 for x in r['decoder_flags'])
 assert not r['memory_model']['counts'].get('dynamic_control_first_execution_uncovered',0)
 d=r['render_deadline'];margin=d['period_cycles']-d['worst_cycles']
 s['runs'].append({'mode':r['mode'],'emulated_ms':r['ms'],'render':dict(d,worst_us=d['worst_cycles']/250,margin_us=margin/250),'DMA':r['DMA_summary'],'memory':r['memory_model'],'quantizer_calls':len(r['quantizer_calls']),'valid_context_calls':sum(int(x['word'],16)!=0 for x in r['quantizer_calls']),'candidate_fixture_injections':len(r['candidate_fixture']),'hooks':r['hooks'],'pitch_fixed_notes':sorted(set(x['fixed_note'] for x in r['pitch'])),'audio_sha256':r['audio_sha256'],'clock_timer_gap_max_us':r['DMA_summary']['maximum_clock_timer_gap_cycles']/250})
s['sysex_sha256']=j['firmware_after'];s['MAIN_OS_sha256']=hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()
assert s['MAIN_OS_sha256']=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
(out/'Digitone-shared-memory-long-summary.json').write_text(json.dumps(s,indent=2))
print(json.dumps(s,indent=2))
