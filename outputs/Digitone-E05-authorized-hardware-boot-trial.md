# E05: authorized single hardware boot trial

11 October 2026. The user explicitly accepted the residual risk after the prior E04 logo hang, successful stock recovery, E05 PC tests and reported Digiemu launch were discussed. This authorizes one user-operated E05 installation/boot trial. It does not certify hardware readiness. No agent tool has transmitted firmware.

The previously reported stock update rehearsal and backups remain recorded; no repeat rehearsal is required. Save and back up any changes made since those backups before proceeding.

Verified immediately before these instructions:

- Candidate: `Digitone_OS1.44E05_SCALE_ARP_PC_ONLY.syx`
  SHA-256: `17fbe13d6b2aad9c096df7ac20fd4499a7bb0951e146fd0fd0aaeace4037e474`
- Stock recovery: `stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx`
  SHA-256: `d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`

Keep the filenames and existing hardware_ready=false/PC_ONLY designation. Risk acceptance changes trial authorization, not validation results.

## One trial

1. Close Digiemu, Ableton and MIDI loggers. Keep Rubix22 USB connected to the computer. Connect Rubix22 MIDI OUT to Digitone MIDI IN; disconnect Digitone USB for this startup-menu DIN trial. Keep monitoring volume low and the verified stock file immediately available.
2. Use the previously rehearsed FUNC-at-power-on startup menu and TRIG 4 OS UPGRADE option. In Elektron Transfer choose SYSEX TRANSFER, then OS upgrade via device startup menu. Select the exact E05 candidate, with Rubix22 as the sending MIDI output. Follow the displayed completion/reboot instructions.
3. Do not interrupt transfer, erase or programming. MIDI transmission takes several minutes. Do not infer a hang from transfer duration alone.
4. First acceptance checkpoint is the logo clearing, normal interface appearing and panel responding. Report update completion and whether this checkpoint succeeds before extending the trial.
5. If boot succeeds, check RECORD/sequence entry, one simple note, PLAY and STOP. Keep use within a disposable test project. Do not enter diagnostic/test modes, which this candidate intentionally refuses.

If programming has completed but application startup stays at the logo, use the rehearsed startup-menu route to reinstall the verified stock file. EMPTY RESET and FACTORY RESET are not rollback. If transfer/programming is still active or reports an error, preserve the exact screen/message and report it rather than power-cycling based on a guessed timeout. If the startup menu or stock recovery fails, stop and seek Elektron support.

## Limits

Full shutdown/worker retirement, enlarged RAM ownership, physical cache coherence, DMA/audio timing and correction of the previous physical startup failure remain unproven. Five PC startup cases, nine refusal controls and five playback cases passed their bounded criteria; ordinary audio still differs from stock in the emulator. Neither those tests nor reported Digiemu launch guarantees hardware recovery.

[Elektron startup-menu SysEx instructions](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer) confirm the physical MIDI route; startup updating cannot use device USB.
