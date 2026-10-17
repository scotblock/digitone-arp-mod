# Digitone OS 1.42: producer, copy, and remap verification

The traced firmware paths **do not fully satisfy the earlier PC model's assumptions**. The relevant full-event copies preserve the proposed eight context bytes, but cached synth notes use type 1, and continuing remapped arp ticks skip destination setup. Those findings require a revised integration design. Stock firmware does not initialize the proposed metadata, and storage ownership remains unproven. No firmware was modified, rebuilt, or sent to hardware.

This is static analysis of the decoded section-3 ColdFire executable, using its existing address mapping, plus bounded PC specification tests. Addresses below are executable addresses, not offsets into the SysEx file. This report supersedes the type-zero-only assumption and the assumption that every remapped tick can acquire binding through destination setup in the earlier event-context report.

## Producers and recycling

| Path | Firmware evidence | Consequence for the proposed context |
|---|---|---|
| Fresh sequencer note | `40093c26`; fresh allocation at `40093e82` | Synth event type 0. Capture context from the explicit pattern/track inputs at construction; initialize or invalidate on every path. |
| Cached sequencer note | `400942ea`; cache at `419a304c + 72*track`; synth construction call at `40094456..40094476` | The same producer receives the existing cache event and current pattern pointer `41342150`. At `40093e72..40093e7e`, the reused-cache branch writes event type **1**. Context and pitch guards must admit types 0 and 1. |
| Cache emission | `40093442..4009344e`, `40093888..40093892` | Full 72-byte copies preserve a snapshot already initialized in the cache; they do not independently capture current settings. |
| Held-note template | `400efa20`; per-note template at `431d1758 + 0x2a18*track + 0x414 + 0x48*note` | Construction uses type 0 and does not initialize `+20..+27`. Template refresh must initialize context before any selected-note copy. |
| Held-note selection/replacement | `400efbe0`, `400efc08`, `400efc2a` | Three observed full 72-byte copies preserve those bytes, including old snapshots already queued independently. |
| Queued live on/off event | `400eff9c..400efffa` | Constructs an event with flags `0x30601`, one note, track/source identity and raw note. On/off state depends on the queue entry. It does not initialize the candidate bytes. Capturing the correct root/scale at the upstream queue producer remains a separate target; do not assume this late constructor still has the original pattern context. |
| Pool allocation | `400f0626` | Clears `+44`, `+38`, `+30`, `+2c`, and type `+00`, but not `+20..+27`. A valid stale tag can survive recycling. |
| Pool/held resets | pool linking `400f0504`; held resets `400ef9d0`, `400ef9f6` | Pool linking does not initialize context. The held resets clear selection state/head pointers, not all 72-byte templates. Startup or reset clearing alone cannot replace per-producer initialization. |

The dispatcher at `4009cb98` handles types 2 through 6 separately and sends both 0 and 1 through the shared synth-note path at `4009ce78`. Type 1 is therefore a real synth-note variant, not an unsupported event to discard. Generic copy/free payload handling distinguishes type 0; widening context eligibility does not justify changing payload ownership or reference counting.

The audit supports byte preservation at these concrete copy sites. It does **not** prove that all direct or indirect producers and consumers have been found, or that `+20..+27` are globally unowned in both synth variants.

## Actual remap and arp order

For the ordinary synth note-on path (on/off field `+04 == 1`, low parameter-only flag `0x2` clear):

1. At `4009dc5e..4009dc94`, the dispatcher tests remap flag `0x40000`. An already-remapped event bypasses destination-mask fan-out.
2. An unremapped event obtains a destination mask through `4009f23c`. At `4009dcdc`, it calls copy helper `4009bd8a` for each set destination bit **before the original's arp setup**.
3. The helper copies all 72 bytes, clears copied `+2c`, `+30`, and `+38`, writes destination to `+08`, sets `0x40000`, writes the former playback track to source field `+3c`, and links the copy through `+44`. It preserves existing arp flag `0x80000`, identity `+40`, and candidate context bytes `+20..+27`.
4. Original processing resumes at `4009dd48`. At `4009dd4e..4009dd58`, an event already carrying `0x80000` jumps directly to `4009df4a`, bypassing setup. Otherwise destination settings are selected and `4009719e` is called at `4009dda6`.
5. The existing-arp branch passes identity `+40` and playback track `+08` to `4009755e` at `4009df52`. A negative result skips note output; a valid result supplies the selected note at `4009df5e`.
6. The linked-event continuation at `4009cef0..4009cefe` processes the copies. The helper inserts at the head, so the mask's ascending insertion order is visited in reverse after the original.

**Initial notes:** copies are made before the source event is marked as accepted arp output. Each ordinary destination copy can therefore reach its own setup and obtain accepted destination state, subject to mode/priority/acceptance conditions. Destination setup cannot be assumed to accept every copy.

**Continuing arp ticks:** the copied source tick already has `0x80000` and the source identity. Its destination copy preserves both and goes directly to destination-track arp note selection. Per-track identities can coincide, so that selection may succeed using the destination's existing arp state. The incoming copy still carries the source's binding. The previous strict incoming-context guard rejects that copy and loses scale-lock coverage despite valid stock arp output.

Forcing setup on these ticks would change the observed stock lifetime and priority behavior. The safer proposed design is to obtain context from the **playback track's accepted retained template after successful arp selection**, with active-state, identity, binding and event-type checks. Incoming candidate context remains relevant when a new setup is accepted; it is not authoritative after a copied continuing tick selects another track's arp state. This is an integration proposal, not yet a proven hook or firmware implementation.

The observed already-remapped branch suppresses a second fan-out in this route. The earlier nested-remap model case remains a defensive hypothetical, not evidence of nested routing here.

## Release routing

The second traced call to `4009bd8a` is at `4009e2ba`. The release path at `4009e274` checks the remap flag; an unremapped release uses the previously saved destination mask at `413463b0`, emits copies, then clears that mask. An already-remapped release bypasses further fan-out.

At `4009e2cc`, `4009743e` receives playback track and the raw note byte for arp removal. Subsequent voice release also depends on original note/source identity. The scale hook must preserve those allocation/release fields and must not snap the raw event note used for lifetime matching. Retained metadata must become unusable when the accepted state is cleared; exact storage writes and concurrent reset ordering remain to be proved.

## PC checks and limits

The corrected event-context harness passes **15 scenarios**, **92,160 encoding round trips**, and **64 single-bit corruption checks**. It now accepts synth types 0 and 1. The original behavior harness still passes **10 scenarios and 4,608 quantization cases**.

The new bounded route adapter passes five checks:

- Initial fan-out reaches destination setup with fresh identities.
- Continuing fan-out skips setup and reproduces the prior binding-guard coverage gap.
- The proposed retained playback-track context handles matching-identity fan-out in the bounded model.
- The remap flag suppresses repeated fan-out through this route.
- Replacing destination state rejects a copied old identity.

These tests reproduce the traced flag, copy, and routing decisions; they do not execute the firmware. Successful arp selection is an explicit model input. Note selection, voices, interrupt interleaving, scheduling, identity wrap, payload reference counts, and CPU execution are not emulated. Passing the retained-context alternative does not establish storage safety or a usable insertion point.

Files: `digitone_firmware_route_checks.py`, `Digitone-firmware-route-check-results.json`, the corrected `digitone_event_context_model.py`, and `Digitone-event-context-model-results.json`. Keep the accompanying behavior model and scale-map JSON beside the scripts. The scripts are PC-only and produce no firmware.

## Safest next target

Trace the successful `4009755e` return through final coarse-pitch calculation and establish a guard that reads the correct playback-track retained state without altering stock setup or release behavior. In parallel within that static audit, locate the upstream queued live-note producer where source pattern root/scale are still available. Close type-0/type-1 byte ownership, all initialization paths, reset atomicity and identity wrap before selecting any storage or writing a patch.

## Unchanged inputs

Rechecked after the PC tests:

- Original SysEx SHA-256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.
- Decoded section-3 SHA-256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.

Both match the prior analysis. Only analysis documents and PC model files were changed.
