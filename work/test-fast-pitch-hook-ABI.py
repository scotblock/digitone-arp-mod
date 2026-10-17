import pathlib
source=pathlib.Path('work/test-native-arp-controlled.py').read_text()
prefix=pathlib.Path('work/test-native-arp-overlays.py').read_text().split('def run(mode):')[0]
prefix='\n'.join(x for x in prefix.splitlines() if not x.startswith('subprocess.run('))
line=next(x for x in source.splitlines() if x.startswith('exec(pathlib.Path'))
source=source.replace(line,"exec("+repr(prefix)+")\nblob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()")
source=source.replace('m.install_isa_patches_scoped(blob,RAM)','m.install_isa_patches_scoped(blob[:1892],RAM)')
source=source.replace('outputs/Digitone-native-arp-controlled-results.json','outputs/Digitone-fast-pitch-hook-ABI.json')
exec(compile(source,'fast-pitch-hook-ABI','exec'))
