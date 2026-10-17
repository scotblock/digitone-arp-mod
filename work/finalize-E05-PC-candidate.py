from pathlib import Path
import json,hashlib,shutil
load=lambda name:json.loads(Path('outputs',name).read_text())
layout=load('Digitone-E05-PC-candidate-layout.json');startup=load('Digitone-E05-PC-startup-comparison.json');reset=load('Digitone-E05-PC-diagnostic-reset-controls.json');play=load('Digitone-E05-PC-playback-comparison.json');container=load('Digitone-E05-PC-container-verification.json');shutdown=load('Digitone-E05-shutdown-diagnostic-audit.json')
assert all(x['passed'] for x in [startup,reset,play,container])
assert len(startup['cases'])==5 and len(reset['cases'])==9 and len(play['cases'])==5
assert all(r['pattern_handoff']['completed'] for r in play['cases'])
scale=next(r for r in play['cases'] if r['image']=='E05_restored' and r['scenario']=='scale');assert scale['quantize'] and all(x['matches'] for x in scale['quantize']);changed=sum(x['note']!=x['actual'] for x in scale['quantize']);assert changed>0
source=Path(layout['candidate']);sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==layout['candidate_sha256']==container['sha256']
dest=Path('outputs/Digitone_OS1.44E05_SCALE_ARP_PC_ONLY.syx');shutil.copyfile(source,dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==sha
Path(str(dest)+'.sha256').write_text(sha+'  '+dest.name+'\n')
audio=load('Digitone-E05-PC-ordinary-audio-difference.json')
report={'candidate':str(dest.resolve()),'sha256':sha,'PC_only':True,'hardware_ready':False,'scope_completed':['Bounded shutdown/diagnostic entry audit and whole diagnostic refusal controls','One consolidated native-copied candidate with corrected ISA and input/reset/UI/deferred-release guards','Matched stock/candidate native startup and DSP playback comparisons'],'startup_cases':len(startup['cases']),'reset_refusal_cases':len(reset['cases']),'playback_cases':len(play['cases']),'scale_quantizer_checks':len(scale['quantize']),'changed_scale_pitches':changed,'all_pattern_handoffs_observed':True,'ordinary_comparisons':play['ordinary_comparisons'],'ordinary_audio_difference':audio,'firmware_container_verification':container,'unresolved':['Whole-application shutdown dispatcher and queued-worker exclusion at final global release','Diagnostic callers/return handling and unknown computed/interior reset bypasses','Exclusive ownership of the expanded reserved RAM range','Physical cache coherence, DMA contention and audio timing','Whether the corrected startup fixes the earlier physical-device logo hang'],'previous_firmware_preserved':True,'evidence':['Digitone-E05-shutdown-diagnostic-audit.json','Digitone-E05-PC-candidate-layout.json','Digitone-E05-PC-container-verification.json','Digitone-E05-PC-startup-comparison.json','Digitone-E05-PC-diagnostic-reset-controls.json','Digitone-E05-PC-playback-comparison.json','Digitone-E05-PC-ordinary-audio-difference.json']}
Path('outputs/Digitone-E05-PC-candidate-results.json').write_text(json.dumps(report,indent=2))
text=f'''# Digitone 1.44 E05 — PC-only candidate

File: `{dest.name}`

SHA-256: `{sha}`

Use this candidate in Digiemu only. Hardware readiness remains unproven. Stock 1.44 and E04 files were preserved. The device/version display still says 1.44; distinguish this build by its filename and checksum.

## What changed

E05 packages the corrected ColdFire startup stores, the tested live root/scale capture and atomic context copying, native storage initialization, cold/LIVE admission, input/release/sustain guards, UI/reset refusal and deferred release draining into one copied payload. Helpers previously supplied separately to PC RAM are relocated to `47be3800..47be46ee`; the unsupported diagnostic queue command returns at its outer entry before allocating or publishing any event. The copied payload is {layout['payload_bytes']:,} bytes and ends at `47be4804`.

Global parent destruction is not disabled. The shutdown audit supports a startup/global lifetime counter that stays at 94 through the observed queue lifecycle. Forced last-release tests show deletion at zero; full application shutdown dispatch and worker retirement at that boundary remain unproven.

## Completed comparisons

- Five native startup cases passed: stock and candidate with fresh/restored projects, plus candidate with its optional feature deliberately disabled. Every run reached the UI; candidate runs reached LIVE. Native copying supplied the added helper code; tests did not host-load those helpers. The disabled feature reached LIVE with READY=0.
- Nine stopped-state reset/diagnostic refusal controls passed, without event allocation/publication or changes to the monitored storage.
- Five matched DSP playback cases passed: stock/candidate with scale off and enabled, plus disabled-feature ordinary playback. Each delivered all input MIDI, produced nonzero audio without a DSP error or CPU halt, and completed the requested pattern replacement with sustained notes and subsequent fresh input.
- {len(scale['quantize'])} observed scale quantizer returns matched the independent oracle; {changed} returned a changed pitch. These are observed call counts, not exhaustive workload coverage.
- Transport packet checksums/sequence, container length/checksum/padding, compressed MAIN checksum and independent decompression passed. Non-MAIN sections match stock byte for byte.

## Ordinary playback comparison

'''
for r in play['ordinary_comparisons']:
 text+=f"- {r['image']}: pitch sequence identical to stock = {r['pitch_values_identical']}; audio byte exact = {r['audio_byte_exact']}; observed pitch calls {r['candidate_pitch_count']} versus stock {r['stock_pitch_count']}.\n"
if any(not r['audio_byte_exact'] or not r['pitch_values_identical'] for r in play['ordinary_comparisons']):text+='\nOrdinary playback equivalence is incomplete. The observed differences remain a limitation of this candidate; passing the per-run controls does not resolve their cause.\n'
text+=f"\nIn the stock-versus-enabled-candidate ordinary run, the first audio difference occurred at {audio['first_difference_seconds']:.4f} seconds; {100*audio['differing_sample_fraction']:.2f}% of interleaved samples differed over the take. This measurement does not establish the cause.\n"
text+='''
## Limits and use

These are PC tests with modeled clocks/peripherals, scoped ISA support and bootstrap/DSP shortcuts. Startup was exercised from decoded MAIN with loader-matching boot arguments, rather than a complete execution of the new physical updater/loader. They do not certify cache handoff, physical timing, DMA behavior, the enlarged RAM region or recovery from every exception. Diagnostic/test-mode entry is intentionally unsupported in this candidate. No hardware trial was performed, and this build is not certified to fix the earlier logo hang.

To test: add the E05 `.syx` to Digiemu as a separate firmware entry and build it with a fresh emulator session first. Keep the stock entry available. A subsequent test can use a copy of the saved project; do not overwrite the original session. Stop here before planning any physical installation.

## Evidence

'''
for name in report['evidence']:text+='- ['+name+']('+str(Path('outputs',name).resolve()).replace('\\','/')+')\n'
Path('outputs/Digitone_E05_PC_ONLY_README.md').write_text(text,encoding='utf-8')
print('CREATED',str(dest.resolve()),'SHA256',sha,'scale checks',len(scale['quantize']),'changed',changed)
print('Ordinary comparisons',play['ordinary_comparisons'])
