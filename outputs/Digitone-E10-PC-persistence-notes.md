# E10 native project persistence bridge

17 October 2026. Separate PC-only decompressed image. E09A remains unchanged; no E10 firmware container or release was created.

## Result

The new machine-code helpers capture all 128 M1 pattern records during native project decoding and emit them during native project serialization. The native named-file workflow and retained RAM mirror rebuild both preserve all 128 distinct records without the test runner inserting bank data or calling the capture/emission helpers.

An explicitly invoked **stock retained-cache writer** then wrote the updated mirror to the alternate storage bank and invalidated the previous bank. A separate cold PC boot from that resulting card restored all 128 records through the new native capture hook and reached the user interface. This is a native write/reboot control, **not proof of automatic power-loss handling or hardware persistence**.

Playback regression from the copied persistence image also passes: the panel-created four-step program uses scale-degree offsets and a rest, produces 23 matched note-on/off pairs on each port, and has identical DIN/USB note messages. This playback programs active state; it does not yet recall the saved bank.

## Implementation

- Capture hook: native 1.44 project decoder at `0x4000e98a`, after the 128-kit conversion loop. A3 supplies the serialized project and A4 its runtime owner.
- Emission hook: native project encoder at `0x4000ecc0`, before the kit loop. A3 supplies the destination and D3 the runtime owner. The observed stock kit encoder does not reach the proposed record at kit `+0x940..+0x95f`.
- The record bank remains at `0x47bee000` (128 records × 32 bytes). Added helpers start at `0x47bf0000`; ownership metadata is at `0x47bf1000`. The copied payload is 69,664 bytes. These addresses are PC candidates; exclusive physical RAM ownership is not established.
- Capture validates version, bounds, checksum and field ranges. Blank/invalid records become absent defaults. Capture requires cold or LIVE admission and a quiescent M1 state; refusal invalidates bank ownership without changing bank bytes.
- Emission requires the captured runtime owner. A foreign owner receives zero extension fields, including when its serialization buffer was previously used for another project. Emission does not bind that foreign owner.
- Helpers preserve the caller's registers and interrupt status, and mask interrupts while publishing/copying the bank. Native ColdFire instruction checks pass. Physical masking cost and whole-project replacement synchronization remain uncertified.
- Copied metadata starts invalid/zero. Native cold initialization establishes the empty bank before the project decoder supplies saved records. No runtime pointers or UI cursors are serialized.

## Working-copy finding and corrected interpretation

The earlier cold test read an old `COKI` retained-image fixture at storage `0xf400000`. A normal named save rebuilt the RAM mirror at `0x40555ee4` and wrote updated named files, but did not itself call the retained-bank writer during the observed session. Therefore the unchanged old bank was not sufficient evidence that the new emission hook lost records.

The new test observes 128 matching records in the native rebuilt RAM mirror, with selected bank 0 and pending bank 1. In a separate PC control, stock entry `0x400a8182` writes the complete mirror to bank 1 (`0xf800000`) and invalidates bank 0. The harness supplies only a disclosed native call frame; it does not write record bytes, bank-selection metadata or storage-controller results. A fresh boot selects and decodes that written copy successfully.

The ordinary automatic shutdown/power-fail route was not triggered by this control. It must not be described as a verified physical shutdown/reboot cycle.

## Evidence and boundaries

Six passing reports are consolidated in `Digitone-E10-PC-persistence-verification.json`: helper contracts, cold startup with absent records, native named load/save, explicit stock cache write, cold restoration after that write, and playback regression. The input named file contains the previous audit's diagnostic records; these tests preserve existing records rather than generating them through the step editor.

The engine/editor and the saved bank are **not yet connected**. Next: bind completed project/pattern selection to the appropriate bank slot, publish editor changes into that slot, and test two different patterns across edit/save/reload. Copy/clear/undo, incremental writes, asynchronous replacement and reset/refusal need their own adapters or checks. All startup tests use direct MAIN with unchanged E09A DSP/resources; no E10 container/loader continuity or hardware readiness is claimed.
