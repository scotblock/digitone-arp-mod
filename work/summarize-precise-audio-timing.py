import pathlib,json,math,hashlib
from fractions import Fraction
p=pathlib.Path('outputs');j=json.loads((p/'Digitone-precise-audio-timing-pilot.json').read_text());checks=json.loads((p/'Digitone-precise-audio-timing-checks.json').read_text())
assert j['failure'] is None and len(j['runs'])==2 and j['firmware_before']==j['firmware_after']
s={'firmware_modified':False,'assumed_core_hz':j['fsys_assumption_hz'],'active_playback_ms_per_run':100,'controlled_checks':checks['passed'],'runs':[],'rounding_correction':'Playback preceded correction of next-frame proxy rounding by at most one cycle; arrival and interrupt execution unchanged. Aggregate completion latency checked against floor(period), proving no misses with the corrected deadline as well.'}
for r in j['runs']:
 assert r['halted'] is None and r['clock']['decode_mismatches']==0 and not any(v['flags']&7 for v in r['decoder_flags'])
 a=r['memory_model']['audio_event_timing'];co=a['counts'];arb=r['memory_model']['shared_arbiter'];period=Fraction(a['period']);active=r['memory_model']['timestamped_payload']['active_channels']
 assert not arb['counts'].get('audio_requests_dropped_while_pending',0) and not co.get('completion_IRQ_coalesced',0) and not co['next_frame_deadline_misses']
 assert co['request_to_completion_max_cycles']<math.floor(period)
 assert co['frames_requested']*2==co['audio_completed']+sum(ch in (52,54) for ch in active)
 assert co['completion_IRQ_assertions']==co['vector_174_delivered']
 d=r['render_deadline'];s['runs'].append({'mode':r['mode'],'total_ms':r['ms'],'core_cycles':r['clock']['cycles'],'render_count':d['runs'],'worst_render_us':d['worst_cycles']/250,'render_margin_us':(d['period_cycles']-d['worst_cycles'])/250,'late_renders':d['late'],'stale_audio_captures':r['DMA_summary']['captures_with_unfresh_words'],'captured_frames':r['DMA_summary']['after_warmup_captures'],'timing':co,'request_period_cycles':str(period),'max_completion_us':co['request_to_completion_max_cycles']/250,'max_IRQ_attempt_delay_us':co['completion_to_IRQ_attempt_max_cycles']/250,'max_request_service_lateness_us':co['arrival_service_lateness_max_cycles']/250,'pending_channels':active,'dropped_requests':0,'max_core_timer_gap_us':r['DMA_summary']['maximum_clock_timer_gap_cycles']/250})
q=j['runs'][1]['quantizer_calls'];pitch=[x for x in j['runs'][1]['pitch'] if x['track']==2];assert len(q)==len(pitch)==1
s['pitch_checks']=[]
for a,b in zip(q,pitch):
 assert b['fixed_note']==a['expected']*65536;s['pitch_checks'].append({'input':a['note'],'expected':a['expected'],'actual':b['fixed_note']//65536})
assert [(x['track'],x['fixed_note']) for x in j['runs'][0]['pitch'] if x['track']!=2]==[(x['track'],x['fixed_note']) for x in j['runs'][1]['pitch'] if x['track']!=2]
s['other_observed_pitch_tracks_match']=True;s['firmware_sha256']=j['firmware_after'];s['MAIN_OS_sha256']=hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest();s['implementation_sha256']=hashlib.sha256(pathlib.Path('work/precise_audio_dma.py').read_bytes()).hexdigest()
assert s['MAIN_OS_sha256']=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
(p/'Digitone-precise-audio-timing-summary.json').write_text(json.dumps(s,indent=2));print(json.dumps(s,indent=2))
