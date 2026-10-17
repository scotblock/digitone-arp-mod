# Third-party material

## Digiemu

Source: https://github.com/irpina/digiemu

`work/upstream/digiemu/` contains a local source snapshot used during this research, including local emulator changes. Its `pyproject.toml` declares **GPL-2.0-or-later**. The GNU GPL version 2 text is included as `COPYING`. Existing copyright notices remain in the source. The snapshot's current upstream commit is not verified; do not treat historical pinned commits elsewhere as an exact pin for this snapshot. No firmware or installed engine DLL is included.

## elektron-firmware-tool

Source: https://github.com/mischa85/elektron-firmware-tool

`work/elektron-firmware-tool/` contains the locally used C sources and documentation. **MIT**, copyright 2026 Marcel Bierling; original LICENSE and PROVENANCE.md included. Its current commit/local difference has not been certified in this export.

## External dependencies not vendored

- Unicorn: https://github.com/unicorn-engine/unicorn — see its upstream licenses and the Digiemu patches for affected code.
- Capstone: https://github.com/capstone-engine/capstone — upstream license applies.
- DNX: https://github.com/NoiseAndMatter/DNX — AGPL-3.0-or-later; optional draft project generator dependency. Historical checkout recorded commit 5512058d87b5cf5b46b3ad0c51d929fcf9051172.

No Elektron firmware image, sound library, user project or recording is included. This document does not relicense third-party work or select a license for this project's original contributions.
