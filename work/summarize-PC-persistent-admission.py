from pathlib import Path
import json,hashlib
root=Path.cwd()
a=json.loads(Path('outputs/Digitone-E04-PC-persistent-admission.json').read_text())
r=json.loads(Path('outputs/Digitone-E04-PC-persistent-admission-routes.json').read_text())
l=json.loads(Path('outputs/Digitone-E04-PC-persistent-admission-lifecycle.json').read_text())
assert a['passed'] and r['passed'] and l['passed']
expected=json.loads(Path('outputs/Digitone-E04-PC-reinitialization-policy-summary.json').read_text())['hashes']
cfg=json.loads(Path('work/os144/PC_ONLY-atomic-storage-layout.json').read_text())
expected.update({'work/os144/PC_ONLY-atomic-storage-main.bin':cfg['main_sha256'],'work/os144/PC_ONLY-atomic-storage-payload.bin':cfg['payload_sha256']})
old_ui=json.loads(Path('work/os144/PC_ONLY-ui-defer-overlay.json').read_text())
expected['work/os144/PC_ONLY-ui-defer-overlay.bin']=old_ui['sha256']
hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in expected}
assert hashes==expected
summary={'PC_only':True,'passed':True,'helper_cases':len(a['helper_cases']),'reset_cases':len(a['reset_cases']),'route_cases':len(r['cases']),'lifecycle_runs':len(l['cases']),'lifecycle_cycles':sum(x['cycles'] for x in l['cases']),'hardware_ready':False,'startup_integrated':False,'physical_exclusive_storage_ownership':False,'existing_artifacts_unchanged':True,'hashes':hashes}
Path('outputs/Digitone-E04-PC-persistent-admission-summary.json').write_text(json.dumps(summary,indent=2))
text='''# Persistent admission and storage lifetime: PC review

A separate 332-byte native overlay now reads a persistent candidate admission word instead of the previous compiled live constant. All tests pass: 30 helper controls, 20 native reset/failure controls, 36 UI-route controls and two lifecycle runs covering six close/re-entry cycles and final owner releases. Firmware, the existing raw candidate and the previous UI overlay remain unchanged; their hashes were checked.

The helper consumes exact COLD once, producing INITIALIZING. Completion can move INITIALIZING to LIVE or FAILED once; duplicate claim/completion is denied. Zero, poison and a tested one-bit corruption never authorize a cold claim. Every observed transition writes one aligned longword under interrupt level 7, with incoming SR, stack and non-result registers restored. All custom instructions pass the existing ISA_C/MOVE audit. This is an instruction-model result, not measured interrupt/cache behavior.

Both UI guards read the guest RAM word themselves. In LIVE, INITIALIZING, FAILED or the tested unknown states, retained audio-test entry is deferred before reference transfer, and explicit audio-test selection is refused before selected assignment. Ordinary and null controls retain their previous behavior. Exact COLD is a stock-pass-through comparison control; this does not authorize arbitrary cold diagnostic setup. Initial state and completion-success arguments are still supplied by fixtures. No initializer-entry or whole-command guard has been installed.

## Storage extent and observed lifetime

Candidate word: `47be2840..47be2843`. Known old context clearing ends at `47be1b74`; the descriptor/pending clear is `47be2000..47be281f`. The candidate is outside both clears and before live helper code at `47be3000`. It occupies existing payload padding, which does not establish exclusive hardware ownership.

Global native write tracing around 20 actual initializer/fallback executions found no write overlapping the word, including writes that might start before it. INITIALIZING, LIVE, FAILED and zero were preserved with valid setup, READY cleared, bad metadata magic, null owner pointer and wrong setup argument. Neighbour canaries were preserved. These calls deliberately execute the initializer to test storage; the overlay does not prevent those calls.

The persistent LIVE value also survives the tested native parent entry, defer, close, full exit-callback dispatch, removal, re-entry and final parent/audio destruction. Reference counts, registry/list cleanup and note context continue to satisfy the earlier controls.

## Startup ordering requirement

The actual early copier overwrites this word with zero from the existing payload. Embedded source and payload both contain zero here. Recopy therefore loses LIVE but never regrants COLD; its resulting state denies admission. Persistence is established for tested warm reset/UI paths, not across the copier or power loss.

A future bootstrap must establish COLD only after the final initial copy and consume it before mutation. There is deliberately no callable helper that resets the word to COLD. The native cold-seed location, proof of fresh-boot provenance, actual startup completion/normal-mode decision, command cleanup/abort boundaries and physical RAM/cache ownership remain unresolved. An arbitrary writer reproducing the exact COLD constant would defeat this single-word design; bounded tests are not a global alias proof.

The next focused step is to identify the unique post-copy cold bootstrap boundary and its completion/failure continuations, then connect the admission helpers in a separate PC startup overlay. Do not install this overlay on a device.
'''
Path('outputs/Digitone-E04-PC-persistent-admission-review.md').write_text(text)
incident=Path('outputs/Digitone-E04-hardware-startup-incident.md')
marker='## Twenty-eighth follow-up: persistent admission candidate'
if marker not in incident.read_text():
 incident.write_text(incident.read_text()+'\n\n'+marker+'\n\nSeparate native PC overlay replaces compiled live controls with persistent state reads. Thirty state/ABI controls, twenty actual reset/failure controls, thirty-six UI-route controls and six native lifecycle cycles pass. Candidate 47be2840 is preserved by observed warm resets/UI destruction but overwritten with zero by the early copier; zero denies and never rearms COLD. Trusted post-copy cold seeding, startup completion provenance, native initializer/whole-command admission and physical ownership remain unimplemented/unproven. Existing firmware/raw candidate/old UI blob hashes unchanged. See `Digitone-E04-PC-persistent-admission-review.md`.\n')
policy=Path('outputs/Digitone-E04-PC-reinitialization-protection-policy.md')
marker='## Persistent admission PC candidate'
if marker not in policy.read_text():
 policy.write_text(policy.read_text()+'\n\n'+marker+'\n\nThe disposable persistent overlay tests single-use COLD -> INITIALIZING -> LIVE/FAILED and native UI guards reading candidate word 47be2840. Zero/unknown values deny. Known warm resets and tested parent lifetime preserve it; the actual early copier sets it to zero, so trusted cold seeding must occur after copying. Startup integration, native initializer/command admission and global/physical storage certification remain pending. See `Digitone-E04-PC-persistent-admission-review.md`.\n')
print(json.dumps(summary,indent=2))
