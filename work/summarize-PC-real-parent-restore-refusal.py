from pathlib import Path
import json,hashlib
r=json.loads(Path('outputs/Digitone-E04-PC-real-parent-restore-refusal.json').read_text());old=json.loads(Path('outputs/Digitone-E04-PC-reinitialization-policy-summary.json').read_text())['hashes'];cfg=json.loads(Path('work/os144/PC_ONLY-atomic-storage-layout.json').read_text());checks={'four_refusal_controls_pass':r['passed'] and len(r['cases'])==4,'actual_parent_callback_observed':all(x['parent_entry_callbacks']==['0x400e47ae'] for x in r['cases']),'before_callback_refusal_keeps_registry':all(x['registry_before']==x['registry_after'] for x in r['cases'] if x['when']=='before_parent_callbacks'),'post_callback_refusal_runs_registry_writer':all(len(x['parent_registry_callback_executions'])==1 for x in r['cases'] if x['when'].startswith('after_')),'images_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in old.items()),'raw_candidate_unchanged':hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes()).hexdigest()==cfg['main_sha256'] and hashlib.sha256(Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes()).hexdigest()==cfg['payload_sha256'],'native_guard_uninstalled':not r['native_guard_installed']};assert all(checks.values())
Path('outputs/Digitone-E04-PC-real-parent-restore-refusal-summary.json').write_text(json.dumps({'PC_only':True,'passed':True,'checks':checks,'whole_parent_transaction_rejection_proven':False,'hardware_ready':False},indent=2))
Path('outputs/Digitone-E04-PC-settings-constructor-probe.json').write_text(json.dumps({'PC_only':True,'full_constructor_completed':False,'constructor':'0x40072a7e','last_PC':'0x400634ec','exception':'Invalid memory mapping (UC_ERR_MAP)','instruction_context':'virtual-base offset read through application dependency returned by 40149fba','classification':'captured PC application dependency not fully initialized; not evidence of a firmware defect','base_parent_prefix_successfully_executed_separately':True},indent=2))
report='''# Retained-child refusal with actual parent entry callbacks

Four native PC controls pass using a fully stock-constructed audio child and actual parent entry records from the settings constructor's base-parent prefix. Refusal before callbacks preserves both child ownership and the application active-page registry. Refusal after callbacks preserves child ownership but leaves the parent registered as active. Firmware containers and current raw PC candidate are unchanged (hash checked); no native guard is installed.

## Construction scope

Full audio constructor `400b2b5e` executes with actual heap allocation. Settings constructor `40072a7e` executes from its entry through **40072ac4**, immediately after its base-parent construction returns. The parent callback vector is therefore guest-created by `400e42c0`, not an empty vector or supplied callback record. This prefix registers entry target **400e47ae** and the corresponding exit target **400e47ca**.

Full settings construction was attempted separately. It stops at `400634ec` reading a virtual-base offset through an application dependency supplied by `40149fba`; the PC snapshot lacks that dependency's required initialized object state. This is recorded as an unsuccessful fixture probe, not a stock firmware fault. The refusal controls do not claim a fully constructed settings menu, nor exhaust callbacks that might be added by computed paths later in complete construction.

The test wraps the real audio page using stock `400e43fc` and assigns it to retained +8c with actual shared-reference assignment. Initial retained state and manager/current-task state are controlled conditions. The initialized application's active-page registry is obtained through actual singleton `4014a060`, rather than replacing the callback's target. Queued notes are produced before the tested entry path.

## Actual callback effect

Entry handler `400e4e1e` invokes parent callback dispatcher `400e562a` before checking retained +8c. That dispatcher clears parent close flag +30, binds manager pointer +2c and marks the page active through `400e539e`. It dispatches the actual registered **400e47ae** callable.

That target gets the application with `4014a060` and tail-calls **400aedc2**. The latter appends the parent page/subobject pointer to the active-page vector at application +198/+19c/+1a0. Both post-callback controls observe exactly that append. The callback is not an input shutdown or note-ownership drain; watched gates, queued notes, pool and context remain unchanged.

## Refusal controls

| Refusal point | Child ownership | Parent/registry result |
|---|---|---|
| **400e4e2e**, after local prologue but before callback arguments are pushed | Selected and retained references/counts preserved | No entry callback executes; parent page bytes and registry preserved |
| **400e4e42**, after callback dispatch but before retained transfer | Selected and retained references/counts preserved | Parent becomes active/bound and is appended to the application registry |

The host selects the restore/return tail **400e4eae** in both cases. Its native register restoration, stack cleanup and return execute. Each point passes with uncontended and already-recursive manager state; the test does not acquire that manager mutex on these refusal paths, and its incoming ownership/recursion stays unchanged. No interrupt-control drift, child audio-entry execution or audio-vector change is observed. Note gates, queued note state, pool/context hashes and owning reference bytes/counts remain unchanged.

The earlier point is before any tested parent entry side effects, but it is **not a verified whole outer transaction abort**. An outer manager can have published a parent node or changed selection before invoking this handler. The handler is a void entry callback with no established failure result for its outer caller. Jumping to the tail by itself cannot roll back that publication or notify the caller.

The later point may implement a deliberate deferred-child state: parent entry completes, retained child stays pending, and audio-test entry is withheld. Such a policy must define consistent parent selection/UI state and subsequent retry or close behavior. It cannot be described as refusing the parent operation, because active-page registry mutation has already happened.

## Result and next concrete check

The previously empty parent-callback gap is narrowed: native base-parent callback registration and execution now show the real active-page registry write. This rules out treating the post-callback refusal as preserving the whole parent transition.

Next, trace the outer manager's parent publication and callback contract to choose between an earlier whole-operation veto and an explicitly defined deferred-child outcome. Keep both candidate local continuations unimplemented until that caller contract is established. A complete settings-construction dependency gap remains, alongside the separate initial audio-selection request, native boot latch, pending-close policy and hardware RAM/cache/timing validation.

Evidence: `Digitone-E04-PC-real-parent-restore-refusal.json`, `Digitone-E04-PC-real-parent-restore-refusal-summary.json`, and unsuccessful `Digitone-E04-PC-settings-constructor-probe.json`.
Reproduce: `work/test-PC-real-parent-restore-refusal.py`; constructor probe: `work/probe-PC-stock-settings-parent.py`.
'''
Path('outputs/Digitone-E04-PC-real-parent-restore-refusal-review.md').write_text(report)
with Path('outputs/Digitone-E04-hardware-startup-incident.md').open('a') as f:f.write('\n\n## Twenty-fourth follow-up: parent callbacks and restore refusal\n\nFour PC controls pass with stock audio child and real settings base-parent construction prefix. Entry callback 400e47ae registers parent in active-page vector; refusal before callbacks preserves it, refusal after callbacks leaves registry mutation while preserving retained child. Full settings constructor hits a missing initialized application dependency at 400634ec; separately recorded as fixture gap. Outer parent publication/void callback contract remains unverified. Native guard uninstalled and firmware/raw candidate unchanged. See `Digitone-E04-PC-real-parent-restore-refusal-review.md`.\n')
print('PASS four refusal controls and unchanged-image checks; parent callback side effect documented')
