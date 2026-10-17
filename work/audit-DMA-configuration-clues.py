import sys,pathlib,struct,json,zlib
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from emu import snapshot
out={'snapshots':[],'literals':[]}
for p in pathlib.Path('work/continuous-emulator/snapshots').rglob('*.snap'):
 b=snapshot._load_blob(str(p));page=zlib.decompress(b['pages'][0xfc000000])
 out['snapshots'].append({'file':str(p),'CR':hex(struct.unpack_from('>I',page,0x44000)[0]),'priority_bytes':page[0x44100:0x44140].hex()})
for f,base,skip in [('work/section-2.bin',0x80000400,4),('work/section-3.bin',0x40000400,0)]:
 data=pathlib.Path(f).read_bytes()[skip:]
 for off in range(len(data)-3):
  v=struct.unpack_from('>I',data,off)[0]
  if 0xfc044000<=v<0xfc044140:
   out['literals'].append({'file':f,'address':hex(base+off),'value':hex(v),'before':data[max(0,off-6):off].hex(),'after':data[off+4:off+18].hex()})
pathlib.Path('outputs/Digitone-DMA-configuration-clues.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
