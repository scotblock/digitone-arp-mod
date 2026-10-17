# OS 1.42: continuous startup, playback and reserved RAM

The reserved-RAM route survives the exercised stock OS 1.42 startup and playback paths in the PC model. No observed guest write or monitored host write touched `47be0000..47c00000` through any of its eight DDR aliases. A test pattern covering the complete 128 KiB interval remained byte-identical at every checked stage and at the end of playback. The proposed code and metadata occupy only `47be0000..47be1b74` inside that interval.

This is stronger runtime evidence than the earlier direct-reference screen. It is **not global ownership certification**, and no mod was installed in this run.

## Execution reached

The pinned Digiemu engine resolved its required symbols from the actual 1.42 image. A workspace-only experimental product profile identifies the original file by its exact SHA-256. It is not an upstream-supported 1.42 profile and does not reuse 1.43 application addresses blindly.

Stock code ran from the application entry through the scheduler and thread startup, the intro and a live interface. First-boot completion passed the emulator's card checks and the actual DSP-running status check (`2`). The stock note-pool owner was `419c38c0`; all 64 records had valid stock links in both cold-start and post-intro snapshots. The earlier fixture's fixed `419a38c0` owner is therefore not the address this full startup produces. Future hooks must continue deriving it from `*(4199d590)`.

The model initially received boot flags `00140000` as an explicit entry fixture; stock code subsequently stored `00140004`. The pre-OS bootstrap was not executed. The earlier 128 MiB geometry decode still supplies the DDR alias model.

A first detailed run sampled every 64th basic-block entry and scheduler switches. It reached a live interface and part of first-boot setup, then stopped at its wall-time bound. A lighter continuation replayed from the saved post-intro state and finished setup. These are guest-state continuations across snapshots, not one uninterrupted engine or a continuation from the cancelled instruction. The aggregate stack-sample count includes that repeated setup work.

## Playback and pattern switching

The initial Play/Stop session covered 2.1 emulated seconds. A separate session from the settled snapshot covered **10.07 emulated seconds**, including Play, track/trig inputs, PTN+2, PTN+1 and Stop.

The stronger playback session produced:

| Observed behavior | Evidence |
|---|---|
| Transport starts and stops | Resolved transport word changes `0 → 1 → 0` |
| Pattern changes occur | Current backing changes `407b00cc → 407c61e9 → 407b00cc`; its data digest changes and returns |
| Actual note production executes | 20 hits at `40093ef4` |
| Actual event allocation executes | 1,594 hits at `400f0626` |
| Actual note acceptance executes | 21 hits at `4009dd80` |
| Actual coarse-pitch site executes | 31 hits at `4009df9a` |
| All four track IDs appear at the pitch site | Track 0: 7; track 1: 3; track 2: 11; track 3: 10 |
| Synth audio is nonzero | 965,881 nonzero 16-bit samples; RMS about 1,957 |
| Candidate storage remains intact | Zero watched region writes; full-region digest unchanged |

Delivered track inputs alone do not prove every live-note mode. The track coverage above comes from the event IDs actually read at the pitch site. These stock note-path hits do not prove that every cached/live/held arp branch executed, or test the proposed scale-lock helpers in this continuous engine.

## Stack observations

The stock task-creation routine supplies each stack's lower address and size; its size is rounded down to a four-byte multiple. All **14 observed task-stack intervals** are disjoint from the candidate physical region. The recorded observations contain **4,662,995 SP samples** across the startup/setup and initial playback runs, plus 3,368 scheduler-boundary samples in the switching session.

The lowest sampled entry/startup SP in the high stack was `47ffffcc`, leaving **4,194,252 bytes** above the candidate region's end. Task-stack samples were in their separate lower RAM allocations. These are finite observed minima, not worst-case bounds: unsampled temporary SP changes, future tasks, exception paths and other device states remain unproven.

## Probe reliability and remaining limits

The standard Unicorn 2.1.4 library failed Digiemu's correctness guard before firmware execution. The pinned upstream CCR and EMAC fixes, together with its speed patches, were built locally from Unicorn commit `8028ec436f2d9376525352dd38ed9ed6b9f6be10`. All six patch hashes match the pinned Digiemu installer. No system Python package was changed.

The rebuilt engine passed all five compatibility cases and eight upstream memory-hook routing tests. An additional 18 assertions checked computed writes through eight aliases, shared backing bytes, bulk MOVEM writes and a store straddling the lower boundary. That last check exposed a watch-range routing gap; the probe now watches a 64-byte margin around each alias and filters actual access overlap. Exact write PCs are retained.

The firmware still runs under model conditions: flash-read shortcuts, completion stand-ins, idle reschedules and accelerated UI/float routines. Ordering, physical cache coherence and hardware DMA are not certified. Native DMA can bypass individual Python write callbacks; full-region digests check its persistent effects at progress boundaries, but cannot exclude transient writes that restore the original bytes. The probe watches writes, not every read, so possible sentinel-dependent behavior also remains a limitation. The lighter setup and playback runs report zero decompression clamps and zero forced generic wait completions, although specific completion and idle stand-ins remain active.

No executed-path result excludes unvisited computed pointers, bulk copies, project loads, modes, error cleanup, longer sessions or hardware-specific behavior.

## Next focused step

Connect the previously tested boot copier, separate metadata initializer and arp helpers as **ephemeral CPU-memory overlays in this same engine**. Keep the source firmware unchanged and watch the reserved interval while exercising actual arp producers, sustain, queued notes and pattern changes. Separate expected helper writes from unexpected stock writes, verify failure/reentry behavior, and observe the resulting constrained pitches. This will test the integrated design against the real producer/scheduler path rather than supplied finalization boundaries.

Evidence files: [startup/setup and first playback](Digitone-continuous-RAM-watch-results.json), [playback and switching](Digitone-playback-switch-RAM-watch-results.json), [stack intervals](Digitone-continuous-stack-range-audit.json), [stock initialization snapshots](Digitone-continuous-startup-state-audit.json), [CPU compatibility](Digitone-local-CPU-compatibility.json), [native watch tests](Digitone-native-write-watch-tests.json).

The engine source is pinned to [Digiemu commit 24a1dcf](https://github.com/irpina/digiemu/tree/24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2); its [patch documentation](https://github.com/irpina/digiemu/blob/24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2/patches/README.md) explains the fixes and limitations.

Original SysEx and decoded main-section hashes remain unchanged. No firmware was repacked, no flashable mod was produced, and no device I/O occurred.
