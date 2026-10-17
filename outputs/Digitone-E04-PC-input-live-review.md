# Input guards and LIVE transition: PC overlay review

A separate 492-byte host-loaded overlay now guards three recovered input entries and publishes LIVE after the last visible synchronous normal startup call returns. All targeted tests pass: 18 closed-phase entry controls, four LIVE/stock parity pairs, nine completion controls, three continuous native cold startup cases, three settled MIDI sessions, one publication/IRQ control and one controlled closed-to-LIVE receiver handoff. Existing firmware, raw candidates and older guard blobs are unchanged by verified hashes.

## Guard behavior

Exact LIVE is required at packet wrapper `400eb2d2`, cached selector `400eb166`, and live producer `400eae5c`. CLOSED/INITIALIZING/FAILED and tested zero/poison/corruption return before any original prologue or input argument dereference. The denial is a no-op at the recovered function boundary, preserving registers, incoming SR and caller stack. It does not create a note, update cache/context or enter allocation/publication. Unknown callers' expectations still require audit; no general boolean error contract is asserted.

The packet and selector guards cover the cached publications found before the later live producer. Direct live-producer entry is also guarded. LIVE restores saved state, replays each displaced prologue and resumes original execution. Four paired calls match stock CPU/queue/pool/context state and routes, with and without optional context, including the earlier cached publications and later live producer. These parity calls have no concurrent timers, so they do not measure added timing cost.

## Normal completion and fallback

The new completion wrapper replaces normal startup call `4008d3f4`. It executes complete stock `40019444` first, then requires its observed return `4008d3fa`, INITIALIZING, normal boot/test flags, both recovered setup flags at 1 and installed normal audio vector `4009d120`. It publishes through the native phase helper under IPL7 and restores incoming registers/SR before returning to startup idle.

Optional context is checked independently: invalid/missing PTR, metadata or READY disables PTR/READY and still permits LIVE for stock behavior after the normal stock conditions pass. Bad phase/mode/setup flags/audio vector/return enter the earlier proposed masked PC failure stop. This remains a bounded completion contract using observed fields, not universal error/exception certification or hardware recovery.

Default, restored-project and injected-owner-failure startups all execute guest stores zero -> COLD -> INITIALIZING -> LIVE exactly once and reach modeled UI. The injected owner failure follows the real fallback/stock initializer and ends with optional context disabled. Three settled paced DIN sessions preserve stock receive settings: default USB-only rejects DIN; restored and feature-disabled configurations accept and publish notes, all under LIVE.

## Input around publication

The startup cases also offer DIN bytes before note initialization and continue through native startup, with unchanged receive/note gates. Like the earlier controls, these early bytes do not produce an observed note during startup/intro. This is not a promise to discard every raw byte received before LIVE: the guards act when input reaches the guarded functions. Upstream transports may queue raw input and process it later.

A retained, fully started checkpoint from the earlier overlay naturally remains INITIALIZING. With the new guards installed, paced DIN reaches the actual packet wrapper but stops before cached/live processing and note publication. The test then pauses that session, runs the native phase helper with declared success argument 1, restores task CPU/stepper state, and sends another note. That note reaches the cached selector, live producer and queue under LIVE. No host phase write opens input. This is a functional phase-handoff control; actual bootstrap completion checks and full final call are established by the separate continuous startup cases.

At the native completion state's LIVE store, a controlled DIN interrupt offer is rejected under IPL7. After the helper restores the interrupt mask, explicitly offering it again takes vector 156 and consumes all three ring bytes with phase LIVE. Actual peripheral request latching/retry and physical byte timing are not certified.

## Remaining scope

Code lives at fixture-only `47fa0600`, alongside earlier host-loaded bootstrap helpers. No packaged loader/copy delivery, physical executable placement/cache handoff or timing claim is made. These are functional instruction/model checks with the existing cold/intro/playback shortcuts.

CC/sustain, release/panel/sequencer bypasses, upstream USB queues, callback overlap and every unknown computed caller are not fully covered by these three entry guards. The previously isolated UI guards are not patched into this joined startup overlay. Warm initializer and command admission remain absent; input would still be allowed in LIVE during an unguarded warm pool rebuild. Cold replay provenance, global/physical RAM ownership and hardware cache/timing remain unresolved. Do not install this experiment on a device.

The next focused task is auditing note-off/sustain and panel/direct dispatch around this guard, including already queued input, then joining the previously tested UI refusal guards with the startup overlay before claiming complete V1 admission.
