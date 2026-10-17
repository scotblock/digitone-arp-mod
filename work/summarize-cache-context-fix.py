import pathlib,json,hashlib
out=pathlib.Path('outputs');load=lambda name:json.loads((out/name).read_text())
fixed=load('Digitone-indexed-context-handoff-cache-context-fixed.json')
immediate=load('Digitone-indexed-context-handoff-cache-context-fixed-no-delay.json')
refresh=load('Digitone-indexed-context-handoff-cache-context-fresh-settings.json')
helpers=load('Digitone-cache-context-helper-checks.json')
baseline=load('Digitone-queued-arp-verification-summary.json')
for r in [fixed,immediate,refresh]:
 assert r['failure'] is None and not r['halted'] and all(r['storage_checks'].values())
 assert 'diagnostic_metadata_injection' not in r
 assert r['firmware_sha256']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
def witness(r):
 f=r['delayed_note_fixture'];e=f['event'];g=f['generation']
 q=next(x for x in r['quantizer_calls'] if x['event']==e and x['generation']==g)
 p=next(x for x in r['pitch_outputs'] if x['event']==e and x['generation']==g and x['ordinal']>q['ordinal'])
 a=next(x for x in r['events'] if x['kind']=='acceptance' and x.get('event')==e and x['generation']==g)
 pub=a['publication'];assert pub and pub['generation']==g
 assert q['word']=='0x800040bd' and q['expected']==56 and p['fixed_note']==56<<16
 assert pub['metadata']=='0x800040bd' and a['candidate_at_acceptance']=='0x800040bd'
 return {'event':e,'generation':g,'publication_ms':pub['ms'],'acceptance_ms':a['ms'],'publication_backing':pub['backing'],'acceptance_backing':a['backing'],'context':q['word'],'input_note':q['note'],'output_note':p['fixed_note']>>16}
old=witness(fixed);early=witness(immediate)
replacement=next(x for x in fixed['events'] if x['kind']=='transition_commit_done')
assert old['publication_ms']<replacement['ms']<old['acceptance_ms']
assert old['publication_backing']!=old['acceptance_backing']
fixture=refresh['root_scale_fixture']
newbuilds=[x for x in refresh['cache_builds'] if x['track']==2]
assert newbuilds and all(x['backing']==fixture['old_backing'] and x['word']=='0x8000433b' for x in newbuilds)
newqs=[x for x in refresh['quantizer_calls'] if x['word']=='0x8000433b']
assert newqs
newpitches=[]
for q in newqs:
 p=next(x for x in refresh['pitch_outputs'] if x['event']==q['event'] and x['generation']==q['generation'] and x['ordinal']>q['ordinal'])
 assert p['fixed_note']>>16==q['expected'];newpitches.append({'input':q['note'],'output':p['fixed_note']>>16,'context':q['word'],'ms':q['ms']})
summary={'firmware_modified':False,'specific_cached_producer_gap_fixed_in_PC_prototype':True,'context_injected_at_acceptance':False,'old_queued_note':old,'native_replacement_ms':replacement['ms'],'no_delay_note':early,'fresh_setting_cache_builds':newbuilds,'fresh_setting_native_arp_outputs':newpitches,'helper_checks':helpers,'unchanged_firmware_sha256':fixed['firmware_sha256'],'physical_timing_verified':False,'new_overlay_loader_startup_verified':False,'limitations':['Root/scale bytes and queue timestamp delay are explicit PC fixtures. Native constructor, copying, publisher, eligibility, replacement, retention and pitch execute.','Runtime extension is installed in PC RAM after inherited loader-derived startup; changed helper copying through startup is not yet tested.','One naturally reached cached-emission route and two isolated copy ABI sites are covered, not exhaustive producer or concurrency coverage.','An attempted second panel handoff did not complete; it is not counted as a cache-refresh witness. Fresh settings use a separate successful native selection; repeated-slot refresh is checked in isolated producer-hook execution.']}
(out/'Digitone-cache-context-fix-summary.json').write_text(json.dumps(summary,indent=2))
lines=['# Digitone OS 1.42: cached queued-note context fix','',
'**The previously failing queued-arp case now passes in the PC prototype without acceptance-time metadata injection.** The device firmware is unchanged; physical timing and startup copying of the revised overlay remain unverified.','',
'The stock cached-note constructor uses explicit pattern `a3` and track `d4`. In the observed source-pattern selection, it builds track 2 at `0x419a30dc` from pattern backing `0x407c61e9`, root 61/raw scale 0. The earlier pool-only candidate store rejected that cache address. The revised exact-slot resolver admits precisely four 72-byte sequencer-cache slots and stores their captured context in the existing four-word sidecar at offset 2592.','',
'At `0x40093892`, the actual raw copy moves those 72 event bytes into the private allocated event. A machine-code wrapper carries the cache context alongside it before the stock timed publisher. The other raw-copy site at `0x4009344e` is also wrapped, including its displaced stack cleanup. Unknown sources resolve to zero rather than reading a later pattern.','',
'| Case | Context | Actual pitch | Result |','|---|---|---:|---|',
'| Previous natural crossing | 0 | 57 | Fails original scale |',
'| Fixed natural crossing | `0x800040bd` | 56 | Original scale retained |',
'| Fixed no-delay control | `0x800040bd` | 56 | Same capture before replacement |',
'| Separate fresh-pattern setting control | `0x8000433b` | Matches new-scale oracle | Different settings captured |','',
f"The delayed event `{old['event']}`, generation {old['generation']}, is published at {old['publication_ms']:.3f} ms, crosses completed native replacement at {replacement['ms']:.3f} ms and reaches eligibility/acceptance at {old['acceptance_ms']:.3f} ms. The same-generation context is present at publication, acceptance and native quantization. No event eligibility, identity or acceptance metadata is forged.",'',
f"In a separate control, actual native selection constructs the track-2 cache from root 59/raw scale 5. {len(newpitches)} native arp outputs carry that different word and match its scale oracle. Repeated-slot refresh is separately tested by executing the actual producer hook first with root 61/raw 0, then root 59/raw 5, on each track. An attempted second panel handoff did not complete and is not counted as a refresh witness; fresh eligible receiving-pattern notes in one uninterrupted transition remain a coverage target.",'',
'The isolated checks pass 291 cache-address boundary/alignment cases, four cache read/store/clear cases, five invalid-header cases, eight valid producer refresh cases and sixteen producer invalid-capture cases (bad root, bad scale, writer busy and capture fault across four tracks). Eight differential copy cases compare all data/address registers, status register, stack position and 72 event bytes against stock at both call sites. The three counted functional runs complete with helper/guard bytes intact and no unexpected guest writes to the reserved region.','',
'The new RAM overlay is 2,564 bytes, 240 bytes larger than the previous image, and fits below the owner pointer at offset 4096. It uses existing sidecar storage. The test deliberately installs the revision in PC RAM after the inherited startup snapshot. Passing it does not establish loader/copier continuity for this new revision, exhaustive cache mutation coverage, interrupt atomicity or physical deadlines.','',
'## Next step','',
'Connect this revised overlay and the two copy hooks to the PC bootstrap, repeat startup through playback, then repeat the cycle-aware timing controls with the added copy cost. Keep hardware flashing deferred until those checks and the remaining integration limits are addressed.']
(out/'Digitone-cache-context-fix-audit.md').write_text('\n'.join(lines)+'\n')
print('PASS natural crossing, no-delay, refreshed cache and helpers; reports saved')
