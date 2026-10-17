from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
B=0x47be5a00;V=B+0x300;regions=[];blob=bytearray(1024)
def absop(a,op,v):absolute(a,op,v)
def add(name,addr,a):
 code=a.done();blob[addr-B:addr-B+len(code)]=code;regions.append({'name':name,'base':addr,'bytes':len(code)})
# validate_word(word): return exact marked word or zero (legacy/invalid).
a=Asm();a.emit('202f0004220002810000f8000c810000a800');a.branch('6600','bad');a.emit('220002810000007f0c8100000001');a.branch('6500','bad');a.emit('0c8100000063');a.branch('6200','bad');a.emit('4e75');a.label('bad');a.emit('70004e75');add('validate_tagged_word',V,a)
for name,addr,stock,read_off,write_off in [('encode',B,0x400081f6,0x9e,0xa6),('decode',B+0x180,0x4000818a,0xa6,0x9e)]:
 a=Asm();save(a);a.emit('246f0044266f0048');a.emit('2f0b2f0a');absop(a,'4eb9',stock);a.emit('508f28004a00');a.branch('6700','end');a.emit('7000302b'+struct.pack('>H',read_off).hex());a.emit('2f00');absop(a,'4eb9',V);a.emit('588f3540'+struct.pack('>H',write_off).hex());a.label('end');a.emit('2f440000');restore(a);a.emit('4e75');add(name+'_MIDI_settings',addr,a)
Path('work/os144/E08-PC-settings-codec-bridge.bin').write_bytes(blob)
c={'PC_only':True,'base':B,'bytes':1024,'regions':regions,'entries':{'encode':B,'decode':B+0x180,'validate':V},'stock_entries':{'encode':0x400081f6,'decode':0x4000818a},'runtime_slot':158,'serialized_slot':166,'runtime_bytes':164,'serialized_bytes':172,'integrated':False}
Path('work/os144/E08-PC-settings-codec-bridge-layout.json').write_text(json.dumps(c,indent=2));print('Native codec bridge',sum(r['bytes'] for r in regions),'bytes')
