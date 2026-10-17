# E08 M1 native machine-code prototype

The M1 scheduler now executes as ColdFire instructions in the PC engine. Python no longer sorts notes, chooses steps, constructs generated descriptors or bypasses retirement. The native consumer hook, scheduler and retirement hook perform those operations. E07 is unchanged; no installable E08 was produced.

Code loading and configuration remain explicit PC fixtures. The native initializer clears and seeds the additional state in a temporary call frame; it is not connected to the firmware startup copier. This placement is outside E07's copied payload and is not certified for hardware.

## Results

- OFF: 3 note-ons / 3 matching note-offs; [60, 64, 67]; no hanging notes.
- UP_release: 8 note-ons / 8 matching note-offs; [60, 64, 67, 60, 64, 67, 60, 64]; no hanging notes.
- UP_stop: 4 note-ons / 4 matching note-offs; [60, 64, 67, 60]; no hanging notes.
- UP_live_release: 3 note-ons / 3 matching note-offs; [60, 64, 67]; no hanging notes.

13 isolated native contract groups passed: initialization, sorting/dedup, finite expiry, arena busy preflight, transport stop, live zero-gate sources and actual release descriptors, invalid timing configs, invalid notes, M2 bypass, eight-note bounds, clock wrap, consumer register preservation and ordinary retirement. All custom regions passed the retained strict ColdFire instruction checks.

## Descriptor ownership

The helper snapshots value fields and clears borrowed pointer/link fields in the retained template. One busy-guarded temporary descriptor links back to the original native descriptor. Its exact-pointer retirement hook clears busy and prevents the private descriptor entering the stock free list. Ordinary descriptors retain the stock push/free path. The continuous run ends with busy clear and all notes retired, and verifies native code remains unchanged in memory.

This proves bounded behavior of the PC-owned arena in these controls. It does not establish exclusive ownership of that address on hardware or coverage of every callback/reset route.

## Remaining integration

The overlay uses 1,096 code bytes, 320 state bytes and a 64-byte descriptor arena. E07's existing padding plan has only 340 fragmented bytes free, so this layout cannot simply be inserted there. A placement/copying/initialization design is still needed before packaging.

Step interval and output gate are positive configuration fixtures; live source gate zero means held, not an arp rate. Tempo synchronization, settings UI/persistence, sustain, partial release, pattern replacement, mute/reset, channel collisions and M2–M4 remain unresolved.

Next: derive the rate/gate settings from stock MIDI timing and establish an installation layout before a flashable candidate. Keep M1 scope until that integration is verified.

## Artifacts

- [Digitone-E08-M1-OFF-NATIVE-PC.mid](./outputs/Digitone-E08-M1-OFF-NATIVE-PC.mid)
- [Digitone-E08-M1-UP_release-NATIVE-PC.mid](./outputs/Digitone-E08-M1-UP_release-NATIVE-PC.mid)
- [Digitone-E08-M1-UP_stop-NATIVE-PC.mid](./outputs/Digitone-E08-M1-UP_stop-NATIVE-PC.mid)
- [Digitone-E08-M1-UP_live_release-NATIVE-PC.mid](./outputs/Digitone-E08-M1-UP_live_release-NATIVE-PC.mid)
- [Combined results](./outputs/Digitone-E08-M1-native-results.json)
