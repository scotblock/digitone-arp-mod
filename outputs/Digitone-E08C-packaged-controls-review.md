# E08 controls integrated into the PC startup package

Later handoff checks: [pattern/copy/reset review](Digitone-E08C-pattern-copy-reset-review.md) found an early settings-application issue. The successful single-pattern results below do not certify handoff ordering.

The tested M1 MODE/RATE/GATE controls and project conversion helpers are now
part of the internal E08 PC package. They are loaded by the stock loader,
copied by startup and initialized before normal application playback. The
tests do not load replacement helper bytes, install the firmware hooks from
Python, call the M1 initializer from the host, or write the arp settings into
RAM. ColdFire instruction adapters and modeled peripherals remain in use.

This experiment uses E08C filenames to keep the earlier E08 package and test
evidence intact. E08C is an internal controls-integration label, not a released
firmware version. E07 is unchanged. No hardware installation build is released.

## Startup and preservation

- Independent unpacking reproduces the intended MAIN image exactly, and the
  unmodified stock container writer round-trip remains byte-exact.
- The stock bootstrap/loader reaches MAIN at 0x400004e8 with matching image
  bytes after 59,004,824 modeled instructions and no flash writes.
- The copied payload is 32,256 bytes, including
  12,012 additional bytes for this integration.
  Helpers, strings, rate table and displaced stock codec trampolines all travel
  in that payload. No additional heap allocation is introduced.
- The existing 336-byte M1 state contains the pending tagged settings and
  binding cookies. An isolated test poisons its final 24 bytes immediately
  before the native initializer; the initializer clears them. The wrong-caller
  control still excludes M1 initialization.
- Actual native startup reaches LIVE, clears the logo and reaches the UI with
  M1 OFF / 1/16 / 50%, empty event storage, no strict custom-instruction failures
  and no host completion-semaphore satisfactions.
- Resident helper code, tables and installed hooks remain intact after playback.
  The original appended MAIN copier source is zeroed by the time playback
  begins; it is a startup-only area. This does not make warm copier replay safe.

The loader handoff, cold checkpoint and UI checkpoint preserve modeled state.
This establishes a PC execution chain across those checkpoints, not physical
cache or DDR behavior.

## Panel controls, playback and project persistence

On M1, FUNC + SYN2 opens the native page. A changes MODE OFF/UP, B changes
RATE, C changes GATE, and NO closes it. The playback run selects UP / 1/32 /
80% from this page, then later selects UP / 1/16 / 50% from the page again.
There are no host arp-configuration requests in this run.

The observed output contains **81 note-ons and
81 matching note-offs**, with no hanging notes.
OFF passes the C–E–G chord through; UP produces ascending C–E–G repeats.
Both note-release cases leave the held set and descriptor arena empty. Stop
is checked after release; this is not coverage of every held/sustained Stop case.

| Observed phase | Mean step | Predicted from native clock | Mean gate |
|---|---:|---:|---:|
| UP_1_32_gate80 | 62.36 ms | 62.50 ms | 51.66 ms |
| tempo_plus400_1_32 | 62.42 ms | 62.50 ms | 51.83 ms |
| tempo_minus800_1_32 | 65.22 ms | 65.22 ms | 53.72 ms |
| UP_1_16_gate50 | 130.41 ms | 130.43 ms | 65.74 ms |

The LEVEL encoder's bulk tempo input changes the measured native musical
clock rate; the arp interval follows it. Changing 1/32 to 1/16 at the same
slower clock doubles the observed step interval. These are emulator timings,
not physical latency measurements or proof of audio DMA deadlines.

A separate fresh packaged-startup session repeats native project saving:
set UP / 1/32 / 80%, save through the project menus and emulated storage,
change MODE to OFF, and reload the saved project. The saved word and native
arp consumer both return to UP / 1/32 / 80% without another encoder edit.
Synth T4 data and existing M1 fields remain unchanged during the edits, and
the synth-settings getter is not called during the tested M1 control phases.
Legacy records still default to OFF / 1/16 / 50%.

The MIDI input-gate check retains the earlier disclosed emulator fixture.
In this playback run its before/after values are both 3, so reception was
already enabled and the write did not change its value.

## Remaining limits

This is M1 only. M2–M4 are not enabled. Native project persistence has been
observed for this sequence, but actual pattern-handoff isolation, preset
copying, warm reset, retained-view destruction and wider storage lifetimes
still need coverage. The proposed MIDI-record extension has no complete
exclusive-ownership certification. Physical RAM ownership, cache coherence
and real-time audio timing remain unverified. No hardware trial is approved
by these results.

The next bounded test is two patterns with different M1 arp settings, switched
through the real pattern transition while notes are queued or held, followed
by the relevant copy/reset cases. This extends the existing packaged tests
without changing the physical Digitone.

Evidence: `Digitone-E08C-packaged-controls-results.json`,
`Digitone-E08C-packed-loader.json`,
`Digitone-E08C-PC-startup-comparison.json`,
`Digitone-E08C-PC-copier-initialization.json`,
`Digitone-E08C-packaged-panel-playback.json`,
`Digitone-E08C-packaged-playback-verification.json`, and
`Digitone-E08C-packaged-project-controls.json`.

The observed MIDI output is saved as
`Digitone-E08C-packaged-M1-observed-PC.mid` for independent inspection.

Internal PC container SHA-256: `081c592e16bb8cb32b0b4c0ede6f0f10bc8dec95c783a50a7ee259d8d4ee6da6`.

Unchanged E07 SHA-256: `a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd`.
