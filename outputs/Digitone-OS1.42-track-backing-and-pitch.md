# Track backing data and transposed pitch trace

Read-only analysis of original Digitone/Digitone Keys OS 1.42. No firmware bytes changed; no rebuilt or flashable image produced.

## Confirmed Track storage mapping

The RTTI name `5Track` is at `0x401b6679`. Its primary virtual table address point is `0x401764c8`, assigned by constructor `0x40034174` at `0x400341cc`.

Two table entries establish the storage access:

| Virtual byte offset | Target | Behavior |
|---|---|---|
| +0x24 | `0x40031c60` | Jumps to storage setter `0x4013a344` |
| +0x28 | `0x4013a33a` | Returns the pointer at Track object +0x10 |

The setter writes the new pointer to Track +0x10 and invokes virtual +0x10 with a zero second argument. The latter is treated as notification; its full semantics are not established here.

Binding routine `0x4001fc74` takes an owner object P and backing pointer B. After binding the owner's storage, its loop at `0x4001fcb4..0x4001fcd6` passes:

- Track object `P + 0x70 + 0x58 * t`;
- backing pointer `B + 0x3d0 * t`;
- through that Track's virtual +0x24 setter;
- for t = 0..7, ending at data offset 0x1e80.

This connects the previously separate object and raw-data strides. Constructors also initialize these eight Track objects, give each its index through `0x40031d48` (object +0x38), and its owner through `0x40031d2a` (object +0x3c). This index is not yet proven equivalent to every playback/arp channel identifier.

Root getter `0x40032550` and scale getter `0x40032816` call virtual +0x28, then read backing offsets +0x3cb and +0x3ce. Thus, for a bound Track t:

```
Track(t) = P + 0x70 + 0x58*t
Track(t).storage = B + 0x3d0*t
root_byte = *(B + 0x3d0*t + 0x3cb)
scale = signed_byte(*(B + 0x3d0*t + 0x3ce))
```

A null storage pointer makes the getters return root 60 and scale -1. The root getter returns a byte; its caller must handle byte extension correctly. The scale getter explicitly sign-extends.

## Active storage and bank lookup: narrower remaining question

Getter `0x40093b84` returns global pointer `*(u32*)0x41342150`. Getter `0x40093b72` reads a long at that pointer +0x16119. This is a concrete current-context pointer and index field; exact lifetime and selection semantics remain unverified.

Separate caller `0x400dc432` uses the returned index k to form:

```
B_candidate = 0x407b00cc + 0x1611d*k
T_candidate = B_candidate + 0x3d0*track_argument
```

At `0x400dc4aa..0x400dc4b8` it passes T_candidate's +0x3ce scale and +0x3cb root to membership function `0x40106b6c`, along with the note argument. That branch is conditional on a note-to-track lookup. It validates the raw layout, but does not prove that the live arp should always use this bank expression or that the active pointer is always identical to B_candidate. Pattern transitions and overrides still need tracing.

## Resolved: the checked transposed note reaches pitch processing

Earlier analysis found that allocation function `0x4009e720` receives the original note, while a separate sum was checked for 0..127. The later code now explains both paths.

At `0x4009df78..0x4009df98`:

```
n = unsigned_byte(event + 0x18 + note_index)
sum = n + *(s32*)0x80003fc4 + adjustment_table[channel_context]
require sum == (sum & 127)
```

The range-checked sum remains in d6, then `swap d6; clr.w d6` at `0x4009dfa4..0x4009dfa6` creates `sum << 16`. It is preserved in stack local -0x5c, and each allocated voice receives it at `0x4009e060..0x4009e066`:

```
*(u32*)(0x41345ebc + 4*voice) = sum << 16
```

The original note still goes to allocation bookkeeping; the adjusted note travels through this parallel pitch path.

The voice loop at `0x4009d532..0x4009d5ca` reads that table, adds a signed per-voice byte shifted by 16, and passes the result as argument four to `0x400f02b4`. That routine performs stateful fixed-point arithmetic, optionally rounds to whole units, stores its result at `0x4199d570 + 4*voice`, and returns it. The caller adds another fixed-point contribution and stores the result at owner +0x30 +4*voice.

This is strong evidence for a pitch-control path with 16 fractional bits, beyond the allocation records. It does not yet establish the complete oscillator/frequency conversion, the names of every pitch adjustment, or the units of every subsequent operand. The stateful difference calculations are consistent with pitch glide, but that label remains an inference.

## Implication for V1

Snapping only the common arp result at `0x40097818` cannot guarantee the sounding note stays in the selected scale: later transposition and pitch adjustments exist. We need to decide whether the intended rule applies before transpose or to the resulting musical note, then establish the correct track context at that point.

A patch remains premature. The safest next static target is the assignment and lifetime of `0x41342150`, together with the relationship between playback channel identifiers and the Track +0x38 index. This should establish which root/scale data the active arp must use, including pattern changes and overridden arp settings. After that, trace the remaining coarse pitch adjustments before choosing a snapping location. Preserve the arp's negative sentinel returns, disabled scale (-1), and note bounds.

## Verification

The source attachment SHA-256 remains:

`0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`

Evidence comes from bounded ColdFire disassembly and virtual-table/absolute-reference checks. Full control-flow recovery and execution on hardware have not been performed. Truncated listing tails and embedded data were excluded from these findings.
