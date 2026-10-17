"""Native RAM records -> bounded PC file -> cold native load. No stock files."""
from pathlib import Path
import hashlib,json,tempfile,sys
sys.path.insert(0,'work')
import E10_step_bank as codec
ns={};exec(compile(Path('work/test-PC-E10-step-lifetime.py').read_text(),'E10-native-bank-tests','exec'),ns)
u=ns['u'];BANK=ns['BANK'];X=ns['X'];DATA=ns['DATA'];put=ns['put'];get=ns['get'];run=ns['run']
bank=bytes(u.mem_read(BANK,4096));digest=hashlib.sha256(b'PC fixture project identity; not a native project').hexdigest()
packed=codec.encode(bank,digest);assert len(packed)==4176 and codec.decode(packed,digest)==bank
with tempfile.TemporaryDirectory(prefix='E10-bank-',dir=Path('outputs').resolve()) as d:
 p=Path(d)/'fixture.e10seq';p.write_bytes(packed);restored=codec.decode(p.read_bytes(),digest)
 # Cold reset really destroys RAM settings. PC import is deliberately explicit.
 put(0x47be2840,0x434f4c44);assert run('init')==1 and bytes(u.mem_read(BANK,4096))==bytes(4096)
 put(0x47be2840,0x4c495645);u.mem_write(BANK,restored)
 assert run('load',[127,DATA])==1 and get(X+8)==16
checks=[]
def rejects(raw,project=digest):
 before=bytes(u.mem_read(X,64))+bytes(u.mem_read(BANK,4096))
 try:codec.decode(raw,project)
 except ValueError:pass
 else:raise AssertionError('invalid sidecar accepted')
 assert before==bytes(u.mem_read(X,64))+bytes(u.mem_read(BANK,4096))
for cut in [0,7,15,47,79,80,4175]:rejects(packed[:cut])
rejects(packed+b'\0');rejects(packed,'0'*64)
checks.append('Truncation, appended data and another project identity reject before any emulated state write.')
for offset in [0,8,10,12,14,15,48,79,80,4175]:
 bad=bytearray(packed);bad[offset]^=1;rejects(bytes(bad))
checks.append('Header/schema and bank digest failures reject.')
for offset,value in [(4,2),(5,2),(6,0),(7,12),(8,36),(9,1),(12,25),(27,231)]:
 badbank=bytearray(bank);badbank[offset]=value;badbank[28:32]=sum(badbank[:28]).to_bytes(4,'big')
 bad=bytearray(packed);bad[80:]=badbank;bad[48:80]=hashlib.sha256(badbank).digest();rejects(bytes(bad))
checks.append('Malformed version, fields and signed offsets reject even when both checksums have been recomputed.')
assert codec.decode(codec.encode(bytes(4096),digest),digest)==bytes(4096)
checks.append('An empty project bank is a valid disabled/default state.')
out=dict(PC_only=True,passed=True,patterns=128,native_record_round_trip=True,PC_file_survives_cold_reset=True,PC_import_is_host_fixture=True,native_project_save_load=False,automatic_pattern_binding=False,checks=checks,limits=['This is a separate PC sidecar, not native Digitone project persistence. No native save/load or pattern-change callback invokes it.','Project identity is supplied by the PC caller; matching an actual project and maintaining it after native edits are not integrated.'])
Path('outputs/Digitone-E10-PC-step-bank-file.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
