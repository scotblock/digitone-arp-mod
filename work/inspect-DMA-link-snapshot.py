import pathlib,sys,struct,json,zlib
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from emu import snapshot,edma_sw as e
b=snapshot._load_blob(str(next(pathlib.Path('work/continuous-emulator/snapshots').rglob('gui.snap'))))
records=[]
page=zlib.decompress(b['pages'][0xfc000000])
for ch in [30,42,47]:
 off=0x45000+ch*32;tcd=struct.unpack(e.TCD_FMT,page[off:off+32])
 records.append({'channel':ch,'CITER':hex(tcd[6]),'minor_count':e.iteration_count(tcd[6]),'minor_link_channel':e.link_channel(tcd[6]),'CSR':hex(tcd[10]),'major_link_enabled':bool(tcd[10]&32),'major_link_channel':(tcd[10]>>8)&63,'source':hex(tcd[0]),'dest':hex(tcd[5])})
pathlib.Path('outputs/Digitone-DMA-link-snapshot-clues.json').write_text(json.dumps({'scope':'Settled initial snapshot only; live descriptor chains are not proved by these samples','records':records},indent=2));print(records)

