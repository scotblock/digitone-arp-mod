from pathlib import Path
import sys,json,hashlib,subprocess
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections
from dt2.elz import depack_section
sha=lambda b:hashlib.sha256(b).hexdigest()
e05=Path('outputs/Digitone_OS1.44E05_SCALE_ARP_PC_ONLY.syx');assert sha(e05.read_bytes())=='17fbe13d6b2aad9c096df7ac20fd4499a7bb0951e146fd0fd0aaeace4037e474'
proc=subprocess.run(['work/c-verification/pack-review.exe','work/os144/E06-PC-main.bin','work/os144/E06-PC-main-packed.bin'],capture_output=True,text=True);assert proc.returncode==0,proc.stdout+proc.stderr
s=Path('work/build-os144-E03-pc.py').read_text().split('unchanged,_=container()')[0];s=s.replace('inputs/Digitone_and_Digitone_Keys_OS1.44.syx','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx').replace('E03-main-packed.bin','E06-PC-main-packed.bin').replace('emulator-E02-main.bin','E06-PC-main.bin');env={};exec(compile(s,'E06-stock-writer','exec'),env)
unchanged,_=env['container']();assert unchanged==env['stock_c'] and env['syx'](unchanged)==env['raw'];c,entries=env['container'](env['packed'],512);assert len(c)<0x1e0000-8 and 0x80000+((len(c)+0x3ffff)//0x40000)*0x40000<=0x380000
out=Path('work/os144/E06-PC-candidate.syx');out.write_bytes(env['syx'](c));Path('work/os144/E06-PC-container.bin').write_bytes(c)
cfg=json.loads(Path('outputs/Digitone-E06-PC-candidate-layout.json').read_text());cfg.update(candidate=str(out.resolve()),candidate_sha256=sha(out.read_bytes()),syx_bytes=out.stat().st_size,container_bytes=len(c),sections=entries,codec_roundtrip=proc.stdout.strip(),stock_writer_byte_exact=True,candidate_decompression_exact=True,hardware_ready=False)
cc,ee=sections(out);sid,off,n,dest=next(e for e in ee if e[0]==3);assert depack_section(cc[off:off+n])==Path('work/os144/E06-PC-main.bin').read_bytes();Path('outputs/Digitone-E06-PC-candidate-layout.json').write_text(json.dumps(cfg,indent=2));print('Packaged E06 for PC:',out.stat().st_size,'bytes; E05 preserved')
