from pathlib import Path
import json,hashlib
specs=[json.loads(Path('work/os144/PC_ONLY-'+n+'.json').read_text()) for n in ['persistent-admission','cold-admission-overlay','input-live-overlay','release-reset-overlay']]
manifest={'PC_only':True,'new_machine_code_generated':False,'components':[{'base':s['base'],'bytes':s['bytes'],'sha256':s['sha256']} for s in specs],'hooks':[h for s in specs for h in s['hooks']],'limits':['Uses existing fixture-only host-loaded executable addresses. No container, physical cache or placement certification.','UI fixtures establish retained/explicit LIVE refusal; unknown computed/interior callers remain unproven.']}
assert len({h['site'] for h in manifest['hooks']})==len(manifest['hooks'])
Path('work/os144/PC_ONLY-joined-UI-layout.json').write_text(json.dumps(manifest,indent=2));print('Joined layout',len(manifest['hooks']),'distinct sites')
