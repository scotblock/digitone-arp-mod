"""Native ColdFire M1 scheduler overlay. Never packages or edits E07 files."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
B=0x47be6000;S=0x47be7000;ARENA=0x47be7200
D=B;SORT=B+0x800;CLEAR=B+0x900;COPY=B+0x980;EMIT=B+0xa00;HOOK=B+0xb80;RETIRE=B+0xc80;INIT=B+0xd00
parts=[];regions=[]
def add(name,address,a,limit):
 code=a.done();assert len(code)<=limit,(name,len(code),limit);parts.append((address,code));regions.append({'name':name,'base':address,'bytes':len(code)})
def absop(a,op,value):absolute(a,op,value)
def js(a,value):absop(a,'4eb9',value)
def jmp(a,value):absop(a,'4ef9',value)
# Clear held-note membership and reset its sorted count/cursor.
a=Asm();absop(a,'41f9',S+96);a.emit('7220');a.label('loop');a.emit('42985381');a.branch('6600','loop');absop(a,'42b9',S+16);absop(a,'42b9',S+20);a.emit('4e75');add('clear_members',CLEAR,a,128)
# Sorted/deduplicated note set from 128 membership bytes, capped at eight.
a=Asm();absop(a,'41f9',S+96);a.emit('70007200');a.label('loop');a.emit('14300800');a.branch('6700','next');a.emit('27801c4052810c8100000008');a.branch('6400','done');a.label('next');a.emit('52800c8000000080');a.branch('6500','loop');a.label('done');a.emit('27410010202b0014b081');a.branch('6500','end');a.emit('42ab0014');a.label('end');a.emit('4e75');add('sort_members',SORT,a,256)
# Snapshot all value fields; explicitly discard borrowed pointer/link fields.
a=Asm();a.emit('204a');absop(a,'43f9',S+224);a.emit('720d');a.label('loop');a.emit('201822c05381');a.branch('6600','loop');absop(a,'42b9',S+264);absop(a,'42b9',S+272);a.emit('4e75');add('copy_template',COPY,a,128)
# Build one owned descriptor. Successor is the original stock descriptor;
# retirement must bypass stock free for exactly ARENA, then clear busy.
a=Asm();a.emit('202b0014222b0010b081');a.branch('6500','index');a.emit('700042ab0014');a.label('index');a.emit('24330c40');absop(a,'41f9',S+224);absop(a,'43f9',ARENA);a.emit('720d');a.label('copy');a.emit('201822c05381');a.branch('6600','copy');absop(a,'41f9',ARENA);a.emit('70012140001042a8001442a8001811420014202b00242140001c2147002442a80028214a00307001274001182747012052ab0030202b0020d1ab001852ab0014');absop(a,'203c',ARENA);a.emit('4e75');add('emit_descriptor',EMIT,a,384)
# Dispatcher source arg -> D0 descriptor to consume. Called inside a fully
# preserving interrupt-masked wrapper. No host callback implements decisions.
a=Asm();a.emit('246f0004');absop(a,'47f9',S);a.emit('200ab0bc');a.emit(struct.pack('>I',ARENA).hex());a.branch('6700','done')
a.emit('20130c804d314131');a.branch('6600','done');a.emit('4aab0004');a.branch('6600','enabled');a.emit('42ab0008');a.branch('6000','done')
a.label('enabled');a.emit('202b0020');a.branch('6f00','invalid_config');a.emit('222b0024');a.branch('6f00','invalid_config');a.emit('b280');a.branch('6400','invalid_config');a.emit('0c8040000000');a.branch('6400','invalid_config');a.emit('4aab0118');a.branch('6600','done')
absop(a,'2e39',0x80004614);a.emit('2c124aab0008');a.branch('6700','source');a.emit('0c8600000004');a.branch('6700','stop');a.emit('4aab000c');a.branch('6600','source');a.emit('206b0028');a.emit('4a88');a.branch('6700','stop');a.emit('20100c8000000001');a.branch('6600','stop');a.emit('200790ab001c');a.branch('6b00','source');a.emit('42ab000852ab0034');a.branch('6000','source')
a.label('stop');a.emit('42ab000852ab0038');js(a,CLEAR)
a.label('source');a.emit('0c8600000001');a.branch('6200','timer');a.emit('4aaa0004');a.branch('6600','done');a.emit('282a00100c8400000001');a.branch('6500','done');a.emit('0c8400000008');a.branch('6200','done');a.emit('202a002c0c8000000002');a.branch('6700','live');a.emit('0c8000000001');a.branch('6600','done');a.emit('202a00080c8000000001');a.branch('6600','done');a.emit('202a001c');a.branch('6f00','done');a.emit('0c8040000000');a.branch('6400','done')
# Prevalidate before membership mutation.
a.emit('7600');a.label('validate');a.emit('7000103238140c8000000080');a.branch('6400','done');a.emit('5283b684');a.branch('6500','validate');js(a,CLEAR);a.emit('7600');absop(a,'41f9',S+96);a.label('mark');a.emit('7000103238147201118108005283b684');a.branch('6500','mark');js(a,SORT);js(a,COPY);a.emit('42ab000c70012740000827470018202a001cd080d0aa00242740001c42aa0010');jmp(a,EMIT)
# Live sources have zero/infinite gate. Step timing uses independent config.
a.label('live');a.emit('0c8400000001');a.branch('6600','done');a.emit('7000102a00140c8000000080');a.branch('6400','done');a.emit('2800202a00080c8000000001');a.branch('6600','live_off');a.emit('4aab0008');a.branch('6700','live_new');a.emit('4aab000c');a.branch('6600','live_mark');a.label('live_new');js(a,CLEAR);a.emit('27470018');a.label('live_mark');absop(a,'41f9',S+96);a.emit('720111814800');js(a,SORT);js(a,COPY);a.emit('7001274000082740000c42aa0010');a.branch('6000','done')
a.label('live_off');a.emit('0c8000000002');a.branch('6600','done');a.emit('4aab00084aab000c');a.branch('6700','done');absop(a,'41f9',S+96);a.emit('42304800');js(a,SORT);a.emit('4aab0010');a.branch('6600','done');a.emit('42ab000852ab003c');a.branch('6000','done')
a.label('timer');a.emit('0c8600000003');a.branch('6600','done');a.emit('4aab0008');a.branch('6700','done');a.emit('200790ab0018');a.branch('6b00','done');a.emit('beab0120');a.branch('6700','done');jmp(a,EMIT)
a.label('invalid_config');a.emit('42ab000852ab012c');a.label('done');a.emit('200a4e75');add('dispatch',D,a,2048)
# Main consumer's displaced compare/branch is replayed exactly.
a=Asm();save(a);a.emit('2f0a');js(a,D);a.emit('588f2f400028');restore(a);a.emit('2012bc80');a.branch('6600','other');jmp(a,0x400f40ba);a.label('other');jmp(a,0x400f4126);add('consumer_hook',HOOK,a,256)
# Exact arena-pointer check. Ordinary stock descriptors still go to stock free.
a=Asm();a.emit('b5fc'+struct.pack('>I',ARENA).hex());a.branch('6600','stock');absop(a,'42b9',S+280);a.emit('242a0030');jmp(a,0x400f49cc);a.label('stock');a.emit('242a00302f0a');jmp(a,0x400f49c6);add('retirement_hook',RETIRE,a,128)
# Native initializer used through a temporary PC call frame; startup not patched.
a=Asm();save(a);absop(a,'41f9',S);a.emit('7250');a.label('clear');a.emit('42985381');a.branch('6600','clear');absop(a,'41f9',ARENA);a.emit('7210');a.label('arena');a.emit('42985381');a.branch('6600','arena')
for off,val in [(0,0x4d314131),(32,5400000),(36,1350000),(288,0xffffffff)]:absop(a,'203c',val);absop(a,'23c0',S+off)
a.emit('202f0044');absop(a,'23c0',S+40);restore(a);a.emit('4e75');add('native_initialize',INIT,a,256)
blob=bytearray(0xe00)
for addr,code in parts:blob[addr-B:addr-B+len(code)]=code
Path('work/os144/E08-PC-native-M1-code.bin').write_bytes(blob)
main=Path('work/os144/E07-PC-main.bin').read_bytes();hooks=[]
for site,n,target in [(0x400f40b4,6,HOOK),(0x400f49c0,6,RETIRE)]:hooks.append({'site':site,'length':n,'target':target,'original':main[site-0x40000400:site-0x40000400+n].hex(),'replacement':'4ef9'+struct.pack('>I',target).hex()})
cfg={'PC_only':True,'firmware_modified':False,'base':B,'bytes':len(blob),'code_bytes':sum(r['bytes'] for r in regions),'state':S,'state_bytes':320,'arena':ARENA,'arena_bytes':64,'regions':regions,'entries':{'dispatch':D,'sort':SORT,'clear':CLEAR,'emit':EMIT,'consumer':HOOK,'retire':RETIRE,'init':INIT},'hooks':hooks,'limits':['Host loads code in additional PC-only RAM; no copier or hardware storage ownership proof.','Native initializer runs in an isolated PC frame, not a firmware startup installation.','M1 only; independent interval/gate config fixtures, no settings UI/persistence.']}
Path('work/os144/E08-PC-native-M1-layout.json').write_text(json.dumps(cfg,indent=2));print('Native code',cfg['code_bytes'],'bytes; dispatcher',next(r['bytes'] for r in regions if r['name']=='dispatch'))
