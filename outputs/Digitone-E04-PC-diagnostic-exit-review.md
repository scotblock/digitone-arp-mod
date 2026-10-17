# Diagnostic exit: input shutdown and queued-note retirement

The recovered 1.44 diagnostic-exit paths do not provide the proposed local barrier in the tested PC states. Native note creation can still publish after diagnostic entry. Command exit and registered page exit reach the pool initializer with input enabled and queued notes still owned. The queue is discarded by reinitialization itself, rather than retired beforehand. These results reject relying on the recovered exit paths alone; they do not establish a physical-device failure or complete command-transport reachability.

Firmware and the current raw guarded PC candidate remain unchanged. This task added execution tests and evidence only.

## Continuous command path with native notes

Both tested preparation-bit branches execute the following sequence on one disposable captured machine:

1. Run stock diagnostic entry `4008e8b2`, reached by the ENTER_TEST_MODE command in the recovered command worker. It installs audio vector `4008e5c0` and its timer callback; it preserves the enabled ordinary input settings.
2. Supply two complete MIDI Note On packets to native wrapper `400eb2d2`. It executes `400eb166 -> 400eae5c -> 400ff3ec -> 40100252`, allocating and publishing E64 and G67 through stock instructions and the existing PC hooks. No note-event, source descriptor or queue bytes are injected by this continuous test.
3. Run the actual `%s` parser `4008a474`, then the command worker from its post-parse boundary `4008b4ce`. Native string comparison recognizes `#EXIT_TEST_MODE` and takes `4008b890 -> 4009d0ea -> 4009c5ae -> 4009c5a0`.
4. Stop at `47be3400`, the PC reset hook replacing stock entry `400ffed0`, before its first clear. The node head/tail and E-to-G link still reference both native events. MIDI receive mask is 3 and note permission is 1. Interrupt mask is zero. Both events retain their note/state fields and captured disabled-scale word `8000003c`.
5. Resume through the full stock pool initializer and stop at `4009c5aa`, before remaining setup calls. Queue head becomes zero and the first of those events becomes the free-list head. Metadata is cleared and ready republished. This records lifetime invalidation through the actual exit route, rather than injecting a reset into a paused copy.

With preparation bit `80000` clear, the preparatory calls are skipped. With it set, all four actual routines execute: `4009bcc0`, `4009b3da`, `4009b56e`, `4009b65a`. Their observed execution still leaves the input settings and queued-note chain intact at reset. No subcall return, shutdown acknowledgement or heap allocation result is stubbed in these tests.

The command comparison also reaches reset in a control without prior diagnostic entry. Its local branch does not require the test flag to be set. This is not a claim that every physical transport or product UI can admit the command.

## Input-admission control

After actual diagnostic entry with test flag 1 and audio vector `4008e5c0`, the complete native Note On wrapper returns without publication when note permission is zero, and allocates/publishes when it is one. Thus switching the audio handler or setting the test flag is insufficient to reject notes at this handler boundary. The ordinary MIDI receiver transport/dequeue is outside these calls; no assertion that packets always reach this wrapper on hardware is made.

## Registered page-exit callback

Audio-test page entry `400b25bc -> 400e7e7e` is distinct from the ENTER_TEST_MODE command path. It is executed separately before the page-exit controls.

Using constructed manager/page/list/current-task state and the real subobject vtable `401c4714`, native page removal `400e6634` acquires the manager mutex, invokes virtual exit at `400e6698`, and reaches `400e569a -> callable copy/invocation -> 400b25c2 -> 4009d0ea -> setup -> reset`. The callback target/manager match the actual constructor record at `400b2c48..400b2c60`. Actual stock heap allocation for its one-byte closure executes; no supplied allocator return is used.

Both uncontended and recursive mutex controls preserve the queue, enabled input, pending marker and descriptor context at reset. The mutex remains owned and the page node remains linked. Kernel mutex acquisition restores the caller's interrupt mask before the callback; it is a UI-list lock, not a demonstrated global input/ownership barrier. These controls do not execute the earlier real application request that selects the audio-test page, contention scheduling, or callback exception cleanup.

## Coverage and remaining decision

Nine native execution controls and 16 summary checks pass. The continuous test's queued notes are guest-produced; receive configuration, setup-bit selection, packet delivery after dequeue and captured initialized machine state are controlled. Separate queue/pending-marker controls deliberately supply owners to test preservation. Neither live IRQ/task scheduling nor physical device state is exercised.

This closes the question of whether the recovered command branch, optional preparation calls, or uncontended/recursive page-exit mutex supply a local shutdown/retirement barrier: they do not in these observed paths. Earlier transport admission, real page-selection preconditions, other retained payload owners, asynchronous transfers and every computed entry are still not globally certified. Queue reconstruction after exit must not be mistaken for retirement before mutation.

The next design issue is a bounded pre-reinitialization policy for the PC mod—explicit producer exclusion and retirement, or a supported-mode policy that avoids live reconstruction—rather than assuming the readiness flag or copy guard protects the entire allocation-to-publication interval. Do not change stock diagnostic behavior or add a busy wait under interrupt masking without a verified lifetime/return contract. Ordinary pattern handoffs do not reconstruct this pool and remain separately covered.

Physical reserved-RAM ownership, cache coherence, masked-copy duration and startup behavior remain unvalidated. These controls provide no authorization or readiness claim for another device trial, and no new flashable update is produced.

Evidence: `Digitone-E04-PC-diagnostic-command-exit.json`, `Digitone-E04-PC-diagnostic-preparation.json`, `Digitone-E04-PC-diagnostic-note-admission.json`, `Digitone-E04-PC-diagnostic-page-exit.json`, `Digitone-E04-PC-diagnostic-live-exit.json`, `Digitone-E04-PC-diagnostic-exit-summary.json`. Scripts under `work/test-PC-diagnostic-*`; current guarded candidate under `work/os144/PC_ONLY-atomic-storage-*` is hash-verified unchanged.
