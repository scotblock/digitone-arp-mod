# E08E: proposed first M1 hardware trial

**Superseded, 16 October 2026: a confirmed E08E menu-routing regression makes ordinary page buttons open incorrect pages. Do not follow this earlier installation proposal. The frozen file remains available for diagnosis; corrected menu helpers are being validated separately on the PC.**

15 October 2026. This is a review and bounded trial proposal. It is **not hardware certification or an instruction that an installation has been approved/performed**. The final PC-check result is recorded separately in `Digitone-E08E-hardware-trial-review-results.json`; that result must pass before using this proposal.

## Candidate and recovery

Proposed experimental file: `Digitone_OS1.44E08E_M1_ARP_PC_ONLY.syx` in this folder.

SHA-256: `74219ea223999ae190f5c935973b96bf67eea60148416a1009565af6f48dd3a3`.

Verified official recovery: `stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx`.

SHA-256: `d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`.

The last user-reported working physical baseline is E07. Its file remains unchanged. Earlier stock-update rehearsal, backups, the E04 startup failure and successful stock recovery remain recorded; another stock rehearsal is not required solely for this review. Preserve any important changes made since the earlier backups. Use a disposable project for this trial, and keep the stock recovery file accessible. The OS screen still reads 1.44, so identify the build by the exact transmitted file/hash and its new M1 controls.

## Why E08E replaces the earlier PC candidate

E08D's held live arp continued after Stop because the stock MIDI task handles Stop in an outer command, bypassing the descriptor consumer where the prototype expected it. A second Stop also left arp generation active. Mode OFF left retained membership behind.

E08E joins the actual stock command-4 Stop path before stock drains its outgoing notes. It clears M1 generation/membership while preserving the busy private descriptor for its real retirement. Applying OFF uses the same clear. The correction adds no state or copied-memory extent relative to E08D. The arp code/settings/controls and the E07 synth features remain in the candidate.

## Bounded first-trial scope

1. **Agree the experimental trial before installing.** Use the successfully rehearsed startup-menu DIN update/recovery route with Rubix22 MIDI OUT → Digitone MIDI IN. Keep the verified stock recovery file ready. No tool in this work transmits firmware.
2. **Boot checkpoint first.** Establish that the logo clears, the panel responds, a simple synth note sounds, and RECORD/PLAY/STOP work. Report that checkpoint before extending the test. Keep monitoring volume low.
3. **M1 only.** Select MIDI track M1. Its control page is **FUNC + SYN2**: MODE OFF/UP, RATE and GATE. M2–M4 arps are not implemented. Initially use UP, 1/16, 50% gate. Release keys before enabling UP, then send a fresh C–E–G chord.
4. **Use a separate outgoing MIDI channel**, for example channel 9 if it is otherwise unused. Read the displayed channel; do not infer it from an encoder turn count. Keep synth arp channels separate. Send to DIN MIDI OUT and record Digitone MIDI OUT → Rubix22 MIDI IN in Ableton. Avoid MIDI echo: the recording track's MIDI output should be unassigned. A separate sending clip can target the Digitone's configured AUTO channel through Rubix22 MIDI OUT → Digitone MIDI IN. Select M1 to receive that AUTO-channel chord. This mirrors the input path exercised in the PC tests.
5. **Basic musical acceptance.** Expect ascending C–E–G cycling on the selected M1 output channel. Verify key release, Stop while holding the chord, sustain key-release/pedal-release, and OFF → release keys → UP → fresh chord. No new arp notes should appear merely from re-enabling UP. Inspect the MIDI clip for notes that fail to end. M1 produces MIDI for an external instrument/software instrument, not an internal Digitone synth voice.
6. **Stop and review.** Initially avoid important-project saves, copying/loading projects while notes remain held, diagnostic/test modes, shared output channels, simultaneous synth/MIDI arp workloads and output congestion. Pattern handoff/live edits can be the next measured stage after basic M1 behavior is confirmed. Do not treat one successful boot as approval for unrestricted use.

If programming has completed but application startup remains at the logo, use the previously rehearsed stock recovery route. Do not interrupt an active erase/programming operation or substitute a factory/empty reset for reinstalling the stock OS. Preserve the exact screen/message if recovery or transfer fails; the earlier successful recovery is not a guarantee against every hardware/flash failure.

## What the trial would establish

A successful trial would add evidence that this exact enlarged payload executes on the real CPU/cache/DDR configuration and that basic M1 timing/release works on the actual MIDI ports. It would not prove exclusive RAM/DMA ownership across all modes, worst-case audio timing, every callback/reset/exception path, every in-place record replacement, or live project-load/input overlap. Boot failure, hung notes/audio faults, data loss and unsuccessful recovery remain possible.

Keep the current `hardware_ready:false` designation until physical results have been reviewed. A controlled experimental trial and a generally hardware-ready firmware release are different milestones.
