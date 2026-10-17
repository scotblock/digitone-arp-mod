"""Summarize native functional handoff and assumed-cost playback evidence."""
import pathlib,json,hashlib,collections
O=pathlib.Path('outputs')
handoff=json.loads((O/'Digitone-queued-sustained-combined-handoff.json').read_text())
fixture=handoff['delayed_note_fixture']
w=next(e for e in handoff['events'] if e['kind']=='backing_write' and e['backing']!=e['incoming_backing'])
commit=next(e for e in handoff['events'] if e['kind']=='transition_commit_done' and e['ms']>=w['ms'] and e['backing']==w['incoming_backing'])
matching=[e for e in handoff['events'] if e.get('event')==fixture['event'] and e.get('generation')==fixture['generation']]
accepted=next(e for e in matching if e['kind']=='acceptance')
assert fixture['ms']<w['ms']<accepted['ms']
assert accepted['backing']==w['incoming_backing'] and accepted['publication']['backing']==w['backing']
assert any(e['event']==fixture['event'] and e['generation']==fixture['generation'] for e in w['pending_publications'])
assert w['sustain_flags'][6:8]=='01' and int(w['sustain_lists'][3],16)
assert handoff['marks'][-1]['sustain_flags']=='00'*8 and handoff['marks'][-1]['sustain_lists'][3]=='0x0'
assert handoff['failure'] is None and handoff['halted'] is None
summary={'firmware_modified':False,'firmware_sha256':handoff['firmware_sha256'],
 'confirmed_handoff':{'published_ms':w['ms'],'publication_block_completed_ms':commit['ms'],'writer':w['pc'],
 'old_backing':w['backing'],'new_backing':w['incoming_backing'],'queued_event':fixture['event'],
 'event_generation':fixture['generation'],'queue_publication_ms':fixture['ms'],'accepted_ms':accepted['ms'],
 'same_generation_crossed_handoff':True,'sustain_list_present_at_handoff':True,'sustain_released_and_list_cleared':True,
 'fixtures':['UART9 input bytes scheduled through the native receive/parser path; both input filter bits enabled in PC RAM.',
 'One actual stock-produced note delayed by 48,000,000 queue ticks at stock publisher entry; native transition and consumer unchanged.'],
 'clock_model':'Untimed native functional execution, separate from cycle-aware playback.'},'playback':[]}
for name in ['nominal-stock','nominal-all','adverse-stock','adverse-all','adverse-pattern2-stock','adverse-pattern2-all-active-context']:
 p=O/('Digitone-heavy-'+name+'.json')
 if not p.exists():continue
 r=json.loads(p.read_text());q=r['runs'][0]
 assert r['failure'] is None and r['firmware_before']==r['firmware_after']==summary['firmware_sha256']
 d=q['render_deadline'];memory=q['memory_model']
 row={'case':name,'emulated_ms':q['ms'],'renders':d['runs'],'worst_render_us':d['worst_cycles']/264,
 'render_margin_us':(d['period_cycles']-d['worst_cycles'])/264,'late_renders':d['late'],
 'DMA':q['DMA_summary'],'FIFO':memory['FIFO'],'serial_phase':memory['serial_phase'],
 'allocation_bits_observed':sorted({x['bits'] for x in q['allocation_mask_samples']}),
 'accepted_pitch_events':len(q['pitch']),'quantizer_calls':len(q['quantizer_calls']),
 'valid_quantizer_calls':sum(int(x['word'],16)>>31 for x in q['quantizer_calls']),
 'fixture_word_count':len(q['candidate_fixture']),'decode_mismatches':q['clock']['decode_mismatches'],
 'assumed_core_hz':264000000,'assumed_bus_hz':132000000,
 'costs':{'fill':20 if name.startswith('nominal') else 40,'writeback':16 if name.startswith('nominal') else 32,'beat':4 if name.startswith('nominal') else 8}}
 row['quantizer_output_checks']=[]
 for c in q['quantizer_calls']:
  output=next(x for x in q['pitch'] if x['cycles']>c['cycles'])
  check={'input_note':c['note'],'word':c['word'],'expected':c['expected'],'observed':output['fixed_note']/65536,'matches':output['fixed_note']==c['expected']*65536}
  row['quantizer_output_checks'].append(check)
  assert check['matches']
 row['stale_audio_reads']=[x for x in q['DMA_captures'] if x['ms']>=20 and x.get('unfresh_words',0)>0]
 row['observed_backings']=sorted({x['backing'] for x in q['workload'] if 'backing' in x})
 summary['playback'].append(row)
overlay=json.loads((O/'Digitone-delayed-note-overlay-handoff.json').read_text())
f=overlay['delayed_note_fixture']
pub=next(e for e in overlay['events'] if e['kind']=='queue_publish' and e['event']==f['event'] and e['generation']==f['generation'])
assert pub['metadata_word']=='0x800000bd'
oa=next(e for e in overlay['events'] if e['kind']=='acceptance' and e['event']==f['event'] and e['generation']==f['generation'])
ow=next(e for e in overlay['events'] if e['kind']=='backing_write' and e['backing']!=e['incoming_backing'])
assert pub['ms']<ow['ms']<oa['ms'] and oa['backing']==ow['incoming_backing']
summary['direct_note_overlay_probe']={'captured_word':pub['metadata_word'],'queue_crossing_observed':True,
 'quantizer_executed_for_delayed_note':False,'interpretation':'Capture and event-slot lifetime evidence for this direct note; arp retained-context quantization at handoff is not proved by this case.'}
summary['limitations']=['Finite runs from one experimental OS 1.42 snapshot, not hardware validation.',
 'Seven allocation bits do not establish an eight-voice worst workload or every voice/effect algorithm.',
 'Clock candidates and memory/cache costs assumed; physical cache values, codec phase and unrelated peripheral DMA remain unverified.',
 'Timing playback and functional handoff are separate experiments; no cycle-aware full handoff tested.',
 'Cached producer context-copy implementation and full reserved-RAM ownership remain unresolved.',
 'Valid-context timing fixtures inject metadata at commit; they do not prove natural cached-context capture.']
(O/'Digitone-confirmed-handoff-heavy-playback-summary.json').write_text(json.dumps(summary,indent=2))
lines=['# Digitone OS 1.42: confirmed handoff and heavier PC playback','',
 'The queued/sustained functional handoff is confirmed in the PC engine. The active modified playback case exposed one stale stereo DMA read under doubled memory costs; its stock counterpart had none. Firmware remains unchanged. These are PC observations and assumed-cost timing tests; they do not establish readiness to flash.','',
 '## Confirmed queued and sustained handoff','',
 f'The native playback writer at {w["pc"]} replaced backing {w["backing"]} with {w["incoming_backing"]} at {w["ms"]:.3f} ms. Execution reached the publication-block completion at 0x40095bd6 and subsequently produced/consumed notes from the new backing. This is evidence of replacement, beyond a queued panel request.','',
 f'Event {fixture["event"]}, allocation generation {fixture["generation"]}, was published from the old backing at {fixture["ms"]:.3f} ms. It was still pending at replacement and was accepted from the same event generation at {accepted["ms"]:.3f} ms under the new backing. The queued crossing was deliberately created by delaying one actual stock-produced note by 48,000,000 queue ticks in PC RAM. Stock insertion, transition and consumption code executed.','',
 'MIDI CC64 traversed the UART9 receive ring, interrupt, parser and recovered stock controller handler. Track 4 (zero-based 3) had sustain enabled and a non-empty held-note list at replacement. A later CC64=0 cleared both. Input bytes and input-enable settings were explicit PC fixtures; no hardware MIDI ports were opened.','',
 'A separate overlay probe captured 0x800000bd from the old pattern and preserved the delayed event generation across replacement. The delayed event was a direct note, and its arp quantizer did not execute. This does not prove arp retained-context pitch behavior during a handoff.','',
 '## Longer playback and memory sensitivity','',
 'Core/bus candidates: 264/132 MHz; conditional audio rate: 48 kHz. Baseline costs are fill/writeback/beat 20/16/4 cycles; adverse costs are 40/32/8. The serial-phase FIFO and shared DMA arbiter models were used with actual delayed payload copying. Seven allocation bits stayed set during the heavier held-note interval. Render timing measures vector 191 entry through RTE, including preemption and handler cleanup; handler-period overruns and stale payload reads are separate measurements.','',
 '| Case | Emulated ms | Handlers | Worst handler µs | Period margin µs | Overruns | Stale reads | Valid quantizer calls |',
 '|---|---:|---:|---:|---:|---:|---:|---:|']
for r in summary['playback']:
 lines.append(f'| {r["case"]} | {r["emulated_ms"]:.2f} | {r["renders"]} | {r["worst_render_us"]:.2f} | {r["render_margin_us"]:.2f} | {r["late_renders"]} | {len(r["stale_audio_reads"])} | {r["valid_quantizer_calls"]} |')
lines+=['','The four paired baseline/adverse runs exercise the installed hook path but contain no valid arp quantizer calls. They therefore measure heavier playback and inactive-context overhead, not the active scale-lock workload. Supplementary cases are listed separately to avoid merging different workloads.','',
 'In the arp-enabled adverse pair, stock had 8 handler-period overruns but no stale reads. The overlay had 10 overruns and one stale 8-byte stereo payload at approximately 63.334 ms: its next final-word store occurred 155 cycles (0.587 µs) after capture. Neither case recorded FIFO underflow/overflow or invalid shifted words, and the final core/timer gap was zero. The modified workload therefore fails this assumed-cost payload-freshness check even though FIFO occupancy stays healthy.','',
 'All four native quantizer outputs matched the oracle: 57→56, 69→68, 81→80, and 57→56 on zero-based track 2. The other 13 observed pitches matched stock. The valid context word was explicitly supplied at the commit hook for these timing cases; natural cached-context capture is not proved. This pair combines helper execution and intended pitch changes, so it does not isolate which contribution caused the first late store.','',
 '## What remains','',*['- '+x for x in summary['limitations']],'',
 'Next: trace the first stale-read render and use a stock-instruction detour / fixed-pitch control to separate hook, cache, scheduling and changed-pitch costs. Then combine a confirmed arp-producing queue crossing with natural cached-context capture and retained-context pitch output, and measure that full handoff under the cycle-aware model. Physical timing still needs independent evidence.']
(O/'Digitone-confirmed-handoff-heavy-playback-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'confirmed_handoff':summary['confirmed_handoff'],'playback':[{k:r[k] for k in ['case','renders','render_margin_us','late_renders','valid_quantizer_calls']} for r in summary['playback']]},indent=2))
