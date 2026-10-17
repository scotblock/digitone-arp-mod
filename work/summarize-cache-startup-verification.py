"""Join startup provenance, uninterrupted handoff witnesses and timing limits."""
import pathlib,json,hashlib
out=pathlib.Path('outputs');load=lambda name:json.loads((out/name).read_text())
startup=load('Digitone-cache-context-startup-playback.json');build=load('Digitone-cache-context-helper-checks.json')['build']
assert startup['passed'] and startup['code_bytes']==2564 and startup['startup']['copy_longs']==641
assert startup['loader']['same_machine_into_initializer'] and startup['loader']['main_matches'] and not startup['loader']['flash_writes']
assert startup['firmware_before']==startup['firmware_after']
for stage in startup['startup']['stages']:
 assert stage['code_intact'] and stage['guards_intact'] and stage['ready']==1 and not stage['unexpected_writes']
def functional(filename):
 r=load(filename);assert r['failure'] is None and not r['halted'] and all(r['storage_checks'].values())
 assert not r['helper_reinjected'] and not r['PC_runtime_extension_installed'] and r['inherited_hook_checks']
 assert 'diagnostic_metadata_injection' not in r
 return r
base=functional('Digitone-cache-startup-handoff.json')
native=functional('Digitone-cache-startup-handoff-native-pattern-copy.json')
exploratory=[functional('Digitone-cache-startup-handoff-receiving-arp.json'),functional('Digitone-cache-startup-handoff-receiving-arp-fresh-live.json')]
def matching_pitch(r,q):
 p=next(x for x in r['pitch_outputs'] if x['event']==q['event'] and x['generation']==q['generation'] and x['ordinal']>q['ordinal'])
 assert p['fixed_note']>>16==q['expected'];return p
def transition(r):
 f=r['delayed_note_fixture'];i=next(i for i,x in enumerate(r['events']) if x['kind']=='backing_write' and x['incoming_backing']=='0x407b00cc' and x['ms']>f['ms'])
 w=r['events'][i];done=next(x for x in r['events'][i:] if x['kind']=='transition_commit_done' and x['backing']==w['incoming_backing'])
 return {'write_ms':w['ms'],'completed_ms':done['ms'],'writer_pc':w['pc'],'completion_pc':done['pc']}
def old_note(r):
 f=r['delayed_note_fixture'];q=next(x for x in r['quantizer_calls'] if x['event']==f['event'] and x['generation']==f['generation']);p=matching_pitch(r,q)
 a=next(x for x in r['events'] if x['kind']=='acceptance' and x.get('event')==q['event'] and x['generation']==q['generation']);pub=a['publication'];t=transition(r)
 assert pub['metadata']==a['candidate_at_acceptance']==q['word']=='0x800040bd'
 assert pub['ms']<t['write_ms']<=t['completed_ms']<q['ms'] and q['expected']==56
 return {'event':q['event'],'generation':q['generation'],'publication_ms':pub['ms'],'acceptance_ms':a['ms'],'context':q['word'],'input':q['note'],'output':p['fixed_note']>>16,'publication_backing':pub['backing'],'acceptance_backing':a['backing'],'transition':t}
old_base=old_note(base);old_native=old_note(native);t=transition(native)
fresh=[]
for q in native['quantizer_calls']:
 if q['ms']<=t['completed_ms'] or q['word']!='0x8000433b':continue
 p=matching_pitch(native,q)
 # A scheduled subsequent arp step may inherit the accepted record. Count
 # the direct constructor/publication witness separately from this reuse.
 pubs=[x for x in native['events'] if x['kind']=='queue_publish' and x['event']==q['event'] and x['generation']==q['generation']]
 producer=[x for x in native['events'] if x['kind']=='producer' and x['event']==q['event'] and x['generation']==q['generation'] and x['producer_backing']=='0x407b00cc' and x['producer_track']==2]
 item={'event':q['event'],'generation':q['generation'],'quantizer_ms':q['ms'],'context':q['word'],'input':q['note'],'output':p['fixed_note']>>16,'direct_receiving_pattern_producer':bool(producer)}
 if producer:
  pub=next(x for x in pubs if x['metadata']==q['word']);assert pub['ms']>t['completed_ms'] and pub['backing']=='0x407b00cc'
  item.update(publication_ms=pub['ms'],producer_backing=producer[0]['producer_backing'])
 fresh.append(item)
assert fresh and any(x['direct_receiving_pattern_producer'] for x in fresh)
assert fresh[0]['quantizer_ms']<old_native['acceptance_ms']
timing=[]
for name in ['prefix-stock','prefix-fixed','prefix-full','sustained-stock','sustained-full','sustained-full-slow-memory','sustained-stock-slow-memory']:
 r=load('Digitone-cache-startup-timing-'+name+'.json');q=r['runs'][0]
 assert not q['candidate_fixture'] and not q['startup_provenance']['helper_and_header_reinjected']
 row={'case':name,'failure':r['failure'],'elapsed_seconds':r['elapsed_seconds'],'cache_copy_calls':len(q['cache_copy_calls']),'quantizer_calls':len(q['quantizer_calls']),'metadata_fixture_count':len(q['candidate_fixture'])}
 if r['failure'] is None:
  assert q['clock']['decode_mismatches']==0 and q['halted'] is None and all(q['storage_checks'].values())
  fifo=q['memory_model']['FIFO']
  faults={k:fifo['counts'].get(k,0) for k in ['TX_underflow','TX_overflow','RX_empty_read','RX_overflow','invalid_shift_words_completed']}
  matched=0
  for quant in q['quantizer_calls']:
   word=int(quant['word'],16)
   if not word&0x80000000:continue
   track=(word>>13)&3
   pitch=next(x for x in q['pitch'] if x['cycles']>=quant['cycles'] and x['track']==track)
   expected=quant['note'] if name=='prefix-fixed' else quant['expected']
   assert pitch['fixed_note']>>16==expected,(name,quant,pitch)
   matched+=1
  row.update(ms=q['ms'],DMA=q['DMA_summary'],FIFO_faults=faults,valid_context_quantizations_matching_pitch=matched,render_deadline=q['render_deadline'],storage_checks=q['storage_checks'])
 else:
  assert r['failure']['message']=='DMA restart while modeled transfer is active'
  row.update(last_audio_capture_ms=q['DMA_captures'][-1]['ms'],workload=q['workload'])
 timing.append(row)
slow=[x for x in timing if x['failure']]
assert len(slow)==2 and slow[0]['workload']==slow[1]['workload'] and slow[0]['last_audio_capture_ms']==slow[1]['last_audio_capture_ms']
summary={'firmware_modified':False,'startup_continuity_verified_in_PC':True,'revised_helper_sha256':build['sha256'],'bootstrap_copy_longs':641,'fresh_and_old_eligible_arp_notes_observed_in_one_uninterrupted_handoff':True,'inherited_state_old_note_control':old_base,'uninterrupted_handoff_old_note':old_native,'uninterrupted_handoff_new_notes':fresh,'timing_cases':timing,'physical_timing_verified':False,'slower_memory_sensitivity_inconclusive':True,'assumed_costs':{'core_hz':264000000,'bus_hz':132000000,'audio_hz':48000,'normal_fill_writeback_beat':[40,32,8],'slow_fill_writeback_beat':[80,64,16]},'firmware_sha256':native['firmware_sha256'],'limitations':['Finite emulator runs do not certify physical clock/cache/RAM ownership or all producers.','Native copy/paste prepares matching arp-enabled patterns while stopped; subsequent tested handoff plays continuously. Roots/scales and delayed queue timestamp remain labeled PC fixtures.','The functional complete handoff and cycle-aware voice-heavy timing runs are separate workloads.','Slower-memory stock and modified controls both hit an unsupported DMA restart before observed cache copies or quantization; this sensitivity is not a hardware pass or fail.','Backing-data-only clone and MIDI probe did not establish a fresh eligible arp note and are not counted as positive witnesses.']}
(out/'Digitone-cache-startup-verification-summary.json').write_text(json.dumps(summary,indent=2))
lines=['# Digitone OS 1.42: revised startup, handoff and timing verification','',
'**The revised helpers now survive actual PC loader/startup execution. A fresh receiving-pattern arp note and an older queued arp note use their respective scales during one uninterrupted handoff. Timing remains conditional on model assumptions.** Device firmware is unchanged.','',
'The ephemeral loader fixture contains the 2,564-byte helper image plus both cache-copy call-site hooks. The stock loader accepts/decompresses it, and its machine state continues into application initialization. The early copier copies 641 longwords; the initializer establishes the owner pointer and ready header. Cold, intro and settled stages preserve the complete helper image and guards, with no unexpected reserved-region writes. Playback/handoff/timing restore those guest snapshots and verify both hooks; no helper or header is reinstalled by the host.','',
f"The basic inherited-startup control publishes an old-scale event at {old_base['publication_ms']:.3f} ms, completes replacement at {old_base['transition']['completed_ms']:.3f} ms and accepts the same generation at {old_base['acceptance_ms']:.3f} ms. It retains `0x800040bd` and outputs 56.",'',
'## Fresh and old notes in the same transition','',
'Native panel copy/paste prepares an arp-enabled receiving pattern while stopped, including its associated settings. The playback test then starts and performs a complete pattern-2 → pattern-1 replacement without stopping the transport. Direct backing-data cloning and an additional MIDI probe did not establish the eligible fresh-note case; neither is counted as a positive witness.','',
'| Witness | Event/generation | Context | Input → output | Time |','|---|---|---|---|---|']
for x in fresh:lines.append(f"| Fresh receiving-pattern arp{' input' if x['direct_receiving_pattern_producer'] else ' continuation'} | `{x['event']}` / {x['generation']} | `{x['context']}` | {x['input']} → {x['output']} | {x['quantizer_ms']:.3f} ms |")
lines.append(f"| Older queued arp input | `{old_native['event']}` / {old_native['generation']} | `{old_native['context']}` | {old_native['input']} → {old_native['output']} | {old_native['acceptance_ms']:.3f} ms |")
lines+=['',f"Replacement completes at {t['completed_ms']:.3f} ms. The direct fresh event is constructed afterward from receiving backing `0x407b00cc`, track 2, root 59/raw scale 5, and carries `0x8000433b` through publication and native quantization. The older event was published from backing `0x407c61e9`, root 61/raw scale 0, before replacement and arrives later with `0x800040bd`. Same event/generation and execution-order matches establish the witnesses; no eligibility, identity or context metadata is supplied at acceptance.",'',
'## Timing controls','',
'Assumptions: 264 MHz core, 132 MHz bus, 48 kHz audio, normal fill/writeback/beat costs 40/32/8. These are modeled costs, not physical measurements. Acceptance-time context injection is disabled in every case. The fixed-pitch control runs the helper path then restores the stock pitch as a diagnostic.','',
'| Case | Duration | Native quantizations | Stale DMA captures | Minimum margin | Handler-period overruns |','|---|---:|---:|---:|---:|---:|']
for x in timing:
 if x['failure']:lines.append(f"| {x['case']} | Incomplete | {x['quantizer_calls']} | Inconclusive | Inconclusive | Inconclusive |")
 else:
  d=x['DMA'];lines.append(f"| {x['case']} | {x['ms']:.3f} ms | {x['quantizer_calls']} | {d['captures_with_unfresh_words']} | {d['minimum_margin_us']:.6f} µs | {x['render_deadline']['late']} |")
lines+=['',
'The doubled memory-cost controls (80/64/16) both stop on `DMA restart while modeled transfer is active`, at the same workload boundary and last audio-capture timestamp, before any observed cache-copy call or quantization. This exposes a DMA-model limit and leaves the sensitivity check inconclusive. Positive normal-cost results do not establish timing safety across that range. Handler-period overruns and capture margins measure different boundaries; zero stale captures is not a claim that every handler finishes within one nominal period.','',
'## Next step','',
'Resolve active-transfer restart behavior in the software DMA model, then rerun the sensitivity pair. A cycle-aware complete pattern handoff should also be measured; it has so far been exercised functionally, separately from voice-heavy timing. Physical timing/cache coherence and exhaustive ownership remain unverified, so these results do not justify flashing the device.']
(out/'Digitone-cache-startup-verification-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Saved revised startup, uninterrupted handoff and timing verification reports')
