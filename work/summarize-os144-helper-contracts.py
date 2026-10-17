import json,hashlib
from pathlib import Path
def read(name):return json.loads(Path('outputs/'+name+'.json').read_text())
port=json.loads(Path('work/os144/helper-port.json').read_text())
diff=read('Digitone-OS1.44-helper-differential');copy=read('Digitone-OS1.44-helper-copy');native=read('Digitone-OS1.44-native-helper-ABI');outer=read('Digitone-OS1.44-outer-helper-ABI');reset=read('Digitone-OS1.44-helper-reset-cancellation');scale=read('Digitone-OS1.44-scale-contract')
assert diff['passed'] and copy['passed'] and outer['passed'] and reset['passed'] and scale['passed']
assert native['failure'] is None and native['code_intact'] and len(native['cases'])==4
for image in port['PC_only_helper_images']:assert hashlib.sha256(Path(image['path']).read_bytes()).hexdigest()==image['sha256']
assert diff['build_sha256']==port['PC_only_helper_images'][0]['sha256']
hashes={}
for name,path,expected in [('1.44','inputs/Digitone_and_Digitone_Keys_OS1.44.syx','d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'),('1.42 main','work/section-3.bin','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'),('1.42 packed helpers','work/packed-context-overlay.bin','e787fab50d3d2dca4c6c9deb1edecbf2de93577c0ccced3b7a0adaefd3491f88')]:
 hashes[name]=hashlib.sha256(Path(path).read_bytes()).hexdigest();assert hashes[name]==expected
limits=['Isolated helpers use explicit ready headers, event/cache/selection fixtures and root/scale inputs. This is not proof of producer ordering or global storage ownership.','Differential checks compare two independently laid-out existing helper implementations after the same version-operand port; oracle and stock-instruction checks provide additional evidence.','Before/after ABI checks stop at the stock selector entry/return continuation; full selector execution with these helpers remains untested.','Reset tests directly invoke the real 1.44 initializer continuation but do not install a startup hook or prove scheduler/input shutdown.','Cancelled-event tests execute the stock rejection gate to release entry with downstream PC overlays; the pitch helper relies on that upstream gate.','No full startup-to-playback integration with this 1.44 helper image, uncancelled queued-note scale retention across handoff, physical cache coherence or hardware timing is established.']
summary={'passed':True,'firmware_modified':False,'stock_session_hooks_connected':False,'startup_hook_installed':False,'port':port,'test_counts':{'differential':diff['differential_cases'],'cache_bounds':copy['cache_bounds_cases'],'cache_store_read_clear':copy['cache_store_read_clear_cases'],'invalid_header_stores':copy['invalid_header_store_cases'],'cache_producer_refresh':len(copy['producer_refresh_cases']),'cache_producer_invalid_capture':len(copy['producer_invalid_capture_cases']),'stock_copy_ABI':len(copy['raw_copy_ABI_cases']),'stock_producer_pitch_tracks':len(native['cases']),'stock_quantizer_spot_checks':native['quantizer_comparisons'],'outer_commit':outer['commit_ABI_cases'],'allocator_return':outer['allocator_return_ABI_cases'],'before_after_continuation':outer['before_after_continuation_ABI_cases'],'reset':len(reset['reset_cases']),'cancelled_consumer':len(reset['cancelled_consumer_cases']),'all_scale_quantizer':scale['quantizer_cases']},'hashes_unchanged':hashes,'limits':limits,'next_step':'Run the actual 1.44 selector/caller with these helpers in a PC stock session, validate entry and return state, then attempt controlled playback integration. Startup installation remains separate.'}
Path('outputs/Digitone-OS1.44-helper-contract-summary.json').write_text(json.dumps(summary,indent=2))
image=port['PC_only_helper_images'][0]
doc=f'''# OS 1.44 helper contracts: isolated PC tests

The compact context/pitch helpers have been adapted to 1.44 and pass the isolated checks below. The PC helper remains {image['size']} bytes; 17 instruction-contained absolute operands were changed. Its internal helper layout, metadata format and 420-byte pitch lookup table are unchanged. The original firmware, 1.42 main program and original packed helper image retain their hashes.

The new derived helper SHA-256 is `{image['sha256']}`. It exists only as an isolated PC test image. No stock-session or startup installation was performed and no flashable firmware was produced.

## Version-specific contracts

- Event pool: `0x419ebe2c`, 72-byte event stride. Physical cache candidates: `0x419f182c`; this cache relocation is different from the pool's relocation. The actual cache-base operand is at `0x40094c38` in stock 1.44.
- Selected identity records: `0x413915f4`; acceptance cache: `0x41392fcc`; selection gates: `0x413926e4`; commit neighborhood global: `0x41392fbc`.
- Producer continuation: `0x400947f4`; selector entry/return continuation: `0x40097a94` / `0x4009e694`; caller-commit continuation: `0x4009e738`; pitch continuation: `0x4009e88a`.
- Stock memcpy/memset: `0x400fbad8` / `0x400fbb20`. Allocator displaced-prologue continuation: `0x400ffff8`. Stock pool initializer continuation: `0x400ffeda`.

Exact PC hook sites and expected stock bytes are recorded in the companion summary JSON. Address correspondence does not establish broader storage ownership.

## Passing checks

| Check | Cases | Result |
| --- | ---: | --- |
| Context/helper differential checks | {sum(diff['differential_cases'].values()):,} | Registers, materialized status, metadata and event/cache outputs agree between the two ported reference layouts |
| Cache bounds | 291 | Exact alignment/range checks |
| Cache read/store/clear and invalid headers | 4 + 5 | Valid operations and fail-closed storage behavior |
| Cache producer refresh / invalid captures | 8 + 16 | New captures replace stale candidates; invalid root/scale, busy and fault cases clear them |
| Stock raw-copy interfaces | 8 | Registers, status and copied bytes match stock 1.44; metadata follows the copy |
| Stock producer/pitch interfaces | 4 tracks | Displaced instructions, registers/status, event preservation and fixed-point output checked |
| Commit / allocator return / before-after continuation | 40 / 8 / 20 | Stack, storage and return interfaces match the reference contracts |
| Direct reset | 7 | Ready/not-ready cases initialize; invalid header, null pointer and argument cases stop at the existing failure loop without context mutation |
| Stock cancelled-note consumer gate | 4 tracks | `+0x0C = -1` reaches release before any custom helper, even with valid-looking retained metadata |
| Quantizer against extracted 1.44 scale rows | 13,824 | All 36 scale selections, every note 0–127 and roots 0, 60, 127 agree with an independent nearest-note oracle |

The 35 non-chromatic 13-byte scale rows occupy a unique byte-identical 455-byte table at `0x401d5238` in 1.44, with two operand references. The chromatic sentinel remains raw scale -1. The quantizer oracle uses these extracted 1.44 rows rather than assuming the old mapping.

## Cancellation and limits

The stock consumer's cancellation gate remains upstream of the helper insertion points. Isolated tests temporarily attach downstream hooks and execute the real rejection branch; no helper is entered. The pitch helper is not an independent cancellation checker and must never be called as a way to reactivate a cancelled event.

These tests use explicit event, cache, selection and ready-header fixtures. The before/after tests stop at selector entry and the return continuation; they do not yet execute the changed stock selector together with the helpers. Direct reset tests are not a startup installation, setup-failure recovery or producer-shutdown proof. No assertion of hardware timing, cache coherence, complete storage ownership or eligible old-scale retention across pattern replacement follows from these results.

## Next step

Run the actual 1.44 selector and caller with the ported helpers in a PC stock session, validating entry/return state before attempting controlled playback integration. Keep startup installation separate until that integration passes.

Detailed evidence beside this report: `Digitone-OS1.44-helper-contract-summary.json`, `Digitone-OS1.44-helper-differential.json`, `Digitone-OS1.44-helper-copy.json`, `Digitone-OS1.44-native-helper-ABI.json`, `Digitone-OS1.44-outer-helper-ABI.json`, `Digitone-OS1.44-helper-reset-cancellation.json`, and `Digitone-OS1.44-scale-contract.json`.
'''
Path('outputs/Digitone-OS1.44-helper-contracts.md').write_text(doc)
print('PASS isolated 1.44 helper port and contracts; no stock-session/startup integration claimed.')
