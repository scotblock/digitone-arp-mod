"""Document measured persistence and the required working-cache bridge."""
from pathlib import Path
import json
r=json.loads(Path('outputs/Digitone-E10-PC-storage-verification.json').read_text(encoding='utf-8'));assert r['passed']
text='''# E10 candidate storage: native save/load verification

17 October 2026. PC-only tests on separate emulator cards. E09A is unchanged; no E10 firmware container or machine-code persistence hook was created.

## Result

The proposed 32-byte record at kit-slot `+0x940..+0x95f` survives **native named-project saving, reloading, a fresh cold boot and then reloading the named file again**. All 128 distinct pattern records match.

It does **not** automatically survive the stock working-project cache path. Cold startup observed zeroes in all 128 candidate fields. The stock decoder ignores those fields, and the native encode/decode control demonstrates that rebuilding serialized kits from stock runtime data loses the extension.

This supports using the location for a versioned project-file extension, with explicit capture and emission helpers. It does not make the location self-preserving or establish ownership across every other writer.

## Tests and boundaries

1. **Native save/reload:** Started from E09A's established UI state and a private copy of its emulator card. Distinct valid diagnostic records were inserted only at native kit serialization completion during one Save Project As operation. The native workflow serialized 128 slots twice, in two different buffers. The probe changed only the proposed 32 bytes in each slot; all other bytes of each serialized kit were checked immediately unchanged. After native saving and flushing the card, the last serialization buffer was deliberately poisoned. Native loading recovered all 128 records before kit decoding.
2. **Cold working-cache restoration:** Rebooted a separate copy of the saved card using the existing loader-derived E09A state. No records or executable instructions were inserted. Startup completed the logo/UI transition. All 128 fields observed during the native project decode were zero. Independent reading of the saved working-project image also found all 128 fields zero.
3. **Named-project reload after cold boot:** Used that fresh native UI state and another private card copy. Explicitly selected slot 002 NEW PROJECT; cold startup had reset the selector to slot 001 PRESETS. Declined the save-before-load prompt, then confirmed proceeding without saving. Native decoding recovered all 128 records without host injection. This distinguishes stored file data from RAM left by the first test; queued panel requests or an unconfirmed dialog were not counted as a load.
4. **Stock decoder control:** Executed the real 128-kit conversion loop on cloned native kit fixtures, with and without the proposed records. All `128 * 0x988` runtime bytes were identical. Re-encoding those runtime kits into a fresh zero-filled project buffer left all 128 extension fields zero. No runtime arp-state restoration is implied by these storage tests.

The verified serialized project geometry is 128 kit slots of `0xa00` bytes. The stock encoder's observed write extent is `+0x90e`; the observed decoder extent is `+0x902`. The chosen location is beyond both extents and inside each serialized slot. Geometry and the normal conversion loops were established in the preceding kit-codec audit.

## What must be connected next

- Validate and capture each extension record during project decode, before stock conversion discards it. Bind the resulting bank to the actual loaded project and completed pattern transition.
- Emit the correct record on both named-project saves and working-cache rebuilds. Updating only the named-file route would leave cold-start restoration incomplete.
- Establish disabled defaults for blank, legacy or invalid records, and handle replacement/refusal before admitting a new pattern. The existing isolated record validator tests do not substitute for these adapters.
- Repeat native save, edit, reload and cold-start restoration with the actual machine-code helpers and no diagnostic data injection. Copy/clear/undo, asynchronous replacement and physical behavior remain separate scopes.

## Evidence

- `Digitone-E10-PC-storage-native-save-load.json`
- `Digitone-E10-PC-storage-cold-startup.json`
- `Digitone-E10-PC-storage-cold-reload.json`
- `Digitone-E10-PC-storage-stock-decoder-control.json`
- `Digitone-E10-PC-storage-verification.json`

The initial records are PC host fixtures, not integrated E10 firmware behavior. All card writes occurred on task-created copies. No physical Digitone or existing E09A firmware artifact was changed.
'''
Path('outputs/Digitone-E10-PC-storage-verification-notes.md').write_text(text,encoding='utf-8')
print('Documented named-file survival and stock working-cache loss separately.')
