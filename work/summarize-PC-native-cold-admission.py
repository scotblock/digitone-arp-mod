from pathlib import Path
import json,hashlib
startup=json.loads(Path('outputs/Digitone-E04-PC-native-cold-admission-startup.json').read_text())
controls=json.loads(Path('outputs/Digitone-E04-PC-cold-admission-controls.json').read_text())
assert startup['passed'] and controls['passed'] and len(startup['cases'])==2
for case in startup['cases']:
 assert case['passed'] and not case['cold_marker_fixture_only'] and case['native_cold_seed_consumed_before_initializer']
 assert [w['value'] for w in case['admission_word_writes']]==[0,0x434f4c44,0x494e4954]
 events=case['admission_boundary_events']
 assert next(e for e in events if e['pc']=='0x4009d0d8')['admission_word']=='0x494e4954'
 assert next(e for e in events if e['pc']=='0x4009c650')['admission_word']=='0x494e4954'
 assert case['intro']['up'] and case['intro']['intro_done']==1
expected=json.loads(Path('outputs/Digitone-E04-PC-persistent-admission-summary.json').read_text())['hashes']
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in expected.items())
summary={'PC_only':True,'passed':True,'native_loader_derived_startup_cases':2,'seed_controls':len(controls['seed_cases']),'pre_mutation_refusal_controls':len(controls['refusal_cases']),'actual_diagnostic_branch_control':controls['actual_diagnostic_branch_rejected_before_both_calls'],'replay_negative_control_demonstrates_limit':True,'native_seed_and_claim_executed':True,'completion_to_live_installed':False,'whole_initializer_and_command_admission_installed':False,'trusted_fresh_boot_provenance_certified':False,'packaged_loader_code_delivery_verified':False,'hardware_ready':False,'existing_artifacts_unchanged':True,'hashes':expected}
Path('outputs/Digitone-E04-PC-native-cold-admission-summary.json').write_text(json.dumps(summary,indent=2))
review='''# Native cold admission: PC startup experiment

The separate host-loaded overlay now seeds COLD after the actual copier and consumes it at normal startup's call to setup. Default and restored-project loader-derived PC startups both pass and reach the UI. The actual native writes are zero from the copier, COLD from the seed helper and INITIALIZING from the claim helper. No host supplies those state values or chooses success branches in these continuous cold runs.

The new overlay is 280 bytes at disposable fixture address `47fa0300`, using the earlier persistent admission helpers at `47fa0000`. Hooks replace copier tail `4029c518`, normal setup call `4008d318`, and alternate diagnostic call `4008d326` only in emulator memory. Code is host-loaded: delivery by the real loader/copier and physical executable ownership/cache handoff remain unverified. Original firmware, raw candidates and prior UI guard blob hashes are unchanged.

## Success and refusal

The seed helper requires zero state, matching pointer/header/size and the observed startup return. It saves registers/SR, raises IPL7 for the update, restores incoming state, and replays displaced vector setup. The normal helper checks the boot-mode bit and observed return, consumes COLD using the native single-use helper, restores registers/SR and transfers to complete stock normal setup. Both continuous runs show INITIALIZING already present before `4009d0d8` writes setup flags and still present at setup's final return.

Six seed controls cover valid entry, LIVE, FAILED, poison, wrong return and bad header. Five normal refusal controls cover LIVE, zero, poison, diagnostic flags and wrong return. A separate actual stock mode-branch control enters the patched diagnostic call and confirms neither diagnostic setup function nor note initializer runs. Custom instructions pass the existing ISA_C/MOVE audit.

Refusal writes FAILED, disables context PTR/READY, masks interrupts and enters an explicit self-loop. Controlled tests preserve setup flags, note pool, queue, context slots and audio vector. Metadata changes are explicitly limited to PTR and READY. Failure does not unwind the helper frame or return into stock callers that ignore failure. This is a proposed cold-core stop, not a graceful stock shutdown, recovery UI, live refusal protocol or certified hardware-safe failure path. Hardware DMA/peripherals, watchdog and non-maskable events are not excluded by these instruction tests.

## Provenance limitation demonstrated

The negative control deliberately reruns the actual copier on a LIVE fixture and supplies the expected seed return address. The copier recreates zero, and the seed accepts COLD again. This confirms that header/return/zero checks do not establish a non-replayable boot identity. The control injects replay and a forged return; it does not demonstrate a reachable stock warm path. Stock warm reachability/exclusion remains unproven.

No completion-to-LIVE hook is installed. The normal cold run remains INITIALIZING even when the modeled UI appears. Existing stock/context producer admission still follows its original gates and READY, not this new phase; this overlay is not a complete implementation of the policy's producer closure. Earlier native UI guards were tested separately and are not patched into these startup runs. Shared initializer, command and other warm admission routes also remain unguarded.

## Next focused work

Establish the actual full startup completion contract and a safe LIVE/feature-disabled decision, including when input producers can first run. Then connect those transitions and the previously tested UI guards in one PC run. Fresh-boot replay exclusion, global/physical storage ownership, delivered executable placement/cache coherence and hardware timing remain separate blockers. Do not flash this experiment.
'''
Path('outputs/Digitone-E04-PC-native-cold-admission-review.md').write_text(review)
incident=Path('outputs/Digitone-E04-hardware-startup-incident.md');marker='## Thirtieth follow-up: native cold seed/claim experiment'
if marker not in incident.read_text():incident.write_text(incident.read_text()+'\n\n'+marker+'\n\nHost-loaded 280-byte native overlay seeds COLD after copier and claims INITIALIZING before normal setup flags in both default/restored loader-derived PC startup runs. Six seed, five refusal and one actual diagnostic-branch controls pass. Refusal uses a proposed interrupt-masked core stop, not a verified graceful/hardware failure path. Forged copier replay recreates a permit, demonstrating provenance checks are insufficient by themselves; reachable stock warm replay is not established. Completion-to-LIVE, producer gates, shared initializer/command guards and packaged code delivery remain unintegrated. Firmware/raw/previous overlay hashes unchanged. See `Digitone-E04-PC-native-cold-admission-review.md`.\n')
policy=Path('outputs/Digitone-E04-PC-reinitialization-protection-policy.md');marker='## Native cold seed/claim PC experiment'
if marker not in policy.read_text():policy.write_text(policy.read_text()+'\n\n'+marker+'\n\nSeparate host-loaded cold overlay reaches stock UI with native COLD seed and INITIALIZING claim before normal setup mutation. Proposed masked failure stop is tested only on the PC. Forged copier replay demonstrates return/header/zero checks cannot alone certify fresh boot. LIVE completion, actual producer closure and shared initializer/command admission remain absent; prior UI guards are not yet joined into startup. See `Digitone-E04-PC-native-cold-admission-review.md`.\n')
print(json.dumps(summary,indent=2))
