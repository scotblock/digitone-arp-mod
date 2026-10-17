# Digitone OS 1.42: modeled startup completion responses

## Finding

The focused SPI and UART completion tests cover successful responses, delayed readiness, incomplete responses, missing completion, mismatches, and recovered UART timeout handling. The stock timer handler can supply the signal that lets the modeled second-thread setup reach the constructor table. That same state then executes all 119 constructors and 999 stock allocator entries while preserving the proposed allocation and owner pointer.

This does not close the complete application-startup lifetime audit. After the UART version query returns, the executed continuation enters stock asset decompression. It has not yet reached the wrapped initializer. No tested path provides evidence that the proposed allocation is overwritten; equally, the unexecuted remainder cannot be certified from these results.

## Response cases

| Path | Supplied response | Observed stock behavior |
|---|---|---|
| SPI reader at `400ece52` | Receive ready and completion asserted | Copies exactly 17 supplied bytes; neighboring guards remain intact |
| SPI reader | Readiness delayed for three polls | Completes the same exact copy |
| SPI reader | No receive, truncated receive, or no completion | Continues polling until the PC fixture stops execution |
| Checked UART transaction at `4009f3b4` | Exact five-byte echo, immediate or delayed | Returns `0` |
| Checked UART transaction | Mismatched echo | Returns `-1` |
| Checked UART transaction | No echo or only three bytes | Executes the stock timer-based timeout and returns `-2` |
| Checked UART transaction | Transmit never ready | Polls until the PC fixture stops execution |
| Startup version query at `4009f5c0` | Accepted identity/platform and version 5, matching the image | Returns `-3` through the already-current branch |
| Startup version query | Wrong identity | Returns `-1` |
| Startup version query | Wrong platform | Returns `-2` |
| Startup version query | Truncated response or transmit never ready | Polls until the PC fixture stops execution |

The return values depend on the routine: `-2` in the version query means platform rejection, while `-2` in the checked transaction is the timer timeout. The recovered short version receive has no equivalent local timeout. A `FixtureWait` exception is a test execution bound, never a firmware-generated timeout.

## Integrated startup

The SPI fixture serves bytes from the unchanged official container at external-flash address `80000`. Reads outside that container, including the 20-byte read at `40004`, use explicitly synthetic bytes. Those bytes are not a recovered device-state image.

With SPI status completing but no supplied timer event, setup reaches the timer-delay scheduler boundary; the interpreter stops at the unsupported trap. With a timer completion supplied before the blocking wait, execution runs the actual handler at `400ec3a0`, including its semaphore signal, up to the `RTE` boundary at `400ec3ce`. Setup then reaches `4008c7d4` in 2,900 instructions. Interrupt entry, `RTE`, and delivery after the task blocks remain unmodeled.

The constructor dispatcher resumes without adding a new synthetic call frame. It executes all 119 callbacks in table order in 412,495 instructions, entering the actual allocator 999 times. The entire proposed `15c80`-byte allocation and its owner pointer remain byte-for-byte unchanged across this interval.

Three continuations supply the already-current response, wrong identity, and wrong platform respectively. Each executes the version-query return at `4009f75e`. The surrounding caller continues into asset loading after each result; it does not terminate there on these error values. Each bounded continuation preserves the allocation.

The saved regression uses a 50,000-instruction bound for each post-table continuation. A separate earlier probe ran each of those three continuations for 2,000,000 instructions; all remained in the stock decompressor, ending at `400ee2fc`, `400ee31e`, and `400ee2f2` respectively. These bounds do not establish a device hang. The interpreter now supports the encountered `SHI` instruction; decompression completion and output interpretation remain unresolved.

## Evidence and limits

The adjacent [machine-readable results](Digitone-startup-completion-results.json) record individual checks and bounded outcomes. The model executes recovered instructions with explicit peripheral fixtures, a supplied initial scheduler/thread boundary, and a modeled external-device window. It does not reproduce physical device timing, asynchronous scheduling, cache coherence, or all hardware memory semantics. Preservation claims apply to the executed intervals and chosen fixture values.

The original SysEx and decoded main section retain their recorded SHA-256 hashes:

- SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Main section: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`

No firmware was modified or repacked, no flashable artifact was produced, and no device I/O was performed.

## Next focused task

Validate the stock asset decompressor's input, output bounds, and modeled destination semantics, then resume the same startup state to the initializer. That will test the remaining intervening lifetime rather than assuming the standalone initializer tests prove the whole startup bridge. Timer completion after blocking, actual scheduling, physical cache coherence, and broader executable-placement ownership remain separate open checks.
