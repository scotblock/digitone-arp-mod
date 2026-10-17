from pathlib import Path
import json,hashlib
cfg=json.loads(Path('work/os144/PC_ONLY-live-storage-layout.json').read_text());reset=json.loads(Path('outputs/Digitone-E04-PC-live-storage-reset.json').read_text());startup=json.loads(Path('outputs/Digitone-E04-PC-live-storage-startup.json').read_text());play=json.loads(Path('outputs/Digitone-E04-PC-live-storage-playback.json').read_text());c=play['cases'][0]
checks={
 'strict_added_instruction_layout_passes':reset['strict_static_checks'],
 '33_initializer_failure_contracts_pass':reset['passed'] and len(reset['cases'])==33,
 'actual_copier_copies_live_and_reset_code':all(reset['cold_copier'].values()),
 'repeated_reinitialization_clears_storage':reset['three_reinitializations_clear_extra_storage'],
 'four_loader_derived_startups_pass':startup['passed'] and len(startup['cases'])==4 and all(x['passed'] for x in startup['cases']),
 'inherited_loader_state_preserved':all(x['loader_handoff']['state_preserved_by_overlay'] for x in startup['cases']),
 'new_storage_cleared_before_stock_initializer':all(x['extra_storage_zero_before_stock'] for x in startup['cases']),
 'cold_completion_uses_guest_timer_interrupts':all(x['completion_kicks']==0 and x['timer_fired']['1']>=3 for x in startup['cases']),
 'intro_uses_actual_DSP_model':all(x['DSP_model']=='DspCpu' for x in startup['cases']),
 'playback_passes':play['passed'],
 'no_poststartup_host_code_or_storage_seed':c['live_code_copied_by_startup'] and c['extra_storage_initialized_by_guest'],
 'all_live_captures_match':all(x['matches'] and x['index_owner_matches'] for x in c['live_captures']),
 'old_and_new_pattern_sources_reached':set(x['pattern'] for x in c['live_captures'])=={'0x407fd414','0x40813531'},
 'all_live_copies_match':all(x['matches'] and x['bytes_match'] for x in c['live_copies']),
 'pattern_handoff_really_completed':any(x['completed'] for x in c['actual_pattern_changes']),
 'old_context_survives_completed_publication':any(x['pattern']=='0x40813531' and x['word']=='0x800000be' and x['note'] in [64,67] for x in c['quantizer_owners']),
 'fresh_note_uses_new_context':any(x['word']=='0x80000341' for x in c['quantizer_owners']),
 'all_pitch_results_match_without_zero_context':all(x['matches'] and x['word']!='0x0' for x in c['quantize']),
 'DSP_and_application_continue_without_error':c['halted'] is None and c['DSP_after']['error'] is None and c['DSP_after']['booted'] and c['audio_nonzero_bytes']>0,
}
prior=json.loads(Path('outputs/Digitone-E04-PC-live-capture-summary.json').read_text())['hashes'];hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in prior};checks['original_images_preserved']=hashes==prior
out={'PC_only':True,'flashable_firmware_created':False,'checks':checks,'passed':all(checks.values()),'layout':cfg,'hashes':hashes,'pitch_count':len(c['quantize'])};Path('outputs/Digitone-E04-PC-live-storage-summary.json').write_text(json.dumps(out,indent=2));assert out['passed'],[k for k,v in checks.items() if not v]
report=f'''# Live-context storage integrated into PC startup/reset

The added descriptor words and pending input records now initialize through guest startup and the stock pool-initializer hook. Playback no longer seeds this code or clears this storage separately from startup. This is a separate raw PC candidate; E04 and stock update files remain unchanged.

## Implementation

The raw test MAIN redirects the existing initializer entry at `400ffed0` to a new 304-byte guarded fallback at `47be3400`. It retains the 474-byte live capture/bind/copy helpers at `47be3000` and their four caller hooks. The early copier copies an expanded 13,616-byte resident image from `4029c5b0` into reserved PC RAM before the displaced stock continuation; this image includes padding and zeroed storage. No firmware container or new flashable update is built.

The startup compatibility header remains unchanged. On a valid 158-entry pool initialization, the fallback marks ready zero, clears the existing context area, then clears all 2,080 added bytes at `47be2000` (descriptor words plus pending input records). It calls the full stock initializer, verifies the header/pointer again, then publishes ready one. Every subsequent entry through this same hooked initializer repeats the clear. Invalid argument/header/pointer disables the helper pointer and still runs the stock continuation. Post-initializer corruption also disables the pointer. No invalid-setup path publishes ready.

Pattern changes do not clear this descriptor storage: old queued/held note contexts must remain available until their corresponding descriptors are reused. This change follows the pool-initializer lifetime, not every pattern selection. It does not add a new global application shutdown mechanism.

## Verification

- Strict ColdFire instruction checks cover the new fallback, live helpers and actual copier.
- 33 isolated full stock-initializer cases pass across valid/unready setup, invalid argument/header/pointer and changes during initialization. Original pool writes/return, saved registers, full status and balanced stack match their controls. The added clear stays inside its bounds; invalid preconditions leave its poisoned test storage untouched while disabling access.
- The actual copier transfers both code bodies and zeroes the added storage with ready still zero. Three successive real initializer calls each erase freshly poisoned added storage without a test-time clear.
- Four loader-derived cold/intro runs reach the UI: factory/default project, restored project, invalid pre-initializer pointer and post-initializer header corruption. Loader registers/control state/stack are preserved when applying the raw test MAIN. The original E04 loader handoff is used; the larger raw MAIN is overlaid after that handoff. Native guest timer interrupts provide cold completion, with no host semaphore kick.
- Playback restores the new startup checkpoint and verifies the live-code bytes and initially zero storage before use. It performs no extra live-code copy, sidecar clear or hook installation. ISA execution support is still installed in the emulator.
- The guest session again captures old pattern root 62/raw scale 0 and fresh pattern root 65/raw scale 5. Old E/G pitch calls retain the old context after an observed active-pointer change; fresh F uses the new context. All {len(c['quantize'])} pitch results match the oracle with no zero-context calls. Actual DSP execution produces audio without an emulated halt or DSP error.

{len(checks)} summary checks pass. Evidence: `Digitone-E04-PC-live-storage-reset.json`, `Digitone-E04-PC-live-storage-startup.json`, `Digitone-E04-PC-live-storage-playback.json`, and `Digitone-E04-PC-live-storage-summary.json`. Raw candidate/layout are under `work/os144/PC_ONLY-live-storage-*`; scripts are under `work`.

## Remaining limits

Repeated initializer calls are tested from a captured state; a full native UI-driven factory reset or project-load/reset workload has not been newly exercised. Arbitrary in-flight input/copy interleavings remain unproven. Exceptions, bus faults and a stock initializer that never returns are not recovered by this fallback. Alternate cached selector branches and allocation exhaustion still need focused execution coverage.

Startup continuity is joined across cold/intro/playback snapshots, with existing peripheral/scheduling models and decompression shortcuts. This is not a test of a newly packaged larger container through the loader. The padded raw test image does not establish a final packed installation layout or its loader/update bounds. The required code bytes reach the guest copier intact in these PC runs; subsequent source-memory preservation is not separately certified.

Physical RAM ownership, cache coherence, timing and the original hardware startup failure remain unresolved. No new hardware trial is implied. The next focused integration check is source/descriptor-copy serialization with outstanding input and reset, before packaging or broader readiness claims.
'''
Path('outputs/Digitone-E04-PC-live-storage-startup-review.md').write_text(report)
incident=Path('outputs/Digitone-E04-hardware-startup-incident.md');entry='\nFifteenth follow-up completed on 9 October: `Digitone-E04-PC-live-storage-startup-review.md` connects added live-context code/storage to a separate raw PC startup candidate and guarded stock-initializer reset. 33 reset/failure cases, repeated poison/reset, four loader-derived cold/intro controls and startup-derived playback pass. The larger padded raw source is overlaid after the original loader handoff, not loaded from a new packaged container. No poststartup code or sidecar seed is required. Source/copy interleavings, native UI reset coverage and physical RAM/cache/timing remain unproven; original firmware is unchanged.\n'
if entry.strip() not in incident.read_text():
 with incident.open('a',encoding='utf-8') as f:f.write(entry)
print('PASS',len(checks),'summary checks; startup-derived playback',len(c['quantize']),'pitch calls')
