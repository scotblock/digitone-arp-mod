# Source archive and reproducibility

The first repository commit captures research and patch source, not a fully automated clean build.

Run scripts from the repository root: many load other `work/*.py` files, read their definition prefixes, or expect generated files in `work/os144/` and `outputs/`. Do not run the complete historical collection as a test suite. It includes superseded experiments, failures and programs that create candidate files locally.

## Important entry points

- `work/build-E09-PC-dual-port-mirror.py`: separate dual-port synth-owner overlay built from E08F artifacts.
- `work/test-E09-PC-dual-port-mirror.py`: native owner/driver contract checks with disclosed endpoint fixtures.
- `work/integrate-E09-PC-dual-port.py`: startup copier/package integration.
- `work/test-E09-package-path.py`: loader and startup checks.
- `work/test-E09-packaged-synth-both-ports.py` and `work/test-E09-packaged-M1-both-ports.py`: playback checks from packaged startup state.
- `work/finalize-E09-routing-candidate.py`: result-gated local candidate finalization.
- `work/build-PC-E08E-menu-fix.py`: menu correction subsequently packaged as E08F.

These are a dependency chain, not a standalone command sequence: E08F binaries, layouts, firmware inputs, native tool executables and emulator snapshots must first be regenerated. Their absence in this source-only checkout is intentional. Older OS 1.42 experiments are retained for research history, but addresses are version-specific.

## Dependencies

The testing engine uses Python, a patched Unicorn M68K/ColdFire engine, Capstone and Digiemu. The copied Digiemu pyproject records its declared dependency versions; some historical Windows runs used a separately built local CPU engine. `work/build-local-cpu-engine.py` records that experiment's commits and compiler paths. DLLs, installed Python packages and Unicorn's full upstream source are excluded.

The current local Digiemu source snapshot is included to preserve the DMA/timing/model changes. A pristine upstream checkout is not assumed equivalent. Its local snapshot has no Git metadata, so no verified current upstream commit or complete upstream-vs-local diff is claimed. References to earlier commit IDs in historical scripts describe those individual experiments.

The container tool C sources are included under their original MIT license; compile them separately. The draft project generator also requires DNX (AGPL-3.0-or-later), which is not vendored here. Generated test projects are not validated releases.

## Known reproduction cleanup

E09 integration currently appends USB helper metadata with names also used by DIN helpers. The working manifest was later disambiguated by prefixing the new helpers at addresses >= 0x47be7e00 with `USB_`. That metadata-only cleanup is not yet automated by the integrator. The latest routing note/review also contains a diagnostic follow-up added after finalization; rerunning the finalizer alone does not preserve that addition.

The next repository task should make the latest build reproducible from separately supplied stock firmware, with explicit dependencies and generation order. This archive does not claim that has already been accomplished.

## E10 package integration continuation

After regenerating the E10 lifecycle MAIN/payload/layout, preceding native private-card fixtures and the bundled C compressor locally, run `work/build-PC-E10-package.py`, `work/test-PC-E10-package-loader.py`, `work/test-PC-E10-package-startup.py`, `work/test-PC-E10-package-playback.py`, then `work/verify-PC-E10-package-integration.py`. The startup source template is `work/E10_powerfail_startup_template.py`; its helpers and prior playback generators are required. Supply your own stock OS 1.44 input under the documented local path. Private card/snapshot/handoff and compressor executable inputs are intentionally absent from this source archive, so this order is not a turnkey fresh-checkout build. Internal generated firmware stays under `work/os144`; no E10 download release is made by these checks.

### Packaged E10 user workflows

The `test-PC-E10-package-workflow*.py` drivers and `verify-PC-E10-package-workflow.py` extend the prior packaged evidence. With the private upstream runtime, stock-dependent package, verified loader handoff and startup snapshots available, run the native editor/save workflow, restart, named recall, held handoff, and separate copy/reset scenarios, then the consolidated verifier. `--resume-save` and `--resume-completion` continue disclosed native checkpoints used while correcting input/observer assumptions; they do not seed firmware settings. The ordinary final restart/recall and handoff runs include the explicitly programmed A04 rest. The copy/reset branch uses its earlier populated saved-session snapshot. Cards, binaries, screenshots, snapshots and generated handoff state remain excluded. Paths/tooling and prerequisite artifacts require local configuration, so this is a source/evidence archive rather than a turnkey test distribution.

### E10 trial artifact preparation

`work/test-E10-startup-DIN-route.py` adapts the existing stock-bootstrap receiver driver to the exact unchanged E10 container and bounds every modeled flash operation. `work/prepare-E10-hardware-trial.py` requires the private tested container, verified stock 1.44 input and preceding passing reports, then freezes local trial files, builds a stock-dependent ZIP with the existing release tools and tests its extracted CLI. These generated files remain outside the source archive. It neither flashes a device nor publishes a GitHub release.
