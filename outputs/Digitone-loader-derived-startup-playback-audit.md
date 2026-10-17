# Digitone OS 1.42: loader-derived initialization and playback

The PC continuation passes. The actual loader machine reaches the native context initializer, and its saved guest state proceeds through UI startup into arp playback. Firmware remains unchanged; no installable firmware was generated.

## Continuity established

The stock bootstrap and updater ran against the same ephemeral extended container used for the preceding loader/copy audit. MAIN decompression matched the complete 2,423,492-byte extended image, including the early copier and optimized helper/table bytes. The normal Digitone model supplied boot flags `0x00140000`.

Application initialization used that same machine. The test asserted that every CPU register, the control map and the complete loaded image matched the loader handoff before execution resumed. It did not reload MAIN, replace the boot flags, install the helper bytes directly, or supply initialized metadata.

At this boundary, bootstrap device hooks were removed and application device models installed. An exhausted native execution-budget hook also had to be removed; retaining it prevented later chunks from executing. Application model setup supplies three ready/status values, recorded in the detailed results. These are emulator assumptions, not firmware mutations. Application flash-read models retained the full extended flash image, including its shifted asset-section offsets.

The native copier copied the 2,324-byte helper image, including 105 longword writes for the complete 420-byte table. Stock startup then cleared the temporary source and established its caches. The first resident helper execution was the initializer at `0x47be0666`, after the stock cache setup.

The initializer entered with readiness zero, executed the stock initialization body with interrupts masked, returned once, and published readiness one. Stock allocation links were valid. Code, table, readiness and guards survived the cold, intro and settled-UI stages. Ten stock tasks were observed during cold startup.

Intro, settle and playback used snapshots of that guest state in fresh engines. This establishes a chain derived from the executed loader; it is not one uninterrupted engine through playback. No helper image, startup hook or metadata header was reinstalled at those later stages.

## Playback observations

| Observation | Result |
|---|---:|
| Emulated playback duration | 10.066 seconds |
| Rendered audio | 1,932,672 bytes |
| Producer calls | 20 |
| Eligible context captures checked | 18, all matching |
| Native lookup-table reads | 11 |
| Quantizer calls | 11 |
| Pitch changes | 11, all matching the oracle |
| Unhandled playback stops | None |
| Unexpected writes observed in watched reserved storage | None |

The native lookup instruction read the bytes copied by startup. Representative pitch changes were `57 → 56`, `69 → 68` and `81 → 80`; the later fixed-point pitch results also matched. Code and unused-region guards remained intact at playback completion.

The scale behavior test deliberately sets a track's root/scale at the producer and changes those fields afterwards. That makes retained-context behavior observable. It is a labeled fixture, not proof that a user-selected configuration or every natural queue/transition path behaves identically. Pattern buttons were exercised, but this run did not instrument completed pattern replacement and must not be cited as proof of a completed handoff.

Sixteen non-vacuous continuation checks passed. The original SysEx hash before and after remained `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`. The loader made no emulated flash program or erase operations. Scratch snapshots are PC state artifacts, not installation images.

## Remaining limits and next target

Physical cache, store-buffer, DMA and DDR coherence remain unverified. These runs use modeled devices and flash-read, semaphore, idle-scheduling and timer shortcuts. This playback run was not a cycle-aware DMA-deadline measurement. Finite preservation and write observations do not establish global exclusive ownership of the proposed storage.

The next useful PC check is to repeat the cycle-aware playback/deadline controls from this new loader-derived snapshot, then exercise an instrumented, completed pattern handoff with queued and sustained notes. That would test timing and transition behavior using the startup state now established. It would still not certify physical hardware coherence.

Detailed evidence: [startup and playback results](Digitone-loader-derived-startup-playback.json) and [checked summary](Digitone-loader-derived-playback-summary.json).
