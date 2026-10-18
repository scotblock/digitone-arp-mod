"""Separate internal E10 loader-test container; no release or device update."""
from pathlib import Path
import sys,json,hashlib,subprocess
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections
from dt2.elz import depack_section
sha=lambda b:hashlib.sha256(b).hexdigest()
folder=Path('work/os144');main=(folder/'PC_ONLY-E10-life-main.bin').read_bytes();payload=(folder/'PC_ONLY-E10-life-payload.bin').read_bytes()
c=json.loads((folder/'PC_ONLY-E10-life-layout.json').read_text());full=json.loads((folder/'PC_ONLY-E10-life-full-layout.json').read_text())
assert sha(main)==c['main_sha256'] and sha(payload)==c['payload_sha256']
for a,b in [('main',main),('payload',payload)]: (folder/('PC_ONLY-E10-package-'+a+'.bin')).write_bytes(b)
packed=folder/'PC_ONLY-E10-package-packed.bin'
run=subprocess.run(['work/c-verification/pack-review.exe',str(folder/'PC_ONLY-E10-package-main.bin'),str(packed)],capture_output=True,text=True)
assert run.returncode==0,run.stdout+run.stderr
source=Path('work/build-os144-E03-pc.py').read_text(encoding='utf-8').split('unchanged,_=container()')[0]
source=source.replace('C:/Users/bryan/AppData/Local/Temp/Digitone_and_Digitone_Keys_OS1.44.syx','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx').replace('E03-main-packed.bin','PC_ONLY-E10-package-packed.bin').replace('emulator-E02-main.bin','PC_ONLY-E10-package-main.bin')
ns={};exec(compile(source,'E10-stock-container-writer','exec'),ns)
unchanged,_=ns['container']();assert unchanged==ns['stock_c'] and ns['syx'](unchanged)==ns['raw']
container,entries=ns['container'](packed.read_bytes(),512)
assert len(container)<0x1e0000-8 and 0x80000+((len(container)+0x3ffff)//0x40000)*0x40000<=0x380000
out=folder/'PC_ONLY-E10-package-loader-test.syx';out.write_bytes(ns['syx'](container))
decoded,actual=sections(out)
# The transport decoder includes the final 101-byte packet's zero fill.
assert decoded[:len(container)]==container and not decoded[len(container):].strip(b'\0') and len(decoded)-len(container)<101 and actual==entries
stock_sections={sid:ns['stock_c'][off:off+n] for sid,off,n,dst in ns['entries']}
for sid,off,n,dst in entries:
 data=decoded[off:off+n]
 if sid==3:assert depack_section(data)==main
 else:assert data==stock_sections[sid],sid
for cfg in [c,full]:
 cfg.update(candidate=str(out.resolve()),candidate_sha256=sha(out.read_bytes()),sections=entries,internal_loader_test_only=True,firmware_release_created=False,hardware_ready=False,main_sha256=sha(main),payload_sha256=sha(payload),stock_writer_byte_exact=True,candidate_decompression_exact=True)
 cfg['historical_parent_limitations']=cfg.get('limitations',[])
 cfg['limitations']=['Internal PC-only container for loader/startup/playback integration. Not a hardware-ready release.','Stock power mechanism is an accepted inherited assumption; abrupt-loss recovery is not guaranteed.','Physical RAM ownership/cache/timing and complete device update receiver are not certified by packaging.']
(folder/'PC_ONLY-E10-package-layout.json').write_text(json.dumps(c,indent=2),encoding='utf-8');(folder/'PC_ONLY-E10-package-full-layout.json').write_text(json.dumps(full,indent=2),encoding='utf-8')
e09a=sha(Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx').read_bytes());assert e09a=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
r=dict(PC_only=True,passed=True,internal_loader_test_only=True,firmware_release_created=False,hardware_ready=False,candidate=str(out),candidate_sha256=sha(out.read_bytes()),main_sha256=sha(main),payload_sha256=sha(payload),main_identical_to_lifecycle_image=True,stock_writer_byte_exact=True,independent_MAIN_decompression_exact=True,non_MAIN_sections_byte_exact=True,container_bytes=len(container),syx_bytes=out.stat().st_size,packed_MAIN_bytes=packed.stat().st_size,logical_container_512_aligned=len(container)%512==0,source_copy_bytes=len(payload),E09A_unchanged=True,E09A_sha256=e09a,limits=c['limitations'])
Path('outputs/Digitone-E10-PC-package-container.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print('Internal PC package verified:',r['container_bytes'],'container bytes;',r['source_copy_bytes'],'copied bytes. No release/device update.')
