from pathlib import Path
import json,hashlib
r=json.loads(Path('outputs/Digitone-E04-PC-computed-selection-controls.json').read_text());refs=json.loads(Path('outputs/Digitone-E04-PC-computed-selection-refs.json').read_text());old=json.loads(Path('outputs/Digitone-E04-PC-reinitialization-policy-summary.json').read_text())['hashes'];cfg=json.loads(Path('work/os144/PC_ONLY-atomic-storage-layout.json').read_text());checks={'four_bounded_native_controls_pass':r['passed'] and len(r['cases'])==4,'original_images_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in old.items()),'raw_candidate_unchanged':hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes()).hexdigest()==cfg['main_sha256'] and hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes()).hexdigest()==cfg['payload_sha256'],'no_native_guard_installed':not r['native_guard_installed']};assert all(checks.values())
Path('outputs/Digitone-E04-PC-computed-selection-summary.json').write_text(json.dumps({'PC_only':True,'bounded_controls_pass':True,'checks':checks,'full_restored_entry_verified':False,'initial_audio_selection_identified':False,'hardware_ready':False,'shared_helper_direct_call_candidates':len(refs['targets']['0x400e47e6']['calls']),'full_entry_probe':'Digitone-E04-PC-retained-audio-entry-probe.json'},indent=2))
report='''# Computed selection and retained UI state, stock 1.44

A concrete retained-child restore route is identified and exercised through native PC save, selected-reference clear, restore and denied-manager cleanup. It bypasses the previously tested shared selected-child helper. Four bounded controls pass, including ordinary and recursive locks. The initial request that puts AudioTestMenuView into selected state is still unidentified. Full restored audio-page entry has not passed: a separate probe stops in rendering because the constructed page lacks required initialization. No native enforcement is installed; firmware containers and the current raw candidate are unchanged (hash checked).

## Retained UI reference route

This is an in-memory page lifetime mechanism, not demonstrated project-file deserialization or a cold-start pointer restore.

- Generic parent constructor `400e42c0` explicitly clears selected references +84/+88 and retained references +8c/+90. Settings construction also initializes the child slots and builds the audio-test child at +2b4.
- Parent close `400e4ec2` copies selected child +84 into retained child **+8c** using `401774c0` at `400e4ed6`, asks the child to close through virtual +28 at `400e4ee8`, then asks the parent subobject to close. It does not require looking up settings +2b4 at that point.
- Closure `400e4848`, registered by generic child wrapping `400e43fc` at `400e445a..400e4470`, clears the parent's selected owning reference through native move-assignment/cleanup `40158b82`. Retained +8c survives this clear. The sibling closure `400e487e` also clears selected state.
- Parent entry/restore **400e4e1e** dispatches parent entry callbacks first through `400e562a`. If +8c is nonzero, it assigns +8c to selected +84 at `400e4e50`, clears/releases +8c through `40158b82`, retains a temporary, and calls manager **400e6352 directly at 400e4ea0**. It releases the temporary and returns without testing a refusal result.

The recovered settings root vtable `401a3494` includes parent close `400e4ec2` at +80 and parent entry `400e4e1e` at +84. Its page subobject table `401a3530` includes thunks `400e4efe` (close) and `400e4eb8` (entry), each adjusting the subobject pointer by -38 before the corresponding parent operation. These registered virtual routes explain how retained state can bypass an explicit menu action and the shared helper; they do not prove a user input or boot state originally selected the audio child.

## Native sequence controls

For each mutex state, the initial selected audio reference and object/list/task state are controlled fixtures. After that initial seed, the save operation is guest-produced:

1. Execute stock parent close: selected reference is copied to retained +8c and its strong count increases.
2. Invoke the actual registered clear-closure target directly: selected +84 becomes zero and its owning count decreases, while retained +8c remains.
3. Execute stock parent restore until the actual manager admission boundary.
4. Supply the previously tested manager false continuation and execute native temporary release, unlock and return.

The trace never enters `400e47e6`. Temporary ownership, registers, stack, incoming interrupt control and normal/recursive mutex accounting balance. Watched note state and full tested pool/context hashes remain unchanged. **Nevertheless, manager denial leaves +84 pointing to the restored child and +8c empty.** Thus guarding only the shared helper, or only the manager after transfer, does not preserve the restore transaction.

Calling the clear target directly does not certify callback-dispatch ordering or reachability. Actual parent/page removal and live scheduler interleavings are not executed in this save/clear/restore fixture.

## Local restore defer boundary

Two controls defer at **400e4e42**, before the retained-reference transfer, following the native restore/return tail at **400e4eae**. Selected and retained references and strong counts stay unchanged; registers, stack and interrupt control balance. The host chooses this path; no guard instructions are installed.

This is a local defer point, not a verified veto of the whole parent transition. The parent entry callback dispatcher has already run before 400e4e42. These fixtures contain an empty parent callback list, so they do not establish that earlier entry callbacks, outer page publication or a caller's ignored return are harmless. A full policy must admit/reject restore before those earlier mutations or explicitly define a consistent parent-with-deferred-child result. The stock function has no established failure-status contract for such a new policy.

## Computed source audit scope

MAIN scan recovers 38 aligned direct/relative candidates calling `400e47e6`, plus the clear callback registration above and the settings constructor call from `40041056`. Backward source windows show fixed child-slot callbacks and dynamically constructed reference wrappers; they are triage windows, not a complete dataflow proof. The settings-specific callback enumeration from the preceding task still selects no +2b4 child.

The useful new route is retained +8c: once a page is selected, subsequent restore need not read its original child slot at all. That explains why searching only literal +2b4 reads cannot establish complete coverage. It does not prove that the audio child is initially selected by a computed factory, project restore, normal settings input or another recovered direct caller. All computed aliases remain unexhausted.

## Full-entry probe limitation

A positive probe constructs an unlinked retained audio page and lets the manager proceed beyond admission without a rejection. It stops at **400e4fcc**, reading the menu renderer's string/header through root +94, with `UC_ERR_MAP`. The synthetic page lacks the complete constructor/renderer state required at that point. It does not reach audio-entry callback `400b25bc`.

This is an incomplete test fixture, not a demonstrated stock or modified firmware failure. The probe is recorded separately as unsuccessful; it is not included in the four passing controls. No claim of complete restored-page playback or on-device behavior follows.

## Concrete result and next task

The retained-state route is real native code and exposes another pre-mutation protection requirement: restore admission must cover the direct manager call from parent re-entry, not just explicit child selection. A balanced local defer tail is tested, but whole parent-transition rejection is unproven.

Next, construct the audio page using its actual stock constructor and repeat retained-page restore through callback entry. That should resolve the renderer fixture gap and show the real parent/child callback ordering. The initial audio selection request remains a separate, narrower reachability question; do not fabricate one by planting the audio child into an ordinary menu slot. The cold-start/common initializer invariants, native latch placement, pending-close handling, physical RAM/cache/timing and hardware readiness remain unresolved.

Evidence: `Digitone-E04-PC-computed-selection-controls.json`, `Digitone-E04-PC-computed-selection-summary.json`, `Digitone-E04-PC-computed-selection-refs.json`, `Digitone-E04-PC-computed-selection-source-windows.json`, and unsuccessful `Digitone-E04-PC-retained-audio-entry-probe.json`.
Reproduction: `work/test-PC-computed-selection-controls.py`; unsuccessful probe: `work/probe-PC-retained-audio-entry.py`.
'''
Path('outputs/Digitone-E04-PC-computed-selection-review.md').write_text(report)
with Path('outputs/Digitone-E04-hardware-startup-incident.md').open('a') as f:f.write('\n\n## Twenty-second follow-up: retained-child restore bypass\n\nNative parent close saves selected child at +8c; closure clears +84; re-entry restores +8c and calls manager directly, bypassing shared helper. Four bounded PC controls pass. Manager refusal consumes retained reference and leaves selected restored; local earlier defer preserves both but follows parent entry callbacks. Full-entry probe stops in incomplete synthetic renderer at 400e4fcc, not evidence of a firmware fault. Initial audio selection remains unidentified. No guard installed, firmware/raw candidate hashes unchanged. See `Digitone-E04-PC-computed-selection-review.md`.\n')
print('PASS four bounded controls and unchanged images; full entry probe remains unverified')
