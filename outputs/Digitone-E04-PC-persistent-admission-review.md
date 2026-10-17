# Persistent admission and storage lifetime: PC review

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
