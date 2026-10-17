from pathlib import Path
import sys, json, hashlib
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'outputs'))
from digitone_queue_snapshot_checks import checks
result=checks()
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
result['unchanged_input_sha256']=dict(zip([p.name for p in paths],hashes))
(root/'outputs/Digitone-queue-snapshot-check-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(result['scenarios_passed'],'scenarios;',result['encoding_cases'],'encodings; firmware hashes unchanged')
