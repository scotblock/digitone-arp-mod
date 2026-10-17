# Digitone OS 1.42: active writer ownership and update protection

**Follow-up:** [Interrupt capture and writer consistency](Digitone-OS1.42-interrupt-capture-and-writer-consistency.md) resolves the input task's initial SR and the audio service source/level. The task starts at CPU mask 0 and audio is forced at level 5. The recovered paths support preemption between stores; unrelated global gating and broader writer coverage remain uncertified.

**The restore/reset writers can address the active receiving pattern in the recovered canonical-bank install path.** They are not restricted to inactive scratch copies. Their backing getter is a plain pointer load. The input queue has a short interrupt mask, but restores it before UI dispatch; it does not protect the complete metadata update. No complete-update guard has been established in the recovered dispatch chain. This is not a demonstrated hardware race: inherited interrupt state and audio-callback gating still require verification.

No firmware was modified, rebuilt, repacked, transmitted or flashed.

## Backing ownership resolved

The three writer functions from the preceding audit (`40034a8c`, `40034c78`, `40035268`) receive a track object obtained through `400237b0`.

1. Startup at `40015bc2..40015bc8` passes project backing `407b00b0` to `4002235a`, which stores it in `40507e2c`.
2. Manager getter `4012f97a` uses that backing when constructing the object with `40027b86`. Base constructor `40136658` retains the backing at object `+10`; manager construction calls `40022432` to bind its children.
3. Binder `40022366` binds 128 pattern objects to `P + 1c + 1611d*k`, where P is the manager backing. The pattern-object stride is `38c`; this is distinct from the backing stride `1611d`.
4. Pattern binder `4001fc74` binds eight track objects to `B + 3d0*t`. Track-object stride is `58`; backing-track stride is `3d0`.
5. Constructor `40034174` installs track vtable `401764c8`. Its slot `+24` points to `40031c60 -> 4013a344`, which installs backing in object `+10`. Slot `+28` points to `4013a33a`, which simply returns that pointer.

The storage getter is fully recovered:

```
4013a33a  movea.l  4(sp), a0
4013a33e  move.l   10(a0), d0
4013a342  rts
```

It neither copies storage nor acquires protection. The restore/reset writes therefore modify the selected object's actual backing bytes.

## Which bank the UI writers select

`400237b0` selects a track under the pattern object returned by `4002377a`. That selector obtains an index through `400a9ca4 -> 40093b72`. The latter reads:

```
active = *(41342150)
k = signed_long(active + 16119)
```

The UI route clamps k to 0..127 and selects the canonical pattern object for that index. Its resulting writer address is:

```
W = 407b00cc + 1611d*k + 3d0*t
root address  = W + 3cb
scale address = W + 3ce
```

This is an index selected from the active receiving pattern, followed by a canonical-bank lookup. It is not a direct dereference of the active pointer for the eventual stores.

The recovered install route makes overlap concrete: `400eea88` constructs an installation descriptor with a bank address computed at `400eeb08..400eeb14` as `407b00cc + 1611d*index`. `400eeb82` or `400eebfc` copies that descriptor into call arguments and calls `4009461c`. The install routine stores its first argument into `41342150` at `40094652`.

For a canonical installed bank whose embedded index identifies the same k, the writer's W is exactly the receiving track backing. Thus an active root/scale update is supported by the static paths; treating these writers as always offline is unsound.

The distinction still matters during changes:

| Receiving state | Consequence |
|---|---|
| Canonical bank, same index | Writer and receiving fields alias |
| Alternate backing with the same embedded index | Writer still selects canonical storage; equality is not established |
| Pattern transition before UI selection | Selection can use the new active bank's index |
| Transition after track-object selection | The selected bank can become inactive before stores finish |

The recovered binding proves the normal address relationship. It does not prove that the manager can never be rebound later, that every installation uses canonical storage, or that an embedded index cannot be invalid. Missing/out-of-range metadata must not be used to justify snapshot ownership.

## Protection scope traced

The UI screen constructor installs vtable `401a4958`. Slots `+34` and `+38` resolve to `400b6d92` and `400b6e7a`, whose calls reach the three metadata writers.

The recovered input route is:

```
event loop at 400171e2
  -> queue pop 40001d6c
  -> event construction 4001729e
  -> input dispatch 400172a8 -> 40014678
  -> dispatcher 400d8180 -> 400d7dfe
  -> callback 400d6efc -> screen virtual slot +08
  -> 400b6f62 -> tail dispatch 400b71a6 -> 400d6974
  -> screen slots +34/+38 -> restore/reset writer
```

`400d6974` selects slot `+30` for input code `0a`, slot `+38` for `0c`, and slot `+34` for `0b`, after its input-state predicates. These codes are reported as recovered numeric dispatch values, not assigned user-interface labels.

There **is** an explicit queue-pop guard: `40001d8e` saves SR, `40001d90` sets SR to `2700`, and `40001dbe` restores the saved SR before returning at `40001dc8`. It protects queue bookkeeping only. It does not leave interrupts newly masked for the subsequent writer call.

No explicit SR mask spanning the metadata writes was found in the recovered input/dispatch functions, screen handler, direct writer callers or writer functions. The resolved storage getter contributes no lock. Track slot `+10` leads to `4003514a -> 4013b2d4`, a notification route called after the stores; that call is not evidence of protection during the stores.

**What remains unknown:** the interrupt state inherited by the input task; whether some outer system mechanism suppresses the audio callback throughout UI dispatch; the callback's actual interrupt source/priority and scheduling relationship; and the behavior of other indirect callbacks. Those cannot be inferred from the absence of a local SR instruction. This audit therefore rules out the queue-pop mask and backing getter as complete-update protection, but does not prove that no global protection exists.

## PC checks and next step

Eight specification scenarios pass, including 1,024 canonical bank/track address comparisons, alternate-backing distinction, transitions before/after selection, and queue-mask scope. Twenty byte anchors were independently checked against decoded section 3. The tests do not execute firmware or establish scheduling.

The writer consistency gate remains open, now narrowed to a concrete execution-context question: trace the input task's inherited SR and the audio callback's installation, entry/return and any suppression mechanism. Establish whether capture can execute between these active-bank stores. If it can, a reader-only guard is insufficient and a writer-side consistent-commit mechanism must be designed and tested on the PC. Do not implement a firmware hook yet.

Original SysEx SHA-256 remains `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`; decoded section-3 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
