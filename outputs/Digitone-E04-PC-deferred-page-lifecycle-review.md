# Deferred-page close/re-entry and retained ownership

Two native PC lifetime runs pass, with normal and already-recursive manager state. Each performs three complete parent enter/defer/close/remove/re-enter cycles, then releases the final parent and audio owners through stock virtual destructors and heap cleanup. The deferred audio-test child stays retained across cycles; neither its entry/exit handler nor pool reinitialization is reached. Original firmware, existing raw candidate and the separate 150-byte guard overlay remain unchanged (hash checked).

## Actual lifecycle execution

The test uses the full stock AudioTestMenuView constructor and the settings constructor's actual base-parent prefix. Audio owning references and parent callback registrations are created by stock `400e43fc`. A constructed outer owner's valid selected-reference slot owns the parent; the manager supplies a separate node owner while it is published. The starting retained audio reference is a controlled condition, assigned by native reference operations.

For each cycle:

1. Assign the parent handle to the outer owner's selected slot with native `401774c0`.
2. Run actual manager `400e6352`; parent entry and registry update complete while the disposable native guard defers the retained audio child before transfer.
3. Run stock parent close `400e4ec2` and complete manager removal `400e6634`.
4. Execute the actual full parent exit callback list: `400e47ca` removes the parent's active-registry entry; the registered wrapper-clear target `400e4848` clears the outer selected owner. Native list unlink, shared-reference release, node free and mutex cleanup complete.
5. Re-enter the same still-owned parent through the actual manager. The guard defers its unchanged retained child again.

No host branch/return injection chooses deferral; the installed disposable overlay executes its own guard instructions. Current-task identity is the snapshot's original **4052b668**, so inherited stock mutex owners remain consistent. The initial synthetic-task destruction probe hit a wait on a mutex held by that original task, at `40001a9e`. The passing runs use the original task from setup onward, without forced unlock or scheduler stubbing. Cross-task contention and actual scheduler interleaving remain untested.

## Ownership accounting

| Stage | Parent strong owners | Audio strong owners |
|---|---:|---:|
| Published and deferred | 3: handle, outer selected slot, manager node | 2: audio handle and parent retained slot |
| Closed and removed | 1: surviving parent handle | 2: audio handle and parent retained slot |
| Final parent handle released | Parent root destroyed/freed | 1: surviving audio handle |
| Final audio handle released | Already released | Audio root and owning control block destroyed/freed |

Each closed cycle leaves the manager list empty, parent manager binding cleared, outer selection cleared and application registry returned to its starting contents. The parent's selected child remains empty; retained +8c remains the same audio reference. Reference counts do not accumulate over re-entry.

Final releases use native move-assignment `40158b82` into empty references. Parent virtual destruction releases its retained audio owner and frees the parent root. The final audio release destroys/frees the actual audio root and its owning control block. Tests observe the native heap-free path; they do not read freed control blocks afterward.

## Note/reset behavior

Queued-note state, audio vector, gates, pending/descriptor context and tested pool/context hashes remain unchanged across all cycles and final releases. Trace hooks never reach audio entry `400e7e7e`, audio diagnostic exit `400b25c2` or the PC pool-reset entry. Destroying a never-entered retained audio child does not invoke its diagnostic exit callback in these native controls.

This closes the concrete deferred-child ownership question within this fixture: deferral neither consumes the saved reference prematurely nor leaks successive parent/node owners, and normal parent close plus final destruction does not force the diagnostic pool-rebuild path.

## Limits and next step

The outer owner is a constructed reference container; the parent is built only through its actual base-construction prefix. Full settings construction still has the recorded application-dependency gap. Initial real audio selection, other computed writers/callback orderings, live IRQ concurrency, physical RAM ownership/cache/timing and hardware readiness remain unproven.

The guard still uses a test-selected compiled live constant at a fixture-only code address. Next is validating persistent live/cold admission and its storage lifetime before integrating these guards into a new PC startup candidate. Keep current firmware containers unchanged; these lifetime results alone do not make the modification hardware-ready.

Evidence: `Digitone-E04-PC-deferred-page-lifecycle.json`, `Digitone-E04-PC-deferred-page-lifecycle-summary.json`.
Reproduce: `work/test-PC-deferred-page-lifecycle.py`.
