import pathlib,json,hashlib
out=pathlib.Path('outputs');load=lambda n:json.loads((out/n).read_text())
cases=[]
for name in ['stock-normal','full-normal','stock-double','full-double','stock-150pct','full-150pct','stock-double-voices','full-double-voices','prepared-stock-normal','prepared-full-normal','prepared-stock-150pct','prepared-full-150pct','prepared-stock-double','prepared-full-double']:
 r=load('Digitone-dma-restart-'+name+'.json');q=r['runs'][0]
 assert r['failure'] is None and not q['halted'] and all(q['storage_checks'].values())
 assert q['clock']['decode_mismatches']==0 and not q['candidate_fixture']
 m=q['memory_model'];f=m['FIFO']['counts']
 cases.append({'case':name,'ms':q['ms'],'confirmed_pattern_start':q.get('confirmed_start_pattern_backing'),'final_observed_backing':q['workload'][-1]['backing'],'cache_copies':len(q['cache_copy_calls']),'quantizations':len(q['quantizer_calls']),'DMA':q['DMA_summary'],'FIFO_faults':{k:f.get(k,0) for k in ['TX_underflow','TX_overflow','RX_overflow','RX_empty_read','invalid_shift_words_completed']},'restart_requests':m['timestamped_payload']['counts'].get('software_requests_while_inflight',0),'restart_samples':m['timestamped_payload']['restart_samples'],'render_deadline':q['render_deadline'],'storage_checks':q['storage_checks']})
r=load('Digitone-cycle-complete-handoff-native-pattern-copy.json')
assert r['failure'] is None and all(r['storage_checks'].values()) and not r['helper_reinjected']
assert not r['PC_runtime_extension_installed'] and r['timing_start']['hle'] is False
f=r['delayed_note_fixture'];events=r['events']
wi=next(i for i,e in enumerate(events) if e['kind']=='backing_write' and e['incoming_backing']=='0x407b00cc' and e['cycles']>f['cycles'])
w=events[wi];done=next(e for e in events[wi:] if e['kind']=='transition_commit_done' and e['backing']=='0x407b00cc')
def pitch(q):
 p=next(p for p in r['pitch_outputs'] if p['event']==q['event'] and p['generation']==q['generation'] and p['ordinal']>q['ordinal'])
 assert p['fixed_note']>>16==q['expected'];return p
old=next(q for q in r['quantizer_calls'] if q['event']==f['event'] and q['generation']==f['generation'])
p=pitch(old)
assert old['word']=='0x800040bd' and f['cycles']<w['cycles']<=done['cycles']<old['cycles']
fresh=[]
for q in r['quantizer_calls']:
 if q['cycles']<=done['cycles'] or q['word']!='0x8000433b':continue
 ps=[e for e in events if e['kind']=='producer' and e.get('event')==q['event'] and e.get('generation')==q['generation'] and e.get('producer_backing')=='0x407b00cc' and e.get('producer_track')==2]
 pp=pitch(q)
 fresh.append({'event':q['event'],'generation':q['generation'],'cycles':q['cycles'],'ms':q['ms'],'context':q['word'],'input':q['note'],'output':pp['fixed_note']>>16,'direct_producer':bool(ps)})
assert any(q['direct_producer'] for q in fresh)
mem=r['timing']['memory'];caps=[c for c in r['DMA_captures'] if c['ms']>=20]
summary={'firmware_modified':False,'restart_checks':load('Digitone-dma-restart-latch-checks.json'),'sensitivity':cases,'handoff':{'modeled_duration_ms':r['final_timing']['ms'],'backing_write':{k:w[k] for k in ['cycles','ms','pc']},'completed_transition':{k:done[k] for k in ['cycles','ms','pc']},'commit_interval_cycles':done['cycles']-w['cycles'],'commit_interval_us':(done['cycles']-w['cycles'])/264,'old_note':{'event':old['event'],'generation':old['generation'],'publication_cycles':f['cycles'],'quantizer_cycles':old['cycles'],'quantizer_ms':old['ms'],'context':old['word'],'input':old['note'],'output':p['fixed_note']>>16},'fresh_notes':fresh,'captures_after_20ms':len(caps),'stale_captures':sum(not c['all_words_fresh'] for c in caps),'minimum_margin_us':min(c['completion_margin_cycles']/264 for c in caps if c['completion_margin_cycles'] is not None),'FIFO_counts':mem['FIFO']['counts'],'render_deadline':r['timing']['render_deadline'],'storage_checks':r['storage_checks'],'physical_timing_verified':False},'firmware_sha256':r['firmware_sha256'],'limitations':['Timing assumes a 264 MHz core, 132 MHz bus and 48 kHz audio; memory costs are sensitivities, not calibrated hardware measurements.','Stopped native pattern preparation executes without cycle costs; timing begins before PLAY and runs uninterrupted through replacement and old-note acceptance.','Roots/scales, delayed publication timestamp, MIDI/input settings and initial FIFO phase are explicit PC fixtures; event eligibility and retained metadata are stock-produced.','Hardware cache-value coherence, codec phase and exhaustive RAM ownership remain unverified.','Active internal SADDR/DADDR/NBYTES readback and register-bus stall cycles are not comprehensively modeled. Request latching and per-minor writeback are the verified scope.']}
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
assert hashlib.sha256(syx.read_bytes()).hexdigest()==summary['firmware_sha256']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
(out/'Digitone-dma-restart-and-handoff-summary.json').write_text(json.dumps(summary,indent=2))
lines=['# Digitone: DMA restart and complete cycle-aware handoff','',
'The shared DMA model now retains a single software START request, coalesces overlapping requests with self-links, and updates SADDR/DADDR/CITER after each minor. It samples the descriptor when arbitration grants service. Twelve dedicated boundary/payload checks and twenty existing shared-arbiter checks pass. Firmware remains unchanged.','',
'The former exception occurs in stock channel 47: at cycle 10,565,841, `4009c8c4` reprograms and starts a new transfer while the previous 58-minor transfer is around minor 35 under doubled memory costs. Pending START coalesces with the next self-link; active address/count rewrites lose to minor writeback, while BITER survives. The corrected model exposes the consequence instead of aborting. These rules follow [NXP MCF5441x Reference Manual, chapter 19](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf).','',
'## Sensitivity controls','',
'All cases use inherited loader/startup state, disable acceptance-time metadata injection and run stock routines with HLE disabled. Normal fill/writeback/beat costs are 40/32/8; 1.5× costs are 60/48/12; doubled costs are 80/64/16.','',
'| Case | Duration (ms) | Quantizations | Stale captures | Minimum margin (µs) | Busy requests |','|---|---:|---:|---:|---:|---:|']
for c in cases:lines.append(f"| {c['case']} | {c['ms']:.3f} | {c['quantizations']} | {c['DMA']['captures_with_unfresh_words']} | {c['DMA']['minimum_margin_us']:.3f} | {c['restart_requests']} |")
h=summary['handoff'];lines+=['','## Complete handoff', '',f"Timed playback completes an actual pattern replacement at cycle {done['cycles']:,} ({done['ms']:.3f} ms). The interval from backing-pointer publication to the recovered completion point is {h['commit_interval_cycles']:,} modeled cycles ({h['commit_interval_us']:.3f} µs). This measures those two observed points, not every preceding pattern preparation operation.",'',f"The delayed source note remains `{old['word']}` and outputs {old['note']} → {p['fixed_note']>>16} after replacement. Fresh receiving-pattern notes are independently constructed from backing `407b00cc` and retain `8000433b`. Matches use event address, allocation generation and execution order.",'',f"Across {h['modeled_duration_ms']:.3f} ms, the handoff workload records {h['stale_captures']} stale captures after 20 ms and a minimum observed completion margin of {h['minimum_margin_us']:.3f} µs. See the summary for FIFO counters and handler-period overruns; these are distinct measurements.",'','## Limits','']
request=next(x for x in r['marks'] if x['label']=='request queued')
h['request_to_completion_cycles']=done['cycles']-request['cycles']
h['request_to_completion_ms']=h['request_to_completion_cycles']/264000
baseline=load('Digitone-stock-cycle-complete-handoff-native-pattern-copy.json')
assert baseline['failure'] is None and all(baseline['storage_checks'].values())
bcaps=[c for c in baseline['DMA_captures'] if c['ms']>=20]
bdone=next(e for e in baseline['events'] if e['kind']=='transition_commit_done' and e['backing']=='0x407b00cc' and e['cycles'] is not None)
h['stock_instruction_control']={'duration_ms':baseline['final_timing']['ms'],'completed_transition_cycles':bdone['cycles'],'completed_transition_ms':bdone['ms'],'stale_captures':sum(not c['all_words_fresh'] for c in bcaps),'minimum_margin_us':min(c['completion_margin_cycles']/264 for c in bcaps if c['completion_margin_cycles'] is not None),'FIFO_counts':baseline['timing']['memory']['FIFO']['counts'],'render_deadline':baseline['timing']['render_deadline'],'storage_checks':baseline['storage_checks']}
lines.insert(lines.index('## Limits'),f"The queued request → completed replacement interval is {h['request_to_completion_ms']:.3f} modeled ms, including the wait for the stock pattern boundary. The matching stock-instruction handoff records {h['stock_instruction_control']['stale_captures']} stale captures and a minimum margin of {h['stock_instruction_control']['minimum_margin_us']:.3f} µs.\n")
lines.insert(lines.index('## Complete handoff'),'The original panel-request sensitivity tests did not actually enter pattern 2 at the slower costs. Their zero hook calls do not demonstrate hook safety. The additional `prepared-*` controls begin on the confirmed native pattern-2 state; normal costs execute capture and quantization, while the slower windows still fail audio freshness before observed hook execution.\n')
(out/'Digitone-dma-restart-and-handoff-summary.json').write_text(json.dumps(summary,indent=2))
lines.extend('- '+x for x in summary['limitations'])
lines+=['','Positive completion margins do not establish freshness: a stale capture can refer to the previous buffer completion. The two modified stale captures coincide with the first fresh receiving-pattern quantization, whose pitch remains 57. This establishes a timing regression in this workload if the stock control has no stale captures; it does not yet isolate its cause. Active descriptor writeback behavior is a modeled interpretation of the register rules, not a hardware measurement.']
lines+=['','These PC results do not establish physical timing safety or justify flashing the device.']
(out/'Digitone-dma-restart-and-handoff-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'handoff':h,'sensitivity':[{k:c[k] for k in ['case','ms','quantizations','restart_requests']} for c in cases]},indent=2))
