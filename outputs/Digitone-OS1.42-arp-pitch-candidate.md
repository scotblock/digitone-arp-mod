# Live arp pitch calculation: strong candidate

Read-only analysis has located **0x4009755e**, main-image file offset **0x9715e**, as a strong live-arpeggiator pitch-calculation candidate. No firmware was changed or rebuilt.

## Evidence

The function accesses a per-channel state record at `0x41344530 + 40 * first_argument`. It checks its timing/state value against the second argument, checks available-note state, and loads a settings pointer from state +0x20.

It advances the current step at state +0x00, compares against the signed settings byte +0x113, and wraps when necessary. This supports +0x113 as a zero-based last-step/length field. It tests that step's bit in settings word +0x114; a clear bit leads to a negative return. Thus the earlier candidate flag mask is strongly supported as a step-enable mask.

It reads settings mode +0x10f and performs note selection through several branches. Those branches update octave-cycle state using settings +0x111.

The common pitch path is at **0x40097818..0x40097836**:

1. Check selected-note value is nonnegative.
2. Read octave-cycle state from the state record's +0x1c.
3. Compute octave offset as `16 * cycle - 4 * cycle`, i.e. **12 * cycle**.
4. Add the current step index to the settings pointer.
5. Read a **signed byte** at settings +0x116 + step.
6. Add octave offset and step byte to the selected-note value.
7. Return in register d0.

This is direct evidence that the sixteen-step array participates in chromatic pitch arithmetic, rather than merely a UI representation. It does not alone prove whether the selected-note value is always a final absolute MIDI pitch or whether the callers apply further transposition.

Two other paths explicitly return **-2** or **-1**. These are control/sentinel values and must be preserved by any future scale constraint. Negative sums from the pitch arithmetic also reach the same return path; downstream handling needs care.

## Callers connect this to note state

Two direct absolute calls were found:

- instruction at **0x4009de8c**;
- instruction at **0x4009df52**.

Both test the returned d0 for negativity. For a nonnegative result, each stores its low byte into an object at +0x18 and marks field +0x14 active. A negative result disables that active state. The first caller also reads settings +0x112 through a duration lookup table, supporting that byte as note-length selection.

Nearby code reads note bytes, adds two additional values from global/channel tables, checks that the resulting value fits 0..127, and calls **0x4009e720**. Its connection to both arp-return branches needs full control-flow verification; it nevertheless establishes that later pitch adjustment and bounds handling exist in this region.

## Why this matters for scale lock

We have now located the essential `selected note + octave displacement + signed arp step` calculation and callers consuming its result as note state. This is substantially stronger evidence than the UI references.

It is not yet a safe patch location. A scale constraint placed inside the calculation might be invalidated by downstream transposition. The remaining task is to trace the caller's full note-output flow and musical key/scale storage, then decide where to constrain the final pitch while preserving disabled steps, timing, note duration, and sentinel values.

The next concrete targets are callers around 0x4009de8c / 0x4009df52 and output helper 0x4009e720, alongside references to the musical-scale tables. No scale quantizer has yet been identified.

Analysis limitations: targeted Capstone ColdFire disassembly, bounded windows, static evidence only. Matching small displacement constants alone was used to find candidates, not to identify all similarly offset fields as arp settings. The combined use of mode, octave, mask, step length, and signed step array in this function is what makes the identification strong.
