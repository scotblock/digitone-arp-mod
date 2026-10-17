# E08E hardware-trial readiness review

**16 October 2026 update: this trial assessment is superseded by a confirmed menu-routing regression. E08E forwards ordinary parameter keys six page positions too far and its custom SYN2/page-marker guards are too broad. The user reported the effects pages before loading the generated test project. Do not use the older acceptance batch below as menu acceptance or as a recommendation to install E08E. A separate PC-only correction is under validation; the frozen E08E firmware bytes remain unchanged.** See `Digitone-E08E-menu-routing-regression.json` and `Digitone-E08E-PC-menu-fix-contracts.json` for the bounded reproductions/correction checks.

15 October 2026. **The selected PC acceptance batch is complete. E08E is a concrete candidate for reviewing a controlled M1-only experimental hardware trial. It is not hardware-certified. No device update occurred.**

## A real blocker was found and corrected

E08D's held live arp continued after panel Stop and a second Stop. Its normal descriptor consumer never received the synthetic kind-4 Stop descriptor assumed by the earlier isolated scheduler test. The actual stock task received outer command 4 at 854.356 ms, then commands 4 and 5 at the second Stop; these bypass the prototype's descriptor hook. Release still worked, but generation continued until then. This is why the new held-Stop check initially failed.

The corrected E08E package hooks the actual command-4 branch before stock drains outgoing notes. Its native helper stops M1 generation and clears live membership, preserves the owner identity and retains an outstanding arena descriptor for its normal retirement. Applying MODE OFF uses that clear too. Previously OFF left retained notes behind. The correction adds 114 bytes of native controls code inside existing padding, with no additional copied-memory extent or state compared with E08D.

## Checked on the exact final package

| Area | Result |
|---|---|
| Native instruction encoding | 80 custom executable regions / 3,094 decoded instructions checked against the ColdFire restrictions used by the project. |
| Owner guards and Stop bridge | Twelve owner-contract groups plus Stop/clear contracts pass. The bridge preserves registers, stack and incoming interrupt level, then replays the displaced stock instruction. COLD admission refuses mutation. |
| Container | Packet sequence/checksums, whole-container length/checksum/padding, compressed MAIN checksum and independent exact MAIN decompression pass. All non-MAIN sections remain stock. |
| Startup-menu DIN receiver/updater | Exact package received and simulated programming reaches `0x1b6200`; 5 modeled erases and 2,481 writes. Bad whole checksum, missing end and bad packet checksum produce no programming. Flash/display/geometry are fixtures; this is not a hardware transfer. |
| Packaged loader → copier → startup | Loader reaches MAIN; exact payload copy, native initialization and restored-project startup reach the UI through preserved modeled state. No physical flash/cache behavior is inferred. |
| Actual pattern handoff and fresh/released notes | 41 note-ons / 41 matched note-offs; receiving settings apply at the consumed context, without the earlier premature lead. |
| Complete incoming-pattern panel race | 35 matched note pairs; incoming edit is stored/notified, early publication is refused and its edited value applies 82.679 ms later at context consumption. |
| Stop, sustain and OFF → UP | 37 matched note pairs. Held Stop clears generation/membership; no late restart. CC64 holds released keys until pedal-up. OFF clears retained membership; re-enabling UP stays idle until fresh input. |
| Native project save/reload | Final E08E settings save, change and reload correctly at the same parameter-record address while quiescent. Owner matches the restored record. Existing MIDI fields and synth T4 data remain unchanged. |
| Diagnostic/reset refusal | Nine stopped native entry cases pass with no watched storage writes and balanced returns. These are explicit admission fixtures, not asynchronous reset evidence. |

Continuous playback uses the packaged machine code and native consumers. Mode/rate/gate edits and project actions use native panel input. These results retain emulator peripheral/ISA adaptations and use modeled timing. Separate loader/startup/playback checkpoints preserve modeled state; they are not physical boot captures.

## Placement and remaining physical questions

The payload is 32,256 bytes at `0x47be0000..0x47be7e00`, an increase of 13,820 bytes over E07. The old E07 payload prefix is unchanged except its cold-success continuation into M1 initialization. The stock cache-handoff bytes are unchanged; the actual modeled loader-derived entry has CACR `0x0008c000` with data cache/store buffer disabled.

The occupied range stays inside the existing `0x47be0000..0x47c00000` reservation, leaving 98,816 bytes. M1 state is 344 bytes, with an eight-byte gap before the unchanged 64-byte arena. This extends the bounded placement evidence; it is **not** proof of exclusive physical RAM/DMA ownership, cache coherence or worst-case timing. E07's reported physical success does not certify the additional range or new paths.

Other unproven cases include asynchronous live project-load/input overlap, all same-address record reuse, a queued old note crossing replacement, arbitrary warm copier/exception paths, shared-channel note ownership and congested/simultaneous synth/MIDI arps. The latest continuous runs use live MIDI input; internal sequencer-chord playback has not been repeated on this final package. M2–M4 arps remain unimplemented. The first proposed hardware trial is consequently limited to boot/basic controls and M1 live input on a separate output channel.

## Frozen review artifact and proposed next action

Candidate: [Digitone_OS1.44E08E_M1_ARP_PC_ONLY.syx](./outputs/Digitone_OS1.44E08E_M1_ARP_PC_ONLY.syx)

SHA-256: `74219ea223999ae190f5c935973b96bf67eea60148416a1009565af6f48dd3a3`.

Stock recovery: `stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx`, SHA-256 `d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`.

E07 and earlier PC candidates are preserved. The published review copy is byte-identical to the tested internal E08E package. Its `hardware_ready:false` status remains explicit.

The proposed next milestone is **an agreed, user-operated boot-only checkpoint using the previously rehearsed DIN startup update/recovery route**, then a bounded M1 live-note test if boot/basic controls pass. It is not unrestricted use. See [the trial proposal](./outputs/Digitone-E08E-proposed-hardware-trial.md) for scope, recovery and recording setup. The user has not yet approved this specific E08E installation in this turn; no tool has transmitted firmware.

Machine-readable consolidated evidence: `Digitone-E08E-hardware-trial-review-results.json`. Reproduction/freezing driver: `work/finalize-E08E-trial-review.py`.
