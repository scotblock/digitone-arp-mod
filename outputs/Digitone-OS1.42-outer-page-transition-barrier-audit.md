# Digitone OS 1.42: outer page-transition barrier audit

Firmware remains unchanged. No context trailer, setup hook or guard has been implemented.

## Result

There is an existing page-manager mutex around the exit callback. It serializes operations using that mutex, but does not keep interrupts masked while callbacks run or establish that note producers and retained payload owners have stopped.

Bounded execution now includes the outer page-removal dispatcher and actual mutex acquisition, rather than entering the exit callback directly. Both uncontended and recursive acquisition reach the pool initializer with the supplied caller mask restored, the alternate audio vector still installed, and a controlled retained payload still live.

This closes the local question of whether the recovered page dispatcher hides a sustained interrupt mask. A complete system-wide shutdown barrier remains unverified.

## Outer dispatcher and callback order

Page processing at `400d7dfe` takes the manager mutex at manager `+4`. Pending removal leads to `400d7d50`, which takes the same mutex and walks the manager's page-node list. This is compatible with recursive acquisition by the same task.

The removal loop reads a page's close-request byte through `400d6baa`, which returns page `+30`. For a marked page it invokes virtual slot `+1c` at `400d7db4`. The constructor-installed subobject table `401a3ba8` resolves that slot to `400d6db6`, the exit-callback-list dispatcher.

The resulting recovered route is:

`400d7d50 -> virtual +1c -> 400d6db6 -> callable invoker -> 400ae45e -> 4009c802 -> setup -> 400f0504`

Node unlinking and destruction occur after the exit callback returns. The page-manager mutex is released later through `4012f8e8` at `400d7dec`. Therefore at pool initializer entry the callback is still inside the page transition, and its page node remains linked.

An explicit page-removal route at `400d7bcc` also acquires the manager mutex before virtual exit at `400d7c3a`. Its local graph supplies no separate audio-pool ownership condition.

## What the mutex protects

RAII acquisition helper `4015a5e2` calls kernel mutex acquisition `40001a4c` and records ownership of the guard. The kernel helper briefly raises SR to `2700` to update the lock's owner/waiter fields.

On an uncontended lock it assigns the current task from `429a39a8`. If that task already owns the lock, it increments the recursion count. Other-owner contention can enqueue the task and execute a scheduler trap. At `40001aa4` it restores the saved SR before returning.

Guard destruction uses `4012f8e8 -> 40001b6e` to release the mutex, again using a temporary interrupt mask around lock bookkeeping. These are task mutex operations, not an instruction sequence that keeps every other task or audio interrupt disabled throughout the exit callback.

Other tasks that acquire the same manager mutex can be excluded while it is owned. Establishing producer exclusion would require evidence that each relevant producer shares that lock or is separately stopped. No such contract is demonstrated by these local graphs.

## Executed outer-route checks

The PC harness supplies a one-node manager list, the constructor's actual subobject vtable, one registered exit callable, a current-task pointer, entry SR `2000`, and configuration word `401f21e0=0`. It executes the actual removal dispatcher, actual uncontended/recursive mutex code, callable-copy/manager/invocation code and setup path, stopping at initializer entry before pool mutation.

For both acquisition cases:

- The virtual exit resolves to the actual callback dispatcher and then pool setup.
- The manager mutex is owned by the supplied current task, with the expected recursion count.
- SR's upper byte is restored to `20` before the callback reaches setup.
- The alternate audio vector remains `400d924e`.
- A controlled retained payload has count one and retains its pointer.
- The page node remains linked during the callback.
- Neither tested acquisition enters the contention/scheduling trap.

The retained record is a deliberately supplied negative control. These executions do not prove that real page entry permits such a retained record; they show that the recovered outer callback route itself does not test or retire it before pool setup under these inputs.

The one-byte empty-closure allocation return is supplied explicitly. The heap allocator, real UI scheduler, audio ISR, MIDI receive task and peripherals are not executed.

## Producer-stop conditions

The recovered close-request condition is a page byte, not an acknowledgement from the audio or MIDI tasks. Pending manager flags trigger page work; their local graphs contain no direct test of the payload owner, scheduler queue head, retained templates or live record counts, and no queue-drain call.

The manager lock's contention path may suspend a waiting task, but acquiring the lock does not establish suspension of all other tasks. Restoring the caller SR likewise preserves any protection supplied by an earlier caller; it does not prove that earlier protection exists. The actual upstream UI task's state remains a separate question.

Accordingly, the recovered manager mutex is useful evidence of page-list serialization, but cannot serve as the proposed pool-reinitialization guard's complete quiescence condition.

## Validation and remaining decision

16 execution assertions passed across two cases totaling 269 instruction steps. Twelve additional structural/hash checks passed; eight confirmed-entry local graphs cover 286 instructions. Original SysEx and decoded image hashes remain unchanged.

Normal-return graphs do not certify exception cleanup. Contended mutex acquisition, scheduler traps and complete page-transition task execution were not tested. The custom interpreter is not independently validated against ColdFire hardware.

The next meaningful target is whether entering these alternate audio/test modes establishes a stronger precondition before exit: no live payload records, no retained arp templates, and input producers disabled or acknowledged stopped. This requires tracing the mode-entry paths and the receive-task gates, rather than treating the page mutex as a complete barrier. Keep the proposed allocation extension and hooks unimplemented.

Details: `Digitone-outer-page-transition-execution-results.json` and `Digitone-outer-page-transition-graphs.json`.
