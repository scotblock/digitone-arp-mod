# Startup completion and first input admission: PC findings

Four loader-derived startup runs pass: default/restored with no external input, then default/restored with three DIN note bytes offered before note initialization. Four checkpoints per normal run capture actual state before note setup, after full audio/note setup, before the later worker startup, and at the normal startup idle point. Fourteen handler probes, six saved-state interrupt probes and two settled input sessions also pass. Existing firmware/raw/previous UI-overlay hashes are unchanged.

## Stock gates open before note initialization

Stock configuration deserialization writes receive gate `41368d64` at `40009b0a` and note gate `41368d88` at `40009bde`. Default receive gate becomes 2 (USB only); restored receive gate becomes 3 (DIN and USB). Both note gates become 1 while admission is still COLD and context READY is zero. The later native cold claim changes phase to INITIALIZING but does not change either stock gate.

DIN receive vector `40000270` already points at `400025c8`, its ring DADDR is `4bc00000`, and the saved INTC permits interrupt level 4 at the pre-initializer snapshot, where SR is `2000`. The phase word therefore is not an effective input barrier.

## Handler eligibility versus transport production

Direct, controlled calls to actual note wrapper `400eb2d2` with unchanged stock gates reach producer `400eae5c` before initialization. Those pre-initializer probes stop before note-pool writes. After normal setup returns at `4008d31e`, complete handler calls publish queued notes while phase remains INITIALIZING. Some cached-path publications occur before reaching `400eae5c`, so a guard only at that later producer would miss them.

The saved DIN IRQ controls offer vector 156 under saved SR/INTC conditions, consume all three bytes through actual ISR `400025c8` and callback `400e842c`, then return. They do not reach the note producer. The separate continuous cold runs inject the same bytes before setup, take the actual interrupt, finish startup and reach modeled UI without observing note-handler/producer publication from those bytes. This does not establish why the early bytes fail to produce notes, or prove a universal startup input exclusion. In particular, USB and panel producer timing remain untested.

Once the modeled UI is settled, paced DIN input on the restored configuration executes the real receiver/worker/handler and publishes a note while admission is still INITIALIZING. Default USB-only configuration rejects DIN as the stock setting requires. No gate or phase value is changed to authorize either session. Thus the native seed/claim experiment alone does not implement the policy's producer closure or transition to LIVE.

## Completion boundaries

`4008d31e` follows completion of normal note/audio setup: stock initializer has returned, context READY is 1 and normal audio vector is installed. Later startup work still remains. Startup `4008d3dc` calls the next worker initializer, then `4008d3ee` starts the input worker through `400eb3e6`, and `4008d3f4` calls `40019444` to create/start the application worker. The normal path then reaches `4008d3fa -> 4008d3ec` (idle).

`4008d3fa`, after the last visible synchronous startup call returns, is a late candidate for LIVE publication. Reaching the idle point on the normal branch in both runs establishes observed completion of these calls, not an explicit checked success/error contract. At these checkpoints the current task is `4137465c`, matching the recorded startup task at priority 1; the input worker is created at priority 7. These task observations do not certify all scheduler/IRQ overlap or hardware preconditions.

A late publication cannot by itself hold earlier input closed: stock note gates already authorize the direct handler, receiver callbacks are active earlier, and workers are made runnable before that final boundary. Conversely, publishing LIVE immediately after the note initializer would mislabel later startup as complete. No LIVE store is added by this investigation.

## Concrete next step

Add a PC-only phase-aware check before input dispatch can enter either cached publication or live-note production, and cover panel/direct routes separately. Then test publishing LIVE at the normal completion boundary together with these guards, including feature-disabled stock fallback and input offered before/during/after the handoff. The completion condition must distinguish stock setup completion from optional context availability. Exact graceful failure handling, non-replayable boot provenance, global/physical storage ownership and hardware cache/timing remain unproven.
