# Restored-project arp eligibility and modeled audio

Both focused gaps are closed for a sequencer-only PC workload: the restored state reaches the actual arp quantizer with valid retained context, and the engine produces nonzero PCM using the unmodified section-7 DSP program. A separate mixed-input test exposes a live-MIDI context gap, described below. E04, stock recovery firmware and the corrected raw overlays are unchanged. No new flashable firmware was produced.

## Causes and fixes

The previous loader-startup folders contained MAIN only. `dsplink.find_section7()` therefore found no DSP program and `install()` selected the handshake-only `DspLink`, whose documented behavior supplies no FM voices. Fresh, separate test folders now also contain unchanged stock section 7. It matches the previously extracted section-7 bytes. The engine selects `DspCpu` and executes the guest DSP program.

The previous checkpoint was `gui-raw.snap`, the first live UI frame, with DSP boot unfinished. The playback harness now waits for actual guest DSP boot and more than 100 modeled renders before configuring notes. This took six instruction-paced model seconds in each case; it is not a physical startup-time measurement and no host semaphore wakeup or DSP-ready flag is injected.

The restored sound's arp was OFF. Copying sequence descriptors did not establish sound arp configuration. A one-detent MODE turn also stayed inside the encoder driver's idle dead zone. The completed workload selects T1, opens FUNC+SYN1, and uses FUNC+NOTE (the emulator's KEYBOARD label) to enable the arp through the guest input dispatcher. The captured menu displays TRUE. The keyboard toggle route is documented in [Elektron's Digitone manual, §9.6](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf).

## Workload and results

Root 62 and raw scale 0 (or disabled scale for controls) are disclosed PC pattern-field fixtures. After warming up, native panel actions select T1, enable its arp, enter grid recording, toggle step 1, leave recording and press PLAY. No sequence descriptors are copied. No MIDI is injected into this sequencer-only test. No event fields, eligibility flags, selected-note results or private context words are seeded. Event production, selection, retained-context reads, pitch adjustment and DSP rendering execute in the guest model.

| Scenario | Hooks | Pitch outputs | Oracle checks | Changed notes | Capture checks | DSP renders | Nonzero audio frames |
|---|---|---:|---:|---:|---:|---:|---:|
| ordinary | corrected | 7 | 7 | 0 | 8 | 12629 | 192292 |
| ordinary | stock_sites | 7 | 0 | 0 | 0 | 12618 | 192316 |
| scale | corrected | 7 | 7 | 7 | 8 | 12619 | 192370 |

All corrected-run context captures and quantizer returns match their independent expected values. Strict custom-instruction checks stay clean, payload bytes stay exact, readiness remains set, and there is no modeled halt or DSP error. The ordinary corrected/stock-site pitch streams match. Stock-site controls restore runtime arp hooks after the same corrected startup; they are not independent stock startup runs.

Ordinary audio bytes identical: False. Unlike the earlier zero-buffer comparison, both recordings now have nonzero audio. If the bytes differ, instruction pacing and earlier scheduling phase remain possible causes; these runs alone cannot establish which cause applies.

Corrected scale examples:
- MIDI pitch 60 → 59; captured context 0x800000be; oracle 59.
- MIDI pitch 60 → 59; captured context 0x800000be; oracle 59.
- MIDI pitch 60 → 59; captured context 0x800000be; oracle 59.
- MIDI pitch 60 → 59; captured context 0x800000be; oracle 59.

## Mixed-input gap

A separate run combines the native sequencer trig with a held live-MIDI chord, CC64 sustain/release and a fresh note. All 30 MIDI bytes are delivered; however, 26 of 27 quantizer calls receive context zero in each corrected run. Only the sequencer-created note retains a valid context; the enabled-scale run changes that one note and leaves the other calls unchanged. A preceding live-only run also had zero context on every quantizer call. These results establish a concrete remaining gap for this live input path; a zero-word oracle pass is not evidence of scale locking. The emitted live pitches remain stock-compatible by the helper's fallback behavior. It remains to trace whether context was never attached, lost on copying/selection or rejected by a later guard. The sequencer-only run has valid context on every quantizer call.

## Evidence and remaining limits

Evidence: `Digitone-E04-PC-ISA-DSP-loader-startup.json`, `Digitone-E04-PC-restored-sequencer-arp-DSP.json`, `Digitone-E04-PC-restored-arp-DSP-summary.json`, the menu PNGs and paired WAV files. Clips suffixed `-audible.wav` remove the silent lead-in only. `Digitone-E04-PC-encoder-dead-zone-control.json` preserves the unsuccessful small-encoder-input control. `Digitone-E04-PC-live-MIDI-zero-context.json` and `Digitone-E04-PC-restored-arp-DSP.json` preserve live-only and mixed-input evidence.

The missing-section diagnosis is an inspection of the local engine's actual selection code, confirmed by real DSP renders and nonzero PCM after supplying the section. It does not diagnose the physical E04 startup freeze. Loader-derived state is still followed by a raw MAIN overlay; a corrected packaged loader test remains outstanding. DSP serial loading, FPGA behavior, timer costs and snapshot restoration remain modeled. Physical cache coherence, timing and exclusive RAM ownership are unverified. Each control restores the same guest snapshot using a disposable emulator card; evolving card contents and scheduling phase are not a complete physical stock/custom control.

Follow-up completed: `Digitone-E04-PC-live-context-loss-review.md` identifies the missed live creator/raw-copy/immediate-publication route. The selected live event never receives candidate context; selection commits zero and the final cookie guard correctly rejects it. Next establish the live descriptor's receiving-pattern ownership and an appropriate capture point before implementing a PC-only fix. A separately named corrected PC-only package still needs verification through the actual loader. Keep the physical Digitone on working stock 1.44.
