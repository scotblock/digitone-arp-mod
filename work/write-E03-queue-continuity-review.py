from pathlib import Path
import json,hashlib
p=Path('outputs/Digitone-OS1.44E03-continuous-queue-action-checks.json');r=json.loads(p.read_text());assert r['passed'] and len(r['cases'])==5
paths={
'inputs/Digitone_and_Digitone_Keys_OS1.44.syx':'d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659',
'outputs/Digitone_OS1.44E02_SCALE_ARP_DIGIEMU_ONLY.syx':'8e1d9c4e384d30314255801d0e1ef70736a1f76ac1279a31f8e02d3285fe43ef',
'outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx':'8775320f161cb02efa8f51b2671034baf73eeec95f4bb66ffc20a29e9b0a2a3d'}
for path,digest in paths.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
r['firmware_files_unchanged']=paths
r['limits']=['One persistent Machine per case; packet arrival and application/dialog task execution are scheduled explicitly by the PC harness. This is not a full kernel or real-time peripheral run.','Tests enter the stock dispatcher with complete framed SysEx messages; USB/UART ingress is not executed here.','Application consumer starts at recovered loop boundary 40019ccc with task stack/register fixtures. Kernel queue instructions execute; empty-queue waits and thread scheduling do not.','UI registry entry selection, heap backing, strings/rendering, project save, mutex/wakeup/thread operations, hardware identity/geometry/factory state and flash are fixtures. The stock parent-view lookup, dynamic cast, shared ownership, callback managers, work-deque operations and worker instructions execute.','Success stops at programming-complete boundary 40100504, before reset. Failure stops at the error callback entry after real queue delivery. Physical flash failures/cache/timing are not validated.','The receiving path executes stock OS 1.44, receiving E03; this audit does not execute all E03 startup/arp hooks.']
r['local_provider_confirmation_finding']='Stock provider vtable 401c8f08: +0c -> 401742e4 returns false, +14 -> 401742ea returns true. Completion routes directly to 400c98da and queues action 400c9536; no separate Yes/No interaction occurs along this tested local route.'
p.write_text(json.dumps(r,indent=2))
report='''# E03 queue-to-update action continuity

The bounded PC continuity test passes all five cases. No firmware file was changed, rebuilt, transferred or flashed. This extends the earlier receiving-path audit; hardware readiness remains unestablished.

## Joined path

For each case, one persistent stock OS 1.44 machine receives the E03 framed stream at manufacturer/device dispatcher `400eaac8`. Receiver `400e9fcc` now uses the actual enqueue routine `40001cda`, initialized by stock queue constructor `40001c78`, on application queue `4052b6bc`. No host notification collector replaces enqueue/dequeue.

After each packet, the actual consumer loop from `40019ccc` dequeues via `40001d6c`, switches on message type and resolves the active update view. Its type-12 completion branch calls `400c9cca`. The UI registry is supplied, but dynamic casting, reference ownership and parent-view lookup `400e61cc` execute as stock instructions. The local provider routes completion into `400c98da`.

That builder creates action `400c9536`, with callback manager `400c93aa`, plus result action `400c9c6a` and manager `400c94b4`. The actual function copies/destructors and work-deque insertion through `400a87f0` execute. Temporary callback objects are destroyed; the retained heap context remains valid. The harness then overwrites the caller stack frames and schedules the actual worker entry `400a8690`. Its callback-copy/invocation path reaches `400c9536`, which obtains the stock completed buffer and runs checksum/compatibility validation. The valid case reaches updater `40100440`, stopping at programming-complete `40100504`.

## Correction: this local route does not have a separate Yes/No confirmation

The stock local-provider vtable is `401c8f08`. Its `+0c` method `401742e4` returns false and its `+14` method `401742ea` returns true. The executed type-12 branch consequently enters the preparation/work path directly. The title at `401e2632` is "OS Upgrade", not a confirmation question. What earlier discussion called the confirmation callback is the queued received-image action on this route. The test does not manufacture a button press or assert that another provider/route behaves identically.

## Results

| Case | Observed result |
|---|---|
| Valid E03 | One completion and one work item. Retained callback runs after caller frames are overwritten. 20 simulated erase calls and 4,944 256-byte program calls produce exactly the received advertised container; stock-data guard at `380000` remains intact. |
| Bad content checksum, valid packet checksums | Reception completes, but action validation rejects before updater/flash. Worker releases its primary context and drains the work item. Its result callback is copied into a type-6 application message; after worker frames are overwritten, the actual consumer reaches `400c9c6a`. Test stops at that error-callback entry. |
| Missing end marker | Receive phase remains 2. No completion, work action or flash call. |
| Busy update view | Reception reaches phase 3, but the view's `+95` flag suppresses completion handling. No work action or flash call. |
| New receive starts before queued worker runs | Completed-buffer accessor returns zero for the new phase-1 receive. The retained action performs no flash, releases its context and returns via the actual type-6 queue/result-callback path. |

All cases preserve the compared executable interval `40000400..40190000`. Mutable initialized globals within the larger MAIN section are deliberately excluded from that code comparison. Original 1.44 and E02/E03 file hashes match their recorded values.

A failed early fixture run was traced to a stub omitting the hidden return structure of `400e61cc`, leaving a stale shared-reference field. The final test executes that stock lookup on a supplied parent-view list instead. This was a harness error, not evidence of a firmware fault.

## What this does and does not establish

This closes the modeled queue-consumer-to-action continuity and temporary callback lifetime gap on the tested local route. It uses one persistent machine but explicitly schedules packet arrivals and the application/dialog task entries. It does not establish actual kernel preemption, wakeups or peripheral timing. The consumer begins at a recovered loop boundary with task-stack/register fixtures rather than full application boot.

The registry entry selection and heap backing are supplied. String/rendering operations, project save, mutex/thread operations and flash identity/geometry/factory state are simulated or stubbed. Function managers, shared-reference copies/destructors, work-deque operations, checksums/compatibility decisions and worker/updater instructions run unchanged. Success stops before reset; error delivery stops at the error-handler entry. Real UART/USB ingress, flash write failures, power interruption, physical caches and timing remain unverified.

The retained callback preserves a view/context reference; it does not own a private snapshot of the received image. It obtains the current completed buffer when it runs. The tested restart aborts before programming; a complete second transfer and producer activity during programming are not covered. The next receiving-path check should establish the input gate/scheduler protection across that buffer-use interval, with explicit transport pacing/queue-pressure tests.

Separate release blockers remain: startup failure continuation, exclusive reserved-RAM ownership for 1.44, and physical cache/audio timing. Passing these PC tests does not justify a device flash.

## Evidence

- Script: `work/validate-E03-continuous-queue-action.py`
- Results and exact fixtures/limits: `outputs/Digitone-OS1.44E03-continuous-queue-action-checks.json`
- Earlier audit: `outputs/Digitone-OS1.44E03-receiving-path-audit.md`
'''
Path('outputs/Digitone-OS1.44E03-queue-action-continuity-review.md').write_text(report)
print({'passed_cases':[c['name'] for c in r['cases']],'firmware_unchanged':True,'hardware_ready':False})
