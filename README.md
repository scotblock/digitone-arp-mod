# Digitone arp modifications

Source and research archive for the original Elektron Digitone / Digitone Keys, focused on OS 1.44. Unofficial; not affiliated with Elektron.

## Current status — 18 October 2026

| Build | Change | Evidence |
| --- | --- | --- |
| E05 | Scale-constrained synth arp | User reported working on Digitone |
| E06 | Synth arp offsets interpreted as scale degrees | User reported working on Digitone |
| E07 | Synth arp notes sent over DIN MIDI | User recorded output in Ableton on hardware |
| E08F | M1 MIDI-track UP arp, MODE/RATE/GATE controls, corrected menu routing | User reported working on Digitone; exact installed hash not independently verified |
| E09 | Synth arp follows normal DIN / USB / both selection, independent note ownership per port | PC tests only; physical dual-port validation outstanding |
| E09A | Corrects M1 sequenced notes selecting parameter-lock lists as arp settings | User confirms physical synth/M1 arp DIN and USB output and M1 sequencer-triggered arp; installed hash not independently verified |
| E10 prototype | M1 16-step scale-degree sequence, rests, root/scale controls and native encoder editor | Packaged PC workflows pass; exact-byte experimental hardware-trial candidate prepared locally; physical E10 trial pending |
| E11 experimental candidate | M1 synth-style Left/Right, E/F and Up/Down step programming | Native controls, packaged loader/startup and playback pass on PC; physical E11 trial pending |

M2–M4 arps are **not implemented**. A MIDI arp step editor now exists as an **E10 PC prototype**, with native startup/reset integration tested on PC. Native editor-to-bank publication, project saving/reloading and consumed-pattern recall now pass PC tests. Stopped native copy/paste/undo and clear/undo, ten guarded reset entries, and unsaved cache write/cold restore now pass PC checks. Modeled automatic shutdown and cold recovery now pass when the write completes. A synthetic first-chunk interruption exposes an unchanged stock bank-selection limitation; physical hold-up timing and hardware readiness remain unverified. E08F/E09 have a **confirmed M1 sequencer arp bug**: a sequenced note can disable the arp by selecting the wrong settings source. E09A corrects that source selection, with user-reported sequencer operation on hardware. Broader multi-note sequence entry, additional transition/copy/reset families and physical E10 behavior remain outside current coverage. E08E contains a known menu regression and is superseded by E08F. E04 failed to finish startup on hardware; stock was restored successfully.

## Start here

- [E11 synth-style M1 programming](outputs/Digitone-E11-synth-style-notes.md) — native arrow/E/F editor and separate experimental candidate; E10 unchanged.

- [E10 controlled hardware-trial guide](outputs/Digitone-E10-hardware-trial-guide.md) — exact tested bytes frozen locally, startup-menu DIN model and stock-dependent patch reconstruction pass; no hardware certification or public E10 release.

- [E10 complete packaged PC workflow](outputs/Digitone-E10-PC-package-workflow-notes.md) — distinct programs, native save, cold restart/named recall, held-note handoff and copy/clear/reset checks.

- [E10 packaged PC integration](outputs/Digitone-E10-PC-package-integration-notes.md) — stock loader reconstructs the actual internal package, native startup restores 128 records, and keyboard/sequencer playback yields 24 matching note pairs per port.

- [Accepted E10 development assumptions](outputs/Digitone-E10-development-assumptions.md) — continue with stock power handling; no hold-up measurement gate or guaranteed abrupt-loss recovery claim.
- [Focused update-interruption diagnostic](outputs/Digitone-E10-PC-update-interruption-notes.md) — the custom caller and a stopped-entry stock-helper control expose the same header-publication interruption limit.

- [E10 closed-unit hold-up assessment](outputs/Digitone-E10-PC-hold-up-assessment.md) — unchanged shutdown transfer volume, conditional timing lower bounds, and why physical reserve remains unknown.

- [E10 automatic shutdown and interrupted-write results](outputs/Digitone-E10-PC-powerfail-notes.md) — modeled automatic recovery passes after a complete write; a mid-write cut exposes a stock selection limitation.

- [E10 copy, reset and unsaved working-cache checks](outputs/Digitone-E10-PC-lifecycle-notes.md) — native clipboard/undo and incremental retained-image synchronization; unsaved records survive an explicitly invoked stock write and cold PC restore.

- [E10 editor and pattern recall](outputs/Digitone-E10-PC-pattern-binding-notes.md) — panel-created A01/A02 programs save, reload and recall independently; a confirmed running held-chord handoff passes on PC.
- [E10 native persistence bridge](outputs/Digitone-E10-PC-persistence-notes.md) — 128 records survive native save/rebuild and reboot after an explicitly invoked stock cache write; automatic power-loss handling remains unverified; editor binding is covered by the later note above.
- [E10 storage verification](outputs/Digitone-E10-PC-storage-verification-notes.md) — earlier named-project audit that motivated the persistence bridge above.

- [E10 startup and pattern-storage progress](outputs/Digitone-E10-PC-startup-and-pattern-storage-notes.md) — earlier explicit RAM APIs and native kit-codec findings.
- [E10 step sequencer prototype and controls](outputs/Digitone-E10-PC-step-sequencer-notes.md) — source/tests only, no E10 download firmware.
- [E09A sequencer arp correction](outputs/Digitone-E09A-sequence-notes.md)
- [Download experimental patch packages](https://github.com/scotblock/digitone-arp-mod/releases) — supply your own stock OS 1.44 file; [instructions](docs/PATCH_RELEASE.md).
- [Latest routing change and remaining work](outputs/Digitone-E09-routing-and-next-features.md)
- [Validation scope and limits](docs/VALIDATION.md)
- [How the source archive is organized](docs/REPRODUCIBILITY.md)
- [Build progression](docs/CHANGELOG.md)
- [Third-party sources and licenses](THIRD_PARTY.md)

`work/` preserves the research scripts and their original relative paths. `outputs/` contains historical notes and selected recorded results. Older notes describe experiments, proposed changes and superseded decisions; they are not current installation instructions.

The research tree is a **source archive, not a turnkey source build**. Experimental release packages provide a separate stock-dependent patcher for E08F and the E09 PC-only preview. Stock/modified firmware, extracted firmware sections, flash cards, snapshots, recordings and private projects are excluded. Firmware inputs must be obtained separately. No complete installable image is supplied, and a passing PC test does not establish hardware readiness.

Personal absolute file paths were rewritten during export. The manifest records hashes of the original and exported source. Some historical scripts still require local path/toolchain configuration and generated artifacts. See the reproducibility notes before running them.

## License status

No distribution license has yet been selected for the project's original contributions. Third-party sources retain their own licenses; see THIRD_PARTY.md. Do not assume the entire repository is MIT-licensed.
