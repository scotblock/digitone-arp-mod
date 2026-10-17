# Digitone 1.44 E05 — PC-only candidate

File: `Digitone_OS1.44E05_SCALE_ARP_PC_ONLY.syx`

SHA-256: `17fbe13d6b2aad9c096df7ac20fd4499a7bb0951e146fd0fd0aaeace4037e474`

Use this candidate in Digiemu only. Hardware readiness remains unproven. Stock 1.44 and E04 files were preserved. The device/version display still says 1.44; distinguish this build by its filename and checksum.

## What changed

E05 packages the corrected ColdFire startup stores, the tested live root/scale capture and atomic context copying, native storage initialization, cold/LIVE admission, input/release/sustain guards, UI/reset refusal and deferred release draining into one copied payload. Helpers previously supplied separately to PC RAM are relocated to `47be3800..47be46ee`; the unsupported diagnostic queue command returns at its outer entry before allocating or publishing any event. The copied payload is 18,436 bytes and ends at `47be4804`.

Global parent destruction is not disabled. The shutdown audit supports a startup/global lifetime counter that stays at 94 through the observed queue lifecycle. Forced last-release tests show deletion at zero; full application shutdown dispatch and worker retirement at that boundary remain unproven.

## Completed comparisons

- Five native startup cases passed: stock and candidate with fresh/restored projects, plus candidate with its optional feature deliberately disabled. Every run reached the UI; candidate runs reached LIVE. Native copying supplied the added helper code; tests did not host-load those helpers. The disabled feature reached LIVE with READY=0.
- Nine stopped-state reset/diagnostic refusal controls passed, without event allocation/publication or changes to the monitored storage.
- Five matched DSP playback cases passed: stock/candidate with scale off and enabled, plus disabled-feature ordinary playback. Each delivered all input MIDI, produced nonzero audio without a DSP error or CPU halt, and completed the requested pattern replacement with sustained notes and subsequent fresh input.
- 48 observed scale quantizer returns matched the independent oracle; 1 returned a changed pitch. These are observed call counts, not exhaustive workload coverage.
- Transport packet checksums/sequence, container length/checksum/padding, compressed MAIN checksum and independent decompression passed. Non-MAIN sections match stock byte for byte.

## Ordinary playback comparison

- E05_restored: pitch sequence identical to stock = True; audio byte exact = False; observed pitch calls 49 versus stock 49.
- E05_disabled: pitch sequence identical to stock = True; audio byte exact = False; observed pitch calls 49 versus stock 49.

Ordinary playback equivalence is incomplete. The observed differences remain a limitation of this candidate; passing the per-run controls does not resolve their cause.

In the stock-versus-enabled-candidate ordinary run, the first audio difference occurred at 15.1875 seconds; 10.22% of interleaved samples differed over the take. This measurement does not establish the cause.

## Limits and use

These are PC tests with modeled clocks/peripherals, scoped ISA support and bootstrap/DSP shortcuts. Startup was exercised from decoded MAIN with loader-matching boot arguments, rather than a complete execution of the new physical updater/loader. They do not certify cache handoff, physical timing, DMA behavior, the enlarged RAM region or recovery from every exception. Diagnostic/test-mode entry is intentionally unsupported in this candidate. No hardware trial was performed, and this build is not certified to fix the earlier logo hang.

To test: add the E05 `.syx` to Digiemu as a separate firmware entry and build it with a fresh emulator session first. Keep the stock entry available. A subsequent test can use a copy of the saved project; do not overwrite the original session. Stop here before planning any physical installation.

## Evidence

- [Digitone-E05-shutdown-diagnostic-audit.json](./outputs/Digitone-E05-shutdown-diagnostic-audit.json)
- [Digitone-E05-PC-candidate-layout.json](./outputs/Digitone-E05-PC-candidate-layout.json)
- [Digitone-E05-PC-container-verification.json](./outputs/Digitone-E05-PC-container-verification.json)
- [Digitone-E05-PC-startup-comparison.json](./outputs/Digitone-E05-PC-startup-comparison.json)
- [Digitone-E05-PC-diagnostic-reset-controls.json](./outputs/Digitone-E05-PC-diagnostic-reset-controls.json)
- [Digitone-E05-PC-playback-comparison.json](./outputs/Digitone-E05-PC-playback-comparison.json)
- [Digitone-E05-PC-ordinary-audio-difference.json](./outputs/Digitone-E05-PC-ordinary-audio-difference.json)
