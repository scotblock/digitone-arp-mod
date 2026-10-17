# Outer parent publication, caller handling and guard choice

Ten bounded native PC controls pass through the outer page manager and actual application wrapper. The supported local guard contract is: **complete normal parent entry, then defer the retained AudioTestMenuView before child-reference transfer**. This is a chosen PC implementation direction, not installed enforcement or hardware readiness. Original firmware containers and raw PC candidate remain unchanged (hash checked).

## Publication precedes entry

Actual manager `400e6352`:

1. Locks the manager and checks closure/selection conditions.
2. Allocates a list node, copies/retains the target reference and publishes it through `4018723c` at `400e6478`.
3. Recomputes manager selection with `400e626e` at `400e6480`; manager selected-node +1c and page activation state can change here.
4. Loads the new page's virtual entry +18. At `400e648e`, it sets D2=1, then invokes entry at **400e6494**.
5. Cleans arguments and unlocks, then returns D2 in D0 at `400e64a2`. It does not test entry's return value or undo publication.

This ordering executes in the controls using the stock audio constructor, settings base-parent construction prefix and real ownership wrappers. A manager node is already published and the parent's node owner retained when execution reaches the parent's entry refusal point.

## Three native outcomes

| Supplied refusal/defer | Manager result | Parent state after return |
|---|---|---|
| Before parent callbacks at `400e4e2e`, return through `400e4eae` | Success (1) | Node remains published; entry binding/registry callback skipped; page's manager pointer remains zero |
| After normal parent callbacks, before child transfer at `400e4e42` | Success (1) | Parent node is published, parent is bound/active and registered; retained child stays pending; audio entry does not execute |
| Before manager publication at `400e637c`, false/unlock tail | False (0) | No parent node or registry entry; reference accounting unchanged |

All three outcomes execute with both uncontended and already-recursive manager state. Register/stack/interrupt control and lock/reference cleanup balance. Watched queued notes, gates, audio vector and pool/context hashes remain unchanged. The host supplies the branch decision; these are native continuation tests, not guard code.

The pre-callback entry return is therefore not a safe full-parent cancellation: the outer manager has already committed a node and reports success while entry binding was skipped. An earlier manager false path is locally balanced, but it is not a universal application transaction abort either; the previously audited shared selection helper can change its parent-selected reference before calling the manager.

## Actual application caller

Application wrapper **40017f46** copies the requested shared reference into a temporary, passes it to manager **400e6352** using application +40, releases its temporary and propagates the manager result. Four controls execute this complete wrapper around the manager, for deferred-child success and pre-publication false, with both mutex states. The temporary strong owner is released; node ownership survives only on manager success.

The application manager pointer is a controlled fixture; the wrapper and its ownership instructions are actual stock code. This does not prove every higher caller tests false. Earlier recovered menu callbacks ignore selection results, and the shared parent-selection helper assigns its selected child first. No blanket rollback contract is inferred.

## Chosen local contract

For retained audio-test restoration while V1 is live:

- Allow normal parent entry callbacks and their stock page binding/active-registry update to finish.
- Before transferring retained child +8c into selected +84, recognize the protected AudioTestMenuView and defer that child.
- Leave retained ownership intact, selected-child state unchanged, and the audio handler/pool/context untouched by child entry.
- Let the parent operation complete normally. Do not label its success result as a failed parent transaction or fabricate rollback.

The candidate local point remains **400e4e42**, with the tested native return tail **400e4eae**. This preserves the parent-entry contract observed through the actual outer manager and wrapper. It is a deliberate deferred-child state, not a rejection of the whole parent selection.

A final guard still needs machine-code implementation, reliable live/cold admission and page-identity checks, notification/defer semantics, and checks for later close/re-entry/reference lifetime. The parent's earlier callbacks must remain appropriate for the actual complete settings object. The current test only constructs its base-parent prefix; the known full-settings application dependency gap is not erased by these passing controls. Explicit diagnostic entry/exit and direct-child selection need their own already-audited admission boundaries; this defer point does not cover all routes.

## Test scope and next step

Six manager controls and four actual application-wrapper controls pass. Audio child is fully stock-constructed; parent construction stops after its real base-parent return. Current-task/manager/list state and initial retained ownership are controlled. Complete hardware startup, first audio selection request, live interrupt concurrency, all higher callers and physical RAM/cache/timing remain unverified.

Next, implement and exercise this deferred-child contract in a separate PC-only overlay, alongside early explicit child-selection refusal. Keep firmware containers unchanged. Validate the latch/admission storage before treating that overlay as persistent enforcement, and verify close/re-entry behavior without silently consuming the retained child.

Evidence: `Digitone-E04-PC-outer-parent-publication.json`, `Digitone-E04-PC-outer-parent-publication-summary.json`.
Reproduce: `work/test-PC-outer-parent-publication.py`.
