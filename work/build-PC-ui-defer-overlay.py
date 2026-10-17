from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
BASE=0x47fa0000;stock=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;parts=[];layout={};modes=[]
def add(name,a):
 code=a.done();layout[name]={'address':BASE+sum(map(len,parts)),'size':len(code)};parts.append(code)
for name,site,length,load,resume,target in [('retained_defer',0x400e4e42,8,'206a008c',0x400e4e4a,0x400e4eae),('explicit_refuse',0x400e47f6,6,'2052',0x400e47fc,0x400e483c)]:
 a=Asm();a.emit('2f002f08');modes.append(BASE+sum(map(len,parts))+len(a.code)+1);a.emit('70014a80');a.branch('6700','stock');a.emit(load+'4a88');a.branch('6700','stock');a.emit('20100c80401c4714');a.branch('6600','stock');a.emit('2028ffc80c80401c467c');a.branch('6600','stock');a.emit('205f201f')
 if name=='explicit_refuse':a.emit('7000')
 absolute(a,'4ef9',target);a.label('stock');a.emit('205f201f');a.emit(stock[site-base:site-base+length].hex());absolute(a,'4ef9',resume);add(name,a)
blob=b''.join(parts);hooks=[]
for name,site,length in [('retained_defer',0x400e4e42,8),('explicit_refuse',0x400e47f6,6)]:hooks.append({'name':name,'site':site,'length':length,'stock':stock[site-base:site-base+length].hex(),'replacement':'4ef9'+struct.pack('>I',layout[name]['address']).hex()+'4e71'*((length-6)//2)})
Path('work/os144/PC_ONLY-ui-defer-overlay.bin').write_bytes(blob);Path('work/os144/PC_ONLY-ui-defer-overlay.json').write_text(json.dumps({'PC_only':True,'base':BASE,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'layout':layout,'hooks':hooks,'mode_immediate_bytes':modes,'admission':'MOVEQ live=1 compiled into each isolated PC helper. Host may set to0 for disabled/cold comparison; no persistent latch or startup provenance implemented.','placement':'disposable fixture address only; no hardware executable/RAM ownership claim'},indent=2));print('Built',len(blob),'bytes, disposable PC-only overlay')
