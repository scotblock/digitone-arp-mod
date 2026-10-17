# E04 hardware-trial readiness and stock recovery

Reviewed 8 October 2026. Target: original Digitone / Digitone Keys, stock OS 1.44. This document records a proposed trial; no firmware was transmitted, installed or modified during this review.

## Decision

**Physical trial outcome, 8 October 2026:** the user reported E04's update completed but startup remained on the Elektron logo with H at bottom left and 1.44 at bottom right. Stock 1.44 was subsequently reinstalled and reported working. E04 failed startup acceptance and must not be reinstalled pending PC diagnosis and a reviewed correction. The earlier proposed trial below is historical; the instrument is now back on stock. See `Digitone-E04-hardware-startup-incident.md`.

E04 is a PC-validated experimental candidate, not a hardware-certified release. The bounded startup, fallback, placement and container checks support planning a controlled device trial. On 8 October 2026 the user confirmed that the requested stock 1.44 update rehearsal and external backups are complete. These are user-reported, not agent-observed. After discussion of boot failure, audio faults, RAM conflicts, data corruption and possible failed recovery requiring service, the user explicitly authorized the E04 trial and instructed proceeding. Both E04 and stock recovery hashes were reverified unchanged before providing installation instructions. Installation completion and post-installation behavior remain pending; no agent tool transmitted firmware. Do not repeat the stock rehearsal merely to satisfy this review.

Physical cache execution, worst-case audio deadlines and RAM ownership under unobserved workloads are residual trial risks. A successful stock rehearsal reduces installation uncertainty; it does not certify E04 or guarantee recovery after every flash or electrical failure. Keep its PC-only filename and existing `hardware_ready:false` status.

## Reviewed evidence

| Area | Established | Remaining limit |
|---|---|---|
| Exact file | SHA-256 matches the validated E04 candidate; independent framing, checksums and decompression passed. Non-MAIN section contents remain stock. | No physical flash readback. |
| Startup | Actual packaged loader, copier and application continuations reach playback. Valid metadata works; bad magic/pointer disable private context and continue stock startup. | Staged PC execution, short prepared-drive workload. Bus faults, corrupted code and a nonreturning initializer are not recovered by this fallback. |
| RAM | Fixed heap, recovered stack inventory and observed DMA descriptors avoid the reservation. Observed reservation stores belong to intended code. | No universal ownership proof, worst-case stack bound or completed broad project-load/reset coverage. |
| Cache | Complete copy precedes stock data/instruction/branch invalidation and first helper execution. | Instruction cache is already enabled during copying. Logical stale-state controls are not silicon measurements. |
| Musical operation | 1.44 helper/caller evidence covers scale output, capture/copies, sustain, cancellation and eligible cached replay across replacement. | Some paths use explicit fixtures; not all naturally occurring hardware states are covered. |
| Audio | PC packet-age discrepancy has a bounded emulator explanation. Stock physical recordings provide external audio and clock references. | E04 physical audio and timing remain unmeasured; the detailed timing attempt without render coverage is excluded. |
| Startup receiver | Newly tested exact E04: received bytes match; five simulated erases and 2,472 writes produce the advertised container through `1b5000`. Bad whole checksum, missing end and bad packet checksum cause no simulated programming. | Data packets enter the recovered receiver callback; first/end frames traverse UART IRQ. Full serial pacing, physical flash errors and one continuous transfer-to-reboot are not modeled. |

The startup receiver test is new evidence from this review; other rows consolidate existing evidence without rerunning it. No application USB receive-freeze or emulator audio-synchronization change is part of E04.

## File identity

E04: `Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx`

SHA-256: `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`

Verified official recovery copy: `stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx`

SHA-256: `d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`

The recovery copy is byte-identical to the user's official 1.44 file and is now preserved in the workspace rather than only in Windows Temp. Both stock and E04 display OS **1.44**: the display cannot distinguish them. Record which exact file was successfully installed. Do not substitute E01–E03.

## Preparation and stock rehearsal

1. Save the current hardware test project. Export important projects and sounds to the computer with Elektron Transfer; inspect the saved backup files. Keep the baseline pattern, sound and settings identifiable for later comparison. An OS recovery file is not a project backup. [Elektron manual, backup section](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf).
2. Close Ableton, the MIDI logger and other MIDI applications for updating. Keep Rubix USB connected to the computer. Use **Rubix MIDI OUT → Digitone MIDI IN**. This reverses the clock-recording direction; the successful recording does not test this sending path. Disconnect Digitone USB for this DIN rehearsal. Keep monitoring volume low.
3. When a stock rehearsal is explicitly agreed, use only the verified stock recovery file with the startup procedure below. This is itself a real OS write; merely loading a file in Transfer or seeing the startup menu is not proof of successful recovery.
4. Record Transfer's completion result and the device's completion/reboot. Confirm normal boot, saved-project availability, RECORD/sequence entry and playback. If this fails, investigate the stock transfer setup and stop before E04.

## Documented startup procedure and recovery

Hold **FUNC** at power-on, select **TRIG 4: OS UPGRADE**, then use Transfer's **SYSEX TRANSFER → OS Upgrade via device startup menu** workflow and the verified stock file. Follow its displayed instructions through completion. Device USB cannot perform this startup update; use the physical MIDI connection. [Elektron startup-update guidance](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer), [original Digitone manual, printed page 81](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf).

Use this same stock procedure if E04 later fails normal application startup. **EMPTY RESET and FACTORY RESET are not firmware rollback.** Do not choose them as recovery steps. Do not interrupt an active erase/program operation. If an update reports an error or remains stuck, preserve the exact message and stage; do not invent a timeout-based power-cycle procedure. If the startup menu is unavailable or stock recovery fails, stop and seek Elektron service/support rather than repeatedly trying modified files.

At standard MIDI wire speed, E04's 1,604,128 bytes alone take roughly 8.6 minutes, before sender delays and programming. A long transfer is not by itself evidence of a hang. Use the application's/device's status, not a short fixed timeout.

## Proposed E04 trial after prerequisites and explicit agreement

Do not automate installation. Review the exact candidate and remaining risks before any E04 transmission. Use the rehearsed startup DIN route, not the ordinary live-application USB updater. Keep an untouched stock recovery copy immediately available.

Run the following stages in order, stopping at the first failure:

1. **Startup and basic operation:** reach the normal interface, check panel response, RECORD/sequence entry, ordinary note playback and STOP. Test one simple sound/track before a busy project. Do not perform a factory reset as a test.
2. **Scale function:** use a simple stable-pitch sound with transpose/portamento disabled. Compare chromatic behavior and a known nonchromatic scale. Use deliberately out-of-scale arp offsets and verify resulting pitches from recorded audio; MIDI clock alone cannot prove note pitches. Record root, scale, base note and offsets.
3. **Context lifetime:** test release, sustain on/off, STOP/restart, then an actual completed pattern change between two distinct roots/scales. Distinguish held/eligible cached notes from fresh notes after replacement. A requested pattern change is not proof it completed, and stock-cancelled notes should not be expected to revive.
4. **Matched playback:** record the preserved stock-reference pattern for about 60 seconds with audio and MIDI together, then a short voice-heavy test. Observe panel response, hangs, unexpected notes, persistent notes and repeatable discontinuities. Musical output may change intentionally; do not demand byte-identical audio where pitches differ.
5. **Restart and project use:** save only a disposable test project, check its reload and a few completed shutdown/restarts. A clean short trial does not establish all projects or worst-case RAM/timing safety.

If the device hangs, RECORD fails, scale output is wrong, notes persist unexpectedly or reproducible new crackles appear, stop extending the trial and return to stock using the rehearsed route once any update operation is complete. Preserve recordings, settings and the exact failure sequence. Do not treat a passing trial as a release-quality certification.

## Next device action

The stock rehearsal, backups and explicit E04 trial authorization are now recorded. Guide the user through the rehearsed startup DIN route with the verified E04 file, then record update completion, normal boot, RECORD and simple playback before expanding to arp tests. No repeat stock rehearsal, further metronome-only capture or expanding USB shutdown audit is required for this plan. Preserve the PC-only designation as historical file identity; authorization to try it does not establish hardware certification.

## Local evidence

- `Digitone-OS1.44E04-PC-validation-review.md`
- `Digitone-OS1.44E04-physical-cache-and-timing-assessment.md` (supersede its older pending/empty-log baseline notes with the paired-take report)
- `Digitone-OS1.44-continuous-fallback-and-RAM-review.md`
- `Digitone-OS1.44-final-fallback-placement-and-audio-review.md` (historical cache wording is corrected by the E04 cache assessment)
- `Digitone-E04-startup-DIN-checks.json` (all four new controls passed)
- `Digitone-stock-paired-take-20261008-review.md`
