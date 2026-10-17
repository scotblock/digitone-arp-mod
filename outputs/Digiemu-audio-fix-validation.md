# Digiemu audio synchronization fix

A separate local launcher is available in `Digiemu-audio-fix/Start Digiemu.cmd`. It carries independent copies of the user’s stock and modified saved sessions, emulator source, dependency libraries and Tcl/Tk resources. The original installation is unchanged.

The emulator waits for an in-flight DSP render before software DMA channel 47 copies the 1 KiB voice buffer at 0x100003a0. Parameter writes, unrelated transfers and inline DSP execution do not wait. The actual SSRT transfer path is implemented in Python under both native and Python eDMA configurations. CSR-only starts, other transfer shapes and other devices have not been certified by this focused fix. Firmware machine code is unchanged.

35 regression tests passed, including copy-before-DONE ordering, the narrow barrier scope, concurrent wait completion and worker-error propagation. The actual launcher window initializes successfully; both cloned firmware entries report Ready. Separate live runs exercised the normal GUI emulator worker, background DSP, Windows WaveOut, native eDMA, PLAY/STOP and clean shutdown.

Recorded stock and modified streams had zero jumps above 0.02 full scale. Windows output opened and accepted audio, with zero dropped submissions. Live playback nevertheless underruns: the latest modified run rendered 9.424 seconds in 20.578 wall seconds with 37 underruns; the stock control rendered 10.369 seconds in 20.531 wall seconds with 43 underruns. Host load and scheduling vary. No claim of uninterrupted real-time playback or stock byte-exact audio across scheduling phases is made.

The next task is to profile main-CPU execution, DSP render time and barrier waits in the normal GUI worker to determine whether synchronization waits or general emulator throughput prevent real-time playback. Increasing prebuffer length cannot solve sustained production below consumption speed.

The final packaged-engine fixed-input replay also matches the clean inline reference byte for byte (134432 stereo frames), with pitches C, C, E, F, C and the production transfer barrier active.
