import pathlib,json
info=json.loads(pathlib.Path('work/packed-context-build.json').read_text())
source=pathlib.Path('work/test-fast-pitch-hook-ABI.py').read_text()
source=source.replace("blob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()","blob=pathlib.Path('work/packed-context-overlay.bin').read_bytes();layout="+repr(info['layout']))
source=source.replace("blob[:1892]","blob[:"+str(info['code_bytes'])+"]")
source=source.replace('Digitone-fast-pitch-hook-ABI.json','Digitone-packed-context-hook-ABI.json')
exec(compile(source,'packed-native-hook-ABI','exec'))
