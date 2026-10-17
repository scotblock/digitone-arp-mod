# Reserved-RAM follow-up: OS 1.42

Next audit completed: [continuous startup, playback, pattern switching and stack observations](Digitone-OS1.42-continuous-RAM-and-stack-audit.md). Its finite runtime checks strengthen the candidate-region evidence; global ownership remains unproven.

The route remains viable in the bounded PC tests. This pass closes the fitted-memory configuration and memory-alias gap, pins the upstream evidence, and confirms that OS 1.42 needs its own hook definitions. It does not establish exclusive ownership of the RAM region throughout playback.

## Version-pinned sources

Read-only upstream snapshots:

- Elekloader commit `d1cdc74af61aaf6222b76f940e6b10bc5f586fed`.
- Digiemu commit `24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2`.

The [Elekloader Digitone profile](https://github.com/irpina/elekloader/blob/d1cdc74af61aaf6222b76f940e6b10bc5f586fed/elekloader/devices/digitone_mk1.py) registers 1.43 and 1.44, with the proposed `47be0000..47c00000` area. Those versions' observations do not certify 1.42. The [Digiemu status](https://github.com/irpina/digiemu/blob/24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2/docs/STATUS.md) identifies separate cached/uncached memory in its app model as a fidelity limitation; its stricter model shares the backing memory.

Source hashes and hook comparison are recorded in [compatibility results](Digitone-OS1.42-upstream-route-compatibility.json).

## Actual OS 1.42 geometry

Decoded 41 register writes in the stock bootstrap's straight-line setup, file offsets `32c..4ee`. Unexpected instruction forms cause this narrow decoder to fail rather than guess. The geometry registers are:

| Register | Written value | Relevant field |
|---|---|---|
| DDR_CR04 | `00010101` | Eight banks |
| DDR_CR15 | `02000103` | ADDPINS = 2 |
| DDR_CR16 | `02000407` | COLSIZ = 2 |

Using the [NXP manual](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf), Tables 21-20/21-28 and the column-width definition, this gives 14 row bits, 10 column bits, eight banks and a one-byte datapath: **128 MiB**. This is a configuration-derived result, not a physical measurement. Upstream documents a previous incorrect 64 MiB decode; that would incorrectly fold the proposed address onto `43be0000`. OS 1.42's decoded configuration does not support that folding.

The PC model now canonicalizes SDRAM addresses in `40000000..80000000` modulo `08000000`. Thus `47be0000`, `4fbe0000`, `57be0000`, `5fbe0000`, `67be0000`, `6fbe0000`, `77be0000` and `7fbe0000` share storage. `43be0000` is a distinct physical offset. See [geometry evidence](Digitone-OS1.42-DDR-geometry.json).

## Execution and reference checks

With alias normalization installed in both startup and arp fixture classes:

- All 52 startup/storage assertions pass, including stock clearing, the full stock initializer, readiness and reentry.
- All 5,475 arp-integration assertions pass, including 5,256 quantizer comparisons and four track pipelines.
- Forty comparisons across five sampled offsets and eight address windows agree. A write through the uncached alias is visible through the cached address.
- The unchanged rooted instruction screen now checks all eight aliases. Across 55,354 reached instructions, it finds zero direct operands into the reserved region. Its 4,200 indirect edges and two unknown boundaries remain unresolved.

Evidence: [alias test summary](Digitone-reserved-RAM-alias-results.json), [startup assertions](Digitone-reserved-RAM-alias-startup-results.json), [arp assertions](Digitone-reserved-RAM-alias-arp-results.json), [all-alias reference screen](Digitone-reserved-RAM-all-alias-reference-screen.json).

Memory identity tests do not emulate hardware cache coherence, DMA timing, or all computed and bulk accesses. The interpreter rejects accesses crossing a physical wrap boundary rather than implementing them; none of the exercised fixtures requires such an access. Startup retains the previously validated stock-clear loop summary. Arp cases retain supplied producer-finalization fields and gates. These results do not constitute a complete boot/playback run.

## Hook compatibility and next target

At the addresses named by the pinned 1.43 core, only one of eight expected instruction fragments matches OS 1.42: the boot call at `40000538`. The seven other sites differ. This confirms that the entire upstream core cannot be transferred by reusing its manifest. The matching boot call supports continued isolated copier tests; it does not certify a complete port.

For this V1 investigation, the next focused target is a continuous OS 1.42 startup-to-playback execution with the shared DDR model and a write watch on the occupied `47be0000..47be1b74` physical interval. Trace computed pointers, bulk writers and stack use, and connect the outstanding live/held/queued producers. A full hook-bus port is additional work only if adopting that complete framework. Any eventual packaging must preserve exact 1.42 hashes and site signatures.

Original SysEx and main-section hashes were checked unchanged by the startup suite. No firmware was edited or repacked, no flashable output was produced, and no hardware I/O occurred.
