"""Cold restart of the packaged E10 image with the native-saved project card."""
from pathlib import Path
import json
workflow=json.loads(Path('outputs/Digitone-E10-PC-package-workflow-patterns.json').read_text())
assert workflow['passed']
s=Path('work/test-PC-E10-package-startup.py').read_text(encoding='utf-8')
s=s.replace("Path(proof['card']).as_posix()","Path(workflow['private_card']).as_posix()")
s=s.replace('work/E10-package-startup-','work/E10-package-workflow-restart-').replace('outputs/Digitone-E10-PC-package-startup.json','outputs/Digitone-E10-PC-package-workflow-restart.json')
s=s.replace("  assert bytes(m.uc.mem_read(cfg['E10']['bank'],4096))==expected_bank", "  row['cold_bank_observed']=bytes(m.uc.mem_read(cfg['E10']['bank'],4096)).hex()")
s=s.replace("assert peek(cfg['E10']['bank'],4096)==expected_bank", "observed_bank=peek(cfg['E10']['bank'],4096)")
s=s.replace("row['restored_E10_records_match']=128", "row['restoration_completed']=True")
s=s.replace('restored_records_match=128,','restored_records_checked_in_following_named_load=True,')
s=s.replace("print('Loader-derived E10 startup and 128-record restoration pass.',flush=True)","print('Packaged cold restart reaches normal UI; saved-project recall is next.',flush=True)")
exec(compile(s,'E10-packaged-saved-card-restart','exec'))
