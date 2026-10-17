"""Local helper image and matching executed-loader guest environment."""
import pathlib,os,json,struct,hashlib,collections,traceback,sys
prefix=pathlib.Path('work/test-native-arp-overlays.py').read_text().split('\ndef run(mode):')[0]
prefix='\n'.join(line for line in prefix.splitlines() if not line.startswith('subprocess.run('))
exec(compile(prefix,'native-environment','exec'))
blob=pathlib.Path('work/cache-context-overlay.bin').read_bytes()
paths=ExperimentalPaths(str(pathlib.Path('work/cache-loader-derived-arp-emulator').resolve()),SYX.name,paths.devices_dir)
os.environ.update(paths.env())
startup=json.loads(pathlib.Path('outputs/Digitone-cache-context-startup-playback.json').read_text());assert startup['passed']
pre=pathlib.Path('work/cache-loader-fixture.py').read_text().split('originalspin=longrun.spin')[0]
pre=pre.replace('work/fast-pitch-overlay.bin','work/cache-context-overlay.bin')
ns={};exec(compile(pre,'matching-ephemeral-flash','exec'),ns)
assert hashlib.sha256(ns['main']).hexdigest()==startup['loader']['image_sha256']
from emu import dspboot
loader_flash=bytes(ns['flash']);dspboot.build_flash=lambda *args,**kwargs:loader_flash
