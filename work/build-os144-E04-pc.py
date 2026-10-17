from pathlib import Path
import sys,struct,json,hashlib,subprocess
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections
from dt2.elz import depack_section
sha=lambda b:hashlib.sha256(b).hexdigest()
e03=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx')
before=sha(e03.read_bytes());assert before=='8775320f161cb02efa8f51b2671034baf73eeec95f4bb66ffc20a29e9b0a2a3d'
c,es=sections(e03);offset,length,_=next(e[1:] for e in es if e[0]==3)
old=depack_section(c[offset:offset+length]);assert old==Path('work/os144/emulator-E02-main.bin').read_bytes()
payload=Path('work/os144/fallback-final-payload.bin').read_bytes();original=Path('work/os144/packed-context-overlay.bin').read_bytes()
assert len(payload)==2492 and payload[:2212]==original and sha(payload)=='eb908e6ae5ac26490bf4fea0216ba8fcfbff258a8f8ea0f7159342a00e14d2e7'
BASE,STAGE=0x40000400,0x4029c4b0
main=bytearray(old)
assert main[STAGE+14-BASE:STAGE+18-BASE]==struct.pack('>I',553)
assert main[0x400ffed0-BASE:0x400ffed6-BASE]==bytes.fromhex('4ef947be055c')
assert main[STAGE+256-BASE:]==original
main[STAGE+14-BASE:STAGE+18-BASE]=struct.pack('>I',623)
main[0x400ffed0-BASE:0x400ffed6-BASE]=bytes.fromhex('4ef947be08a4')
main[STAGE+256-BASE:]=payload;main=bytes(main)
changed=[i for i,(a,b) in enumerate(zip(old,main)) if a!=b]
assert all(STAGE+14-BASE<=i<STAGE+18-BASE or 0x400ffed0-BASE<=i<0x400ffed6-BASE for i in changed)
assert len(main)==len(old)+280
Path('work/os144/emulator-E04-main.bin').write_bytes(main)
x=subprocess.run(['work/c-verification/pack-review.exe','work/os144/emulator-E04-main.bin','work/os144/E04-main-packed.bin'],capture_output=True,text=True)
assert x.returncode==0,x.stdout+x.stderr;print(x.stdout,flush=True)
source=Path('work/build-os144-E03-pc.py').read_text().split('unchanged,_=container()')[0]
source=source.replace('E03','E04').replace('emulator-E02-main.bin','emulator-E04-main.bin')
env={};exec(compile(source,'E04-container-writer','exec'),env)
unchanged,_=env['container']();assert unchanged==env['stock_c'] and env['syx'](unchanged)==env['raw']
container,entries=env['container'](env['packed'],512)
assert len(container)<0x1e0000-8 and 0x80000+((len(container)+0x3ffff)//0x40000)*0x40000<=0x380000
out=Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx');out.write_bytes(env['syx'](container));Path('work/os144/E04-container.bin').write_bytes(container)
assert sha(e03.read_bytes())==before and sha(original)==sha(Path('work/os144/packed-context-overlay.bin').read_bytes())
r={'PC_only':True,'hardware_ready':False,'output':str(out.resolve()),'output_sha256':sha(out.read_bytes()),'E03_unchanged_sha256':before,'main_sha256':sha(main),'main_bytes':len(main),'packed_main_bytes':len(env['packed']),'container_bytes':len(container),'syx_bytes':out.stat().st_size,'sections':entries,'compression_level':2,'C_codec_roundtrip':x.stdout.strip(),'Python_decompression_exact':True,'unchanged_stock_writer_byte_exact':True,'changes_from_E03':{'copier_count':{'site':hex(STAGE+14),'old':553,'new':623},'initializer_target':{'site':'0x400ffed0','old':'0x47be055c','new':'0x47be08a4'},'appended_fallback_bytes':280,'fallback_end':'0x47be09bc','pointer':'0x47be1000'},'limits':['PC-only candidate; physical cache coherence and audio/DMA timing remain unverified.','Display OS version remains 1.44; identify candidate by filename and checksum.','No hardware update or application USB freeze is performed.']}
Path('outputs/Digitone-OS1.44E04-packaging.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
