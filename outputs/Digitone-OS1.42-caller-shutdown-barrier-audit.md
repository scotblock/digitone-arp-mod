# Digitone OS 1.42: caller shutdown barrier audit

Firmware is unchanged. The proposed trailer, initialization hook and reset guard remain unimplemented.

## Finding

The recovered callers use alternate audio handlers, but no complete pool-shutdown barrier has been established. In bounded execution, both the constructed exit callback and matched test-exit continuation reach the pool initializer while the alternate handler remains installed and the supplied caller interrupt mask is unchanged.

This gives a concrete distinction: normal audio queue consumption may be diverted by changing its vector, while interrupts, alternate audio processing and other tasks continue. That does not establish producer exclusion, complete record release or pattern-writer quiescence.

## Constructed callback lifecycle

The confirmed constructor at `400ae9fa` creates two callback lists on a subobject at parent `+38`. Registration through `400d6ee4` uses subobject `+34`; its invoker `400ae458` tail-calls `400d95cc`. Registration through `400d6ef0` uses subobject `+40`; its invoker `400ae45e` tail-calls `4009c802` and then normal setup.

The registration helper appends a 16-byte callable record. Exit dispatcher `400d6db6` walks the `+40` list, copies each callable through `4015a3ae`, invokes it through `4015a3e0`, and destroys the temporary. `4015a3e0` dispatches through callable `+0c`; the callback manager at `400ae502` handles copying/destruction of its empty closure.

For a controlled one-element exit list, actual callable-copy, manager and invocation instructions reach:

`400d6db6 -> 4015a3e0 -> 400ae45e -> 4009c802 -> 4009bcc6 -> 4009bcb8 -> 400f0504`

The test stops at initializer entry before its first mutation. Configuration word `401f21e0` is supplied as zero, so the conditional preparatory calls in normal setup are bypassed. A one-byte closure allocation return is explicitly supplied at the allocator boundary; the heap allocator is not executed.

At that boundary the supplied SR mask is still level zero, vector `400002fc` still holds alternate handler `400d924e`, and a controlled retained payload remains live. No queue-drain or reset-wrapper call occurred along the executed exit path. This does not establish that a real page transition normally retains that payload; it demonstrates that the local callback route itself supplies no such cleanup or ownership test under those inputs.

## Alternate-handler installation

Existing helper `400d95cc` installs `400d924e` in vector `400002fc` and timer callback `400d920c` in `400002b8`. It writes the same interrupt-priority value 5 used by normal setup. Actual helper execution preserves the caller's SR mask and does not modify the persistent pool owner.

The confirmed alternate-handler graph contains 177 instructions, buffer work and calls, ending through interrupt return. It is active processing, not a terminal handler. Its local graph contains no direct references to the recovered scheduler free heads, payload owner or pool-release helpers. That narrows direct use of those structures; it does not certify every called routine or all asynchronous accesses.

Normal setup reinstalls `4009c838` at `4009bd52`, after rebuilding pools. The exit callback does not replace or disable the alternate handler before the initializer. Any protection supplied by the surrounding UI scheduler or page transition must therefore be established separately.

## Test-exit command

Command text `#EXIT_TEST_MODE` is compared before the matched continuation at `4008afee`. That continuation clears `40253e80` and calls `4009c802`.

The earlier test-entry helper `4008dfd2` installs another alternate audio handler, `4008dce0`, and timer callback `4008d974`. Its confirmed handler graph contains 191 instructions and active buffer processing. The matched test-exit continuation was executed with that vector and a supplied SR mask of level zero; it reached initializer entry without changing either.

The whole-image exact-literal discovery for `40253e80` finds the test-entry store and test-exit clear only. This is not proof against computed aliases, but supplies no recovered direct MIDI-task read that makes clearing that flag a producer-shutdown mechanism.

String comparison, actual command delivery, full test-mode entry and task scheduling are not executed in this check.

## Barrier assessment

| Mechanism | Established | Still missing |
|---|---|---|
| Alternate audio vector | Replaces the normal handler on recovered entry helpers | Every transitive pool access and exclusion of other tasks |
| Exit callback dispatcher | Copies/invokes the registered setup callback | A caller-provided interrupt or scheduler barrier |
| Test-mode flag clear | Happens before normal setup | Producer exclusion and completion acknowledgement |
| Queue drain / retained cleanup | Absent from the tested local exit route | Complete template/cache ownership retirement |
| Common initializer entry | Available before any pool mutation | A verified quiescence condition for allowing reentry |

No existing complete shutdown barrier is verified by these routes. Nor does the absence of a local barrier prove a stock-device failure: the actual surrounding execution state and ownership preconditions remain unknown.

## Validation and next target

14 checks passed across three recorded executions totaling 94 instruction steps. Six confirmed-entry local graphs cover 504 instructions. The source SysEx and decoded image hashes remain unchanged.

These are bounded instruction executions with controlled callback/state inputs. They do not emulate the real UI scheduler, audio interrupts, MIDI receive task, DMA or full page-transition behavior. The custom interpreter remains independently unvalidated against ColdFire hardware.

The next focused target is the outer page-transition dispatcher that invokes `400d6db6`, and the task/interrupt state surrounding `#EXIT_TEST_MODE`. Look for a scheduler lock, an acknowledgement that producers have stopped, or a precondition that retained pool records cannot exist. Keep the proposed storage and hooks unimplemented until that evidence or an explicitly designed lifecycle contract is established.

Details: `Digitone-shutdown-callback-execution-results.json` and `Digitone-shutdown-barrier-graphs.json`.
