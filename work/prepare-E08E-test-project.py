"""Prepare a valid native project image and native-encoded MIDI records."""
from pathlib import Path
import json,sys,zlib,struct,hashlib
sys.path[:0]=['work/upstream/digiemu','work/emulator-deps']
from emu.snapshot import _load_blob

p=Path('work/os144/PC_ONLY-saved-mirror-valid_first.img')
with p.open('rb') as f:f.seek(0xf400000+0x110);image=f.read(0x2a7404)
assert len(image)==0x2a7404 and image[:8]==bytes.fromhex('beefbace0000000e') and image[-4:]==bytes.fromhex('bacef00c')
Path('work/os144/E08E-project-native-seed.bin').write_bytes(image)
b=_load_blob('work/os144/E08E-handoff-ready.snap');page=zlib.decompress(b['pages'][0x41300000]);runtime=bytearray(page[0x6862:0x6862+164])
assert runtime[0x22]==0 and int.from_bytes(runtime[160:164],'big')&1

# The actual stock serializer plus already-tested extension bridge encodes the
# records. This avoids inventing a mapping for stock MIDI preset fields.
ns={};exec(Path('work/test-E08-settings-codec-bridge.py').read_text().split('\nraw=bytearray')[0],ns)
u=ns['u'];R=ns['R'];F=ns['F'];BACK=ns['BACK'];invoke=ns['invoke'];c=ns['c']
rows=[]
matrix=[('01 OFF CHORD',0,2,50,'chord'),('02 UP MEDIUM',1,2,50,'chord'),
 ('03 UP SLOW',1,1,50,'chord'),('04 UP FAST',1,3,50,'chord'),
 ('05 SHORT GATE',1,2,10,'chord'),('06 LONG GATE',1,2,90,'chord'),
 ('07 EIGHT NOTES',1,2,50,'eight'),('08 WIDE CHORD',1,2,50,'wide'),
 ('09 RETRIGGER',1,2,50,'retrigger'),('10 LIVE INPUT',1,2,50,'live'),
 ('11 HANDOFF SLOW',1,1,20,'chord'),('12 HANDOFF FAST',1,3,80,'chord'),
 ('13 M2 BYPASS',0,2,50,'m2'),('14 SYNTH CHECK',0,2,50,'synth'),
 ('15 SYNTH AND M1',1,2,50,'both'),('16 BLANK OFF',0,2,50,'blank')]
for slot,(name,mode,rate,gate,kind) in enumerate(matrix):
    raw=bytearray(runtime);raw[0x22]=8 # native cached getter: zero-based output channel
    word=0xa800|(mode<<10)|(rate<<7)|gate;raw[158:160]=struct.pack('>H',word)
    u.mem_write(R,bytes(raw));u.mem_write(F,bytes(172))
    assert invoke(c['entries']['encode'],[F,R,0])==1
    encoded=bytes(u.mem_read(F,172));assert encoded[166:168]==struct.pack('>H',word)
    u.mem_write(BACK,bytes(164));assert invoke(c['entries']['decode'],[BACK,F,0])==1
    restored=bytes(u.mem_read(BACK,164));assert restored[0x22]==8 and restored[158:160]==raw[158:160] and int.from_bytes(restored[160:164],'big')&1
    rows.append({'slot':slot,'pattern':f'A{slot+1:02}','name':name,'mode':mode,'rate_index':rate,'gate':gate,'kind':kind,'word':word,'midi_record':encoded.hex()})
raw=bytearray(runtime);raw[0x22]=9;raw[158:160]=struct.pack('>H',0xa932)
u.mem_write(R,bytes(raw));assert invoke(c['entries']['encode'],[F,R,0])==1
Path('work/os144/E08E-test-project-spec.json').write_text(json.dumps({'name':'E08E ARP TESTS','rows':rows,'M2_record':bytes(u.mem_read(F,172)).hex(),'M1_channel':9,'M2_channel':10,'tempo':120},indent=2))
print('Native seed',len(image),'bytes; 16 MIDI configurations passed native encode/decode.')
