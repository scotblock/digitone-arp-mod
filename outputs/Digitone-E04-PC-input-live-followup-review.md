# PC input guard follow-up: sustain, bypass and warm reset

Firmware and all prior artifacts remain unchanged, verified against the previous summary hashes. These tests use the existing host-loaded input/LIVE overlay. No installable build was produced.

## Results

Four paced DIN sessions ran without a halt and delivered all bytes. LIVE with the three guards and LIVE with their displaced stock entry bytes restored matched observed handler routes and sustain flags/list pointers across CC64, note-on, explicit note-off, velocity-zero note-off and pedal release. This comparison retains the other experimental hooks; it is not a pristine-stock audio/timing comparison.

Closed-phase negative controls found real uncovered routes:

- CC64 changes sustain flags even in INITIALIZING.
- Explicit status-80 note-off reaches `400eae0c` independently of the guarded packet entry. Velocity-zero status-90 instead goes through the packet guard and is blocked when closed.
- A note accepted in LIVE, held by sustain and released after the phase was set to INITIALIZING reaches the actual sustain-release path and `40100252` queue publication while closed. Phase closing is an explicit host fixture; the upstream paced receiver and downstream release/publication instructions execute normally. This proves a guard bypass under that state, not stock reachability of a warm transition to it.

Nine direct calls to the actual warm initializer (three each from LIVE, INITIALIZING and FAILED) returned and toggled READY 0/1, without changing the admission word. In a separate hypothetical overlap, execution paused at its real stock trampoline `47be0642` with READY=0 and admission still LIVE. A packet on a separate scratch stack reached selector, live producer and publication and changed monitored state. Restoring the paused CPU resumed the reset successfully. This injected preemption does not establish that a real interrupt or scheduler can create the overlap.

Panel T1-T4 press/release attempts, including KEYBOARD selection, reached none of the observed note entries in either LIVE control. They are attempted stimuli, not passed panel-note coverage. The panel receiver/consumer and current UI state need tracing before treating this as evidence about panel guards. No UI refusal or whole-command guard was integrated.

## Next implementation target

Extend admission to the recovered release/sustain paths, with an explicit policy for already retained notes. Establish a whole-operation warm-reset refusal before flags, pool mutation or retained-reference transfer; simply checking READY inside metadata hooks does not prevent stock note-pool writes. Then obtain a positively observed panel-note workload and join the prior UI refusal controls before claiming complete admission. Any release guard must test cleanup and re-entry so retained notes do not leak or become stuck.

## Evidence

- `Digitone-E04-PC-input-live-sustain-panel.json`: receiver sessions and per-input routes/state.
- `Digitone-E04-PC-input-live-warm-reset.json`: repeated initializer calls and disclosed overlap control.
- `Digitone-E04-PC-input-live-followup-summary.json`: assertions, gaps and unchanged hashes.

Existing emulator hardware/storage shortcuts remain. Cold provenance, global physical RAM ownership, real cache handoff and physical timing are still unresolved. Hardware readiness is not established.
