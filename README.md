# Digitone arp modifications

Source and research archive for the original Elektron Digitone / Digitone Keys, focused on OS 1.44. Unofficial; not affiliated with Elektron.

## Current status — 17 October 2026

| Build | Change | Evidence |
| --- | --- | --- |
| E05 | Scale-constrained synth arp | User reported working on Digitone |
| E06 | Synth arp offsets interpreted as scale degrees | User reported working on Digitone |
| E07 | Synth arp notes sent over DIN MIDI | User recorded output in Ableton on hardware |
| E08F | M1 MIDI-track UP arp, MODE/RATE/GATE controls, corrected menu routing | User reported working on Digitone; exact installed hash not independently verified |
| E09 | Synth arp follows normal DIN / USB / both selection, independent note ownership per port | PC tests only; physical dual-port validation outstanding |

M2–M4 arps and a synth-style MIDI arp step editor are **not implemented**. Ordinary sequenced MIDI chord capture and saved-project persistence need further work. E08E contains a known menu regression and is superseded by E08F. E04 failed to finish startup on hardware; stock was restored successfully.

## Start here

- [Latest routing change and remaining work](outputs/Digitone-E09-routing-and-next-features.md)
- [Validation scope and limits](docs/VALIDATION.md)
- [How the source archive is organized](docs/REPRODUCIBILITY.md)
- [Build progression](docs/CHANGELOG.md)
- [Third-party sources and licenses](THIRD_PARTY.md)

`work/` preserves the research scripts and their original relative paths. `outputs/` contains historical notes and selected recorded results. Older notes describe experiments, proposed changes and superseded decisions; they are not current installation instructions.

This is a **source archive, not a turnkey firmware release**. Stock/modified firmware, extracted firmware sections, flash cards, snapshots, recordings and private projects are excluded. Firmware inputs must be obtained separately. No installable firmware is supplied, and a passing PC test does not establish hardware readiness.

Personal absolute file paths were rewritten during export. The manifest records hashes of the original and exported source. Some historical scripts still require local path/toolchain configuration and generated artifacts. See the reproducibility notes before running them.

## License status

No distribution license has yet been selected for the project's original contributions. Third-party sources retain their own licenses; see THIRD_PARTY.md. Do not assume the entire repository is MIT-licensed.
