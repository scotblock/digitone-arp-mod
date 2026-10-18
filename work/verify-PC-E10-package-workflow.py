"""Consolidate scoped packaged E10 edit/save/restart/recall evidence."""
from pathlib import Path
import json,hashlib,ast
hash_file=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
reports={k:json.loads(Path('outputs/Digitone-E10-PC-package-workflow-'+v+'.json').read_text()) for k,v in [('editor','patterns'),('restart','restart'),('recall','recall'),('handoff','handoff'),('copy_clear','copy'),('reset','reset')]}
checks=[]
def check(name,value):
 checks.append({'check':name,'passed':bool(value)})
cfg=json.loads(Path('work/os144/PC_ONLY-E10-package-full-layout.json').read_text())
check('Internal package hash remains unchanged',hash_file(cfg['candidate'])==cfg['candidate_sha256'])
for name,r in reports.items():check(name+' execution passes',r.get('passed'))
r=reports['editor'];check('Native distinct two-pattern edit and named save/load',r.get('two_pattern_panel_recall') and r.get('saved_project_reloaded') and r.get('post_reload_pattern_recall'))
check('No editor code or bank overlay',not r.get('bank_host_written') and not r.get('settings_host_written') and not r.get('helpers_host_loaded') and not r.get('hooks_host_patched'))
check('A04 explicitly contains the programmed step-2 rest',r['expected_fields'][1][2]==0xfffd)
r=reports['recall'];check('Cold restart, saved native load and both panel programs recalled',r.get('restart_and_saved_project_recall') and r.get('post_restart_panel_fields_match') and r.get('all_records_recovered'))
r=reports['handoff'];check('Actual consumed handoff, distinct programs and rests',r.get('confirmed_held_handoff') and r.get('matching_fields_after_consumed_handoff') and r.get('rest_consumption_observed') and r.get('distinct_programs_consumed'))
r=reports['copy_clear'];check('Paste/undo and clear/undo match retained image',r.get('pattern_paste_and_undo_preserve_steps') and r.get('clear_and_undo_retain_steps') and r.get('all_128_retained_records_match_bank'))
r=reports['reset'];check('Ten guarded reset entries preserve storage',len(r['cases'])==10 and all(v.get('nonempty_bank_and_all_new_storage_unchanged') for v in r['cases']))
check('Lifecycle MAIN and copied code remain unchanged',hash_file('work/os144/PC_ONLY-E10-package-main.bin')==hash_file('work/os144/PC_ONLY-E10-life-main.bin') and hash_file('work/os144/PC_ONLY-E10-package-payload.bin')==hash_file('work/os144/PC_ONLY-E10-life-payload.bin'))
check('Working E09A firmware remains unchanged',hash_file('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx')=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c')
scripts=sorted(Path('work').glob('test-PC-E10-package-workflow*.py'))+[Path(__file__)]
for p in scripts:ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
out=dict(PC_only=True,passed=all(v['passed'] for v in checks),checks=checks,candidate_sha256=cfg['candidate_sha256'],reports={k:'outputs/Digitone-E10-PC-package-workflow-'+v+'.json' for k,v in [('editor','patterns'),('restart','restart'),('recall','recall'),('handoff','handoff'),('copy_clear','copy'),('reset','reset')]},source_sha256={str(p):hash_file(p) for p in scripts},firmware_code_changed=False,firmware_release_created=False,hardware_ready=False,stock_power_handling='Accepted inherited assumption; no abrupt-loss guarantee.',limits=['Private PC cards and serialized loader/UI handoffs; inherited ISA, timer, DDR, DSP, input and peripheral model fixtures remain.','Stopped copy/undo and trig clear/undo retain arp settings by stock semantics. Ten reset cases exercise direct guarded entries with admission fixtures, not physical reset overlap.','M1 prototype only. No new device update, physical timing/cache validation or power-system redesign.'])
Path('outputs/Digitone-E10-PC-package-workflow-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'passed':out['passed'],'checks':checks},indent=2),flush=True)
if not out['passed']:raise SystemExit(1)
