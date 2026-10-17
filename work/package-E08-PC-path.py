from pathlib import Path
import sys,json,hashlib,subprocess
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections
from dt2.elz import depack_section
sha=lambda b:hashlib.sha256(b).hexdigest()
e07=Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx')
assert sha(e07.read_bytes())=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
proc=subprocess.run(['work/c-verification/pack-review.exe','work/os144/E08-PC-layout-main.bin','work/os144/E08-PC-path-packed.bin'],capture_output=True,text=True)
assert proc.returncode==0,proc.stdout+proc.stderr
s=Path('work/build-os144-E03-pc.py').read_text().split('unchanged,_=container()')[0]
s=s.replace('inputs/Digitone_and_Digitone_Keys_OS1.44.syx','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx').replace('E03-main-packed.bin','E08-PC-path-packed.bin').replace('emulator-E02-main.bin','E08-PC-layout-main.bin')
env={};exec(compile(s,'E08-stock-writer','exec'),env)
unchanged,_=env['container']();assert unchanged==env['stock_c'] and env['syx'](unchanged)==env['raw']
c,entries=env['container'](env['packed'],512)
assert len(c)<0x1e0000-8 and 0x80000+((len(c)+0x3ffff)//0x40000)*0x40000<=0x380000
out=Path('work/os144/E08-PC-path-candidate.syx');out.write_bytes(env['syx'](c))
old=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text());new=json.loads(Path('work/os144/E08-PC-install-layout.json').read_text())
cfg={**old,**new,'regions':old['regions']+new['regions'],'components':old['components']+new['regions']+new['data_regions'],'MIDI_state':old['MIDI_state'],'candidate':str(out.resolve()),'candidate_sha256':sha(out.read_bytes()),'sections':entries,'stock_writer_byte_exact':True,'hardware_ready':False}
cc,ee=sections(out);_,off,n,_=next(e for e in ee if e[0]==3)
assert depack_section(cc[off:off+n])==Path('work/os144/E08-PC-layout-main.bin').read_bytes()
cfg['candidate_decompression_exact']=True
Path('outputs/Digitone-E08-PC-path-layout.json').write_text(json.dumps(cfg,indent=2))
print('Internal PC container verified',out.stat().st_size,'bytes; E07 unchanged')
