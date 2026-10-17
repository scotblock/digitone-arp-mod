# Digitone OS 1.42: application selection and input-gate writer audit

Firmware unchanged. Context trailer and startup/reset hook remain unimplemented.

## Result

The two MIDI gates are now mapped to concrete project-configuration fields and recovered writers. The application selected-child helper is executed through the previously tested outer transition and return. Neither that helper nor the tested transition establishes an input-stop or payload-ownership barrier.

A significant reachability limit is also established: the tested page is **AudioTestMenuView**, labelled **AUDIO**. The settings constructor creates and stores it, but none of the ten callbacks registered by the recovered normal settings-menu builder selects it. Thus the prior controlled execution does not demonstrate that normal settings-menu interaction reaches this diagnostic page. Computed or other diagnostic selection is not excluded.

Actual device configuration and a complete earlier shutdown contract remain unproven. The firmware image alone does not contain the user's current RAM state or project settings.

## Gate ownership and writers

The current project base `407b00b0` plus configuration offset `b6b8e0` equals `4131b990`.

| Field | Runtime address | Meaning in recovered consumers |
|---|---|---|
| Configuration `+8c` | `4131ba1c` | Receive-source mask: first task queue uses bit 1, second uses bit 2 |
| Configuration `+b0` | `4131ba40` | Nonzero permits Note On and Note Off wrappers to process notes |

These are project settings fields, not identified shutdown-acknowledgement variables.

The project-binding function `40022366` gets its project pointer, adds `b6b8e0`, and passes the result to configuration binding `40029546` for the configuration object at parent `+30`. Property binding `4013835e` stores that underlying pointer at object `+10`; actual virtual getter `40138354` returns it. Configuration vtable `40174fc8` resolves getter slot `+28` and notification slot `+10` to the stock functions used in execution. Startup function `4002235a` stores the supplied project base at `40507e2c`.

Recovered concrete writers:

| Writer | Effect |
|---|---|
| Default initializer `40013722` | Stores receive mask **3** and note permission **1** |
| Receive-mask setter `4002af1a` | Clamps supplied integer to 0..3, writes configuration `+8c`, then notifies |
| Note-permission setter `4002b344` | Writes the low byte of the supplied value to configuration `+b0`, then notifies |
| Note-permission toggle `4002b38e` | Converts zero to 1 and nonzero to 0, then notifies |
| Serialized configuration parser `400094aa` | For version 7, reads serialized byte `+28` for receive mask and byte `+31` for note permission, clamps them to 3 and 1, and writes the runtime fields |

The receive UI change callback `40066750` calls the mask setter. Note UI callback `40066fe6` calls the toggle. This provides concrete UI writer provenance beyond raw absolute-address searches.

The project-loading code at `4000e058` derives the configuration destination using the same project offset and calls the parser at `4000e072`; parser failure is followed by default initialization. Project initialization also uses this offset. These surrounding load/reset paths were inspected, not fully executed or certified for shutdown.

## Writer execution

Both complete default-initializer branches execute, including the optional full configuration initialization. They produce masks 3 and 1 and ordinary channel assignments 0..7.

Complete mask setter, note setter and toggle execution uses the actual getter and notification functions, with controlled empty observer lists. Tests cover the mask clamp boundaries, note low-byte behavior and toggle from zero/nonzero. The notification path returns through stock instructions; it is not replaced by a no-op.

With a real queued event and counted template copy already retaining two references, executing both actual setters with zero values disables both gates but leaves the queue and retained payload owners unchanged. This rules out treating gate values alone as proof of storage quiescence. Side effects from nonempty observer lists remain unverified.

The actual parser prefix executes from its function entry through the two gate writes for serialized zero, normal enabled and saturated values. An incorrect version returns before either gate changes. Valid cases stop immediately after the second gate store; the remainder of the parser and complete project-loading transaction are not executed. Retained and queued owners survive the tested prefix.

## Application selection and reachability

Settings constructor `4006f83a` calls `400ae9fa` to construct AudioTestMenuView. It adjusts the returned object pointer by `+38` and stores its owning UI reference at application `+2b4`.

Normal settings-menu builder `4006f0fe` registers these ten complete action callbacks:

| Menu label | Callback | Selected child field |
|---|---|---|
| PROJECT | `4006f57e` | `+26c` |
| SONG | `4006f5c4` | `+2bc` |
| PATTERN | `4006f60a` | `+27c` |
| SOUNDS | `4006f650` | `+274` |
| MIDI CONFIG | `4006f696` | `+284` |
| SYSEX DUMP | `4006f6dc` | `+28c` |
| AUDIO ROUTING | `4006f722` | `+294` |
| GLOBAL FX/MIX | `4006f768` | `+2ac` |
| CONTROL | `4006f7ae` | `+29c` |
| SYSTEM | `4006f7f4` | `+2a4` |

**AUDIO ROUTING is a different child from AudioTestMenuView.** None of these recovered callbacks selects `+2b4`. This is an enumeration of this actual builder and its leaf callbacks, not a universal proof that the audio-test page is unreachable.

The shared selected-child helper `400d5f02` updates the parent's selected UI reference, retains a temporary reference, invokes `400d7a6e` using the parent's page-manager pointer, releases temporary references and returns. Its local instructions contain no recovered MIDI gate setters, payload-owner checks or ownership-drain calls.

Controlled execution supplies the constructed audio page's reference to this actual helper. It completes the full outer transition, both entry callbacks and normal cleanup. UI reference accounting balances to the three surviving owners: constructed field, selected field and page-list node. The separate queued note/template retain two payload references; receive and note gates stay enabled. No ownership helpers are stubbed.

This extends the tested transition to its common application selection helper. It does **not** invent a real menu action for the audio-test page. The earlier result must remain bounded accordingly.

## Remaining work and decision

No earlier shutdown barrier was found in the recovered common selected-child helper, configuration field bindings or tested empty-observer gate notifications. This is not global certification: computed selection, nonempty observers, upstream task commands, full project load/rebind, concurrency and hardware state remain open.

The previously recovered `#ENTER_TEST_MODE` command installs different diagnostic handlers from AudioTestMenuView's entry callback. They must not be treated as the same transition merely because both are diagnostic.

The most useful next target is the **actual diagnostic/application request path that can select AudioTestMenuView**, if present, together with **nonempty configuration observers and project load/rebind boundaries** that could impose earlier protection. Gate-writer identification is concrete now; an exclusive and exhaustive writer/alias inventory is still not claimed.

Keep the proposed trailer and startup/reset hook unimplemented. Neither defaults, turning reception off, nor the tested application selection helper supplies a certified safe reinitialization contract.

## Validation

**76 checks passed:** 45 complete writer/application execution checks across 18 cases (76,440 recorded instruction steps), 14 parser-prefix checks across four cases (1,226 steps), and 17 structural checks across 26 function graphs (2,114 instructions).

Evidence:

- `Digitone-application-gate-writer-execution-results.json`
- `Digitone-config-parser-gate-prefix-results.json`
- `Digitone-application-gate-writer-graphs.json`

Controlled state includes existing initialized UI/configuration objects, empty observer/dependency lists, no optional child page and no waiting kernel notification task. UI heap returns are supplied only for one-byte callable copies and a 16-byte page-list node. No interrupt/task interleaving or device communication is performed.

Source SysEx SHA256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.

Decoded image SHA256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.

Both remain unchanged. No patch, trailer, startup hook, repackaged SysEx or flashable image was produced.
