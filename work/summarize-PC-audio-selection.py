from pathlib import Path
import json,hashlib,re
r=json.loads(Path('outputs/Digitone-E04-PC-audio-selection-controls.json').read_text());menu=json.loads(Path('outputs/Digitone-E04-PC-audio-selection-menu-map.json').read_text());old=json.loads(Path('outputs/Digitone-E04-PC-reinitialization-policy-summary.json').read_text())['hashes'];cfg=json.loads(Path('work/os144/PC_ONLY-atomic-storage-layout.json').read_text())
checks={'fifteen_native_controls_pass':r['passed'] and len(r['cases'])==15,'eleven_recovered_callbacks_do_not_select_audio_slot':len(menu['callbacks'])==11 and not menu['audio_slot_selected_by_recovered_callbacks'],'original_images_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in old.items()),'raw_candidate_unchanged':hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes()).hexdigest()==cfg['main_sha256'] and hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes()).hexdigest()==cfg['payload_sha256'],'native_guard_not_installed':not r['native_guard_installed']}
assert all(checks.values());Path('outputs/Digitone-E04-PC-audio-selection-summary.json').write_text(json.dumps({'passed':True,'PC_only':True,'hardware_ready':False,'actual_audio_selection_caller_identified':False,'checks':checks},indent=2))
b=Path('work/os144/section-3.bin').read_bytes();strings=[]
for match in re.finditer(rb'[\x20-\x7e]{5,}',b):
 s=match.group().decode('ascii')
 if 0x401df000<=0x40000400+match.start()<0x401e2000 and ('AUDIO' in s.upper() or 'TEST' in s.upper()):strings.append({'address':hex(0x40000400+match.start()),'text':s})
Path('outputs/Digitone-E04-PC-audio-selection-diagnostic-strings.json').write_text(json.dumps({'scope':'diagnostic/string neighborhood, not command reachability proof','strings':strings},indent=2))
rows='\n'.join('| '+x['label']+' | `'+x['callback'][2:]+'` | `+'+x['child_offset'][2:]+'` |' for x in menu['callbacks'])
report='''# Audio-test page selection trace, stock 1.44

The page's construction and storage are traced, and all 11 recovered settings-menu callbacks execute in bounded PC fixtures. None selects its stored child slot. **An actual application request selecting AudioTestMenuView is still unidentified.** The PC helper controls do not invent such a request. Firmware containers and current raw candidate remain unchanged; no native guard is installed.

A concrete enforcement issue is now demonstrated: rejecting selection only in the page manager is too late to preserve the parent's selected-child reference. An earlier shared-helper refusal preserves that reference and its ownership counts in controlled native execution.

## Construction and recovered uses

Settings constructor `40072a7e` allocates 0x248 bytes and calls AudioTestMenuView constructor `400b2b5e` at `40072db8`. It adjusts the resulting object pointer by +38, builds the owning reference and assigns it to settings child **+2b4** through the call at `40072de0`. The assignment is prepared at `40072ddc`. Constructor uses name string `401e197a` ("AudioTestMenuView") and registers entry/exit callable targets `400b25bc` and `400b25c2`. Entry ultimately changes audio handling; exit invokes the setup path previously audited.

Stock MAIN reference scan recovers the constructor call, the name constant use and entry-callback registration. Inspection of aligned +2b4 displacement hits finds the settings initializer clear and the owning-reference assignment. The apparent +2b4 store at `400903e6` belongs to a different object/string table and is not a read selecting this stored child. Other hits include branch displacements, instruction immediates and data. This bounded scan does not exhaust computed addressing or aliases, so it does not prove the slot unread or the page unreachable.

## Settings menu, version-specific enumeration

Builder `400725f4` registers the following callbacks. All execute their own native child-reference copy and selector call in constructed fixtures; none reads settings +2b4.

| Action | Callback | Selected child |
|---|---|---|
'''+rows+'''

OUTBOX 8 is conditional in the builder (`40072998` skips its registration when the feature predicate is false). Its callback uses page helper `400e54a2`; the other ten use shared parent selection `400e47e6`. AUDIO ROUTING remains a distinct child at +294. These are actual recovered 1.44 callback targets, not addresses inferred from the earlier 1.42 audit. Native callback execution validates their instruction boundaries and selected offsets. Menu creation, button dispatch and feature-predicate execution are not included in these callback controls.

A diagnostic-string neighborhood scan also distinguishes ENTER/EXIT_TEST_MODE, audio data commands, test-status commands and START/ABORT_UI_TEST. It yields no direct named AudioTestMenuView selection command. String absence is not proof that no hidden or computed selector exists; ENTER_TEST_MODE installs a different handler route and must not be equated to this page entry.

## Selection mutation precedes manager admission

Shared helper `400e47e6(parent, child_ref)` executes:

1. `400e47fc -> 401774c0`: assign parent +84 to the requested child and release the previous owning reference.
2. Retain a temporary strong child reference.
3. `400e4820 -> 400e6352`: ask the manager at parent +64 to select it.
4. Release the temporary and propagate the manager's result.

Two negative controls supply an audio-page reference directly to this helper, then reject at the manager's previously tested boundary `400e637c`. Actual cleanup and false return complete with both uncontended and recursive locks. The manager's list, note state and pool/context hashes stay unchanged and the audio entry callback is not called. However, parent +84 now points to the rejected child: its strong count stays one above the starting value and the old child's count stays one below it. This is balanced ownership transfer but an inconsistent transaction result for the cold-start-only policy.

The ten settings action callbacks ignore the selector return value, then release their temporary reference and return. Native denied-selection controls show the same parent-reference mutation for those callbacks, while their audio-test slot stays unread. These controls use their own recovered ordinary child slots and controlled page objects, not an audio page planted into a normal UI action. The conditional OUTBOX callback takes a different helper path: its temporary cleanup balances and parent +84 remains unchanged in the tested denial.

## Earlier refusal candidate

Two controls stop the shared helper at **400e47f6**, before pushing assignment arguments or transferring selected ownership. The host supplies D0=0 and chooses the native restore/unlink/return tail at **400e483c**. This skips reading the uninitialized result local at `400e4838`. Stack, saved registers and interrupt control balance; selected reference, old/new strong counts, manager-list bytes, note state and pool/context hashes stay unchanged. This verifies a local early refusal continuation, not a machine-code guard or a real caller dispatch.

A guard placed here could prevent parent mutation for requests that actually use this helper, even if a caller ignores false. It still needs validated requested-page identity, object lifetime/concurrency assumptions, reporting behavior and coverage for selectors using the separate page-helper path. Do not add a fabricated normal-menu action or assume that an exit callback can veto removal.

## Result and bounded next work

Fifteen native controls pass: four audio-reference helper controls and eleven recovered menu callback controls. The actual audio-test selection caller remains unproven. The recovered normal menu is excluded as its direct selector within this builder/callback set; construction alone is not entry reachability.

The next targeted investigation is computed selection or state restoration that can consume the stored +2b4 reference, rather than more generic page-manager tests. For enforcement, retain the demonstrated early parent-helper boundary as a candidate and retain the independent cold-start/common-initializer protections: an unidentified UI selector is not proof that live reinitialization cannot occur. Pending-close policy, boot latch, RAM ownership and physical timing/cache behavior remain outside this task.

Evidence: `Digitone-E04-PC-audio-selection-reference-scan.json`, `Digitone-E04-PC-audio-selection-menu-map.json`, `Digitone-E04-PC-audio-selection-controls.json`, `Digitone-E04-PC-audio-selection-summary.json`, `Digitone-E04-PC-audio-selection-diagnostic-strings.json`.
Reproduce with `work/scan-PC-audio-selection.py`, `work/map-PC-audio-selection-menu.py`, `work/test-PC-audio-selection-controls.py`.
'''
Path('outputs/Digitone-E04-PC-audio-selection-review.md').write_text(report)
with Path('outputs/Digitone-E04-hardware-startup-incident.md').open('a') as f:f.write('\n\n## Twenty-first follow-up: audio-test selection trace\n\nStock 1.44 constructs AudioTestMenuView at settings +2b4, but none of the eleven recovered settings callbacks reads/selects it. Fifteen native PC controls pass. Manager-only denial leaves parent selection changed; a host-selected earlier refusal before the shared-helper assignment preserves it. Actual application selector remains unidentified. No guard installed and firmware/raw candidate hashes unchanged. See `Digitone-E04-PC-audio-selection-review.md`.\n')
print('PASS fifteen native controls, menu enumeration and unchanged-image checks; actual audio selector remains unidentified')
