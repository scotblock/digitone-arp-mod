# E10 update-interruption diagnostic

17 October 2026. This is a focused PC check following the decision to accept stock power handling as an inherited assumption. It does not reopen a requirement to measure or redesign the board power system. No firmware bytes or physical device are changed.

The native editor changes A01's first step offset. A test observer stops immediately after the native helper at 0x400852a0 clears the COKI header, called from E10 synchronization at return PC 0x47bf4112. The interrupted SR is 0x2704. After clearing the test stop marker, external vector 66 is injected at level 7, with the same disclosed pin/controller fixtures as the earlier automatic shutdown test.

Native interrupt dispatch resets the stack (the stock reset-stack flag is 1), lowers the interrupt mask and dispatches the registered shutdown callback. It does not finish the interrupted header publication. The shutdown writer completes its commands, but the new bank starts with zero magic; the old bank has also been invalidated. The current edit is not fully present in the new working image. Both working-copy headers are unrecognized. This is an update interruption before storage writing, distinct from the earlier synthetic cut during a storage write. Full cold fallback with both headers invalid was not executed here.

A paired control calls the unchanged stock helper 0x40085292 through a disclosed stopped-entry frame, copying a non-E10 serialized field to itself. It interrupts at the same header-clear instruction. No E10 data changes, yet the same two invalid bank headers result. Thus the fragile header-clear/interrupt interaction exists in this stock helper/protocol; the control is not evidence of a complete unmodified-stock UI workload. E10 adds a caller to that helper and inherits this exposure.

Both reports mark `execution_completed: true` and `recovery_passed: false`. Their historical `passed` field means the diagnostic reached its expected counterexample, not that recovery was safe. No guaranteed abrupt-power-loss recovery is claimed.

Development decision: keep this under the documented inherited interruption/power-loss assumption, as agreed by the user. Ordinary startup, controls, named saving, playback and packaged loader integration remain concrete E10 work. A later E10-specific hardening option is publishing its per-pattern record without invalidating the global working-image header, using a record-local commit marker/checksum. That option is not implemented, tested or made a prerequisite by this note. Do not infer that SR mask 7 alone excludes the external level-7 request.

See `Digitone-E10-development-assumptions.md` for the accepted scope. The next integration target remains the E10 packaged loader/startup/playback path; no new installable E10 is created here.
