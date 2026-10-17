"""Native encoder/render prototype; temporary PC RAM, no packaged firmware."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
n=json.loads(Path('work/os144/E09A-PC-install-layout.json').read_text());core=json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text())
payload=Path('work/os144/E09A-PC-layout-payload.bin').read_bytes();X=core['state'];PB=n['base'];B=0x47be9400
TURN=B;DRAW=B+0x400;OLD_TURN=B+0x1400;OLD_DRAW=B+0x1800;EDIT=B+0x1c00;STR=B+0x2400;PUB=0x47be9200
old={name:next(r for r in n['regions'] if r['name']==name) for name in ['selected_track','M1_handle','M1_controls_turn','M1_controls_render']}
parts=[];regions=[]
def absop(a,op,v):absolute(a,op,v)
def js(a,v):absop(a,'4eb9',v)
def jump(a,v):absop(a,'4ef9',v)
def ui_save(a):save(a);a.code[-4:]=bytes.fromhex('4e714e71')
def add(name,base,a,limit):
 code=a.done();assert len(code)<=limit,(name,len(code),limit);parts.append((base,code));regions.append({'name':name,'base':base,'bytes':len(code)})
def guard(a):
 ui_save(a);a.emit('206f0044202802c80c804d314352');a.branch('6600','original')
 js(a,old['selected_track']['base']);a.emit('0c8000000004');a.branch('6600','original')

# ui_edit(owner,encoder,delta), using a staged 16-byte sequence on its stack.
a=Asm();save(a);a.emit('4fefffe0242f00642e2f0068202f006c4a80');a.branch('6700','deny')
a.emit('72014a80');a.branch('6a00','sign');a.emit('72ff');a.label('sign');a.emit('2f410010')
a.emit('0c8700000001');a.branch('6500','deny');a.emit('0c8700000008');a.branch('6200','deny')
a.emit('70ff2f400018');absop(a,'2039',X+28);a.emit('b082');a.branch('6600','defaults')
for op,off in [('2639',8),('2839',20),('2a39',24),('2c39',4)]:absop(a,op,X+off)
absop(a,'2039',X+16);a.emit('2f400014');absop(a,'41f9',X+32);a.emit('43d7720f')
a.label('stage');a.emit('101812c05381');a.branch('6a00','stage');a.branch('6000','choose')
a.label('defaults');a.emit('7610283c0000ffff2a3c800000807c00429742af000442af000842af000c42af0014')
a.label('choose');a.emit('222f0010')
for value,label in [(1,'root'),(2,'scale'),(3,'length'),(4,'page'),(5,'step'),(6,'offset'),(7,'rest')]:
 a.emit('0c87'+struct.pack('>I',value).hex());a.branch('6700',label)
a.emit('7c004a81');a.branch('6b00','publish');a.emit('7c01');a.branch('6000','publish')
a.label('root');a.emit('200502800000007fd081');a.branch('6a00','root_low');a.emit('7000');a.label('root_low');a.emit('0c800000000b');a.branch('6f00','root_high');a.emit('700b');a.label('root_high');a.emit('0285ffffff808a80');a.branch('6000','publish')
a.label('scale');a.emit('2005ee8802800000003fd081');a.branch('6a00','scale_low');a.emit('7000');a.label('scale_low');a.emit('0c8000000023');a.branch('6f00','scale_high');a.emit('7023');a.label('scale_high');a.emit('ef880285ffffe07f8a80');a.branch('6000','publish')
a.label('length');a.emit('d6810c8300000001');a.branch('6c00','length_low');a.emit('7601');a.label('length_low');a.emit('0c8300000010');a.branch('6f00','publish');a.emit('7610');a.branch('6000','publish')
a.label('page');a.emit('70004a81');a.branch('6b00','page_value');a.emit('7001');a.label('page_value');a.emit('2f400018');a.branch('6000','publish')
a.label('step');a.emit('202f0014d081');a.branch('6a00','step_low');a.emit('7000');a.label('step_low');a.emit('b083');a.branch('6d00','step_high');a.emit('20035380');a.label('step_high');a.emit('2f400014');a.branch('6000','publish')
a.label('offset');a.emit('202f001441d77e001e300800488748c7de810c87ffffffe8');a.branch('6c00','offset_low');a.emit('7ee8');a.label('offset_low');a.emit('0c8700000018');a.branch('6f00','offset_high');a.emit('7e18');a.label('offset_high');a.emit('11870800');a.branch('6000','publish')
a.label('rest');a.emit('202f00144a81');a.branch('6b00','unrest');a.emit('0184');a.branch('6000','publish');a.label('unrest');a.emit('01c4')
a.label('publish');a.emit('204f2f062f082f052f042f032f02');js(a,PUB);a.emit('4fef00184a80');a.branch('6700','deny')
a.emit('202f0014b083');a.branch('6d00','step_valid');a.emit('20035380');a.label('step_valid');absop(a,'23c0',X+16)
a.emit('202f00184a80');a.branch('6b00','success');absop(a,'23c0',X+56)
a.label('success');a.emit('7001');a.branch('6000','return')
a.label('deny');a.emit('7000');a.label('return');a.emit('2f4000204fef0020');restore(a);a.emit('4e75');add('M1_step_ui_edit',EDIT,a,0x800)

# Existing A/B/C main controls remain in their original corrected helper.
a=Asm();guard(a);a.emit('246f0048242a000c');absop(a,'4ab9',X+56);a.branch('6600','step_page');a.emit('0c8200000004');a.branch('6600','original')
a.label('step_page');a.emit('262a0010');js(a,old['M1_handle']['base']);a.emit('2040202800102f032f022f00');js(a,EDIT);a.emit('4fef000c2f2f0044');js(a,0x400e539e);a.emit('588f70012f400000');restore(a);a.emit('4e75')
a.label('original');restore(a);jump(a,OLD_TURN);add('M1_step_encoder_dispatch',TURN,a,0x300)

strings={};cursor=STR
for key,value in [('title','M1 ARP STEPS'),('root','A ROOT %s'),('scale','B %s'),('length','C LEN %02d'),('page','D <CTRL'),('step','E STEP %02d'),('offset','F OFS %+d'),('rest','G REST %s'),('enabled','H SEQ %s'),('on','ON'),('off','OFF')]:
 strings[key]=cursor;data=value.encode()+b'\0';parts.append((cursor,data));cursor+=len(data)
root_names=[]
for text in ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']:
 root_names.append(cursor);data=text.encode()+b'\0';parts.append((cursor,data));cursor+=len(data)
scales=json.loads(Path('outputs/Digitone-OS1.42-scale-map.json').read_text())['scales'];scale_names=[]
for row in scales:
 scale_names.append(cursor);data=row['short_name'][:4].encode()+b'\0';parts.append((cursor,data));cursor+=len(data)
cursor=(cursor+3)&~3;ROOTS=cursor;data=b''.join(struct.pack('>I',v) for v in root_names);parts.append((cursor,data));cursor+=len(data)
SCALES=cursor;data=b''.join(struct.pack('>I',v) for v in scale_names);parts.append((cursor,data));cursor+=len(data)

def draw(a,key,x,y,arg=None):
 if arg:a.emit(arg)
 absop(a,'4879',strings[key]);a.emit('487800024878'+struct.pack('>H',y).hex()+'4878'+struct.pack('>H',x).hex());absop(a,'4879',0x418e934c);a.emit('2f0c');js(a,0x400de120);a.emit('4fef'+('001c' if arg else '0018'))
a=Asm();guard(a);absop(a,'4ab9',X+56);a.branch('6700','original');a.emit('286f0048');draw(a,'title',64,58)
absop(a,'2039',X+24);a.emit('02800000007f');absop(a,'41f9',ROOTS);draw(a,'root',32,44,'2f300c00')
absop(a,'2039',X+24);a.emit('ee8802800000003f');absop(a,'41f9',SCALES);draw(a,'scale',96,44,'2f300c00')
draw(a,'length',32,32,'2f39'+struct.pack('>I',X+8).hex());draw(a,'page',96,32)
absop(a,'2039',X+16);a.emit('5280');draw(a,'step',32,20,'2f00')
absop(a,'2039',X+16);absop(a,'41f9',X+32);a.emit('720012300800488148c1');draw(a,'offset',96,20,'2f01')
absop(a,'2039',X+16);absop(a,'2239',X+20);a.emit('0101');a.branch('6600','not_rest');absop(a,'203c',strings['on']);a.branch('6000','rest_text');a.label('not_rest');absop(a,'203c',strings['off']);a.label('rest_text');draw(a,'rest',32,8,'2f00')
absop(a,'4ab9',X+4);a.branch('6700','seq_off');absop(a,'203c',strings['on']);a.branch('6000','seq_text');a.label('seq_off');absop(a,'203c',strings['off']);a.label('seq_text');draw(a,'enabled',96,8,'2f00');restore(a);a.emit('4e75')
a.label('original');restore(a);jump(a,OLD_DRAW);add('M1_step_render',DRAW,a,0x1000)
patches=[]
for name,target,clone in [('M1_controls_turn',TURN,OLD_TURN),('M1_controls_render',DRAW,OLD_DRAW)]:
 r=old[name];raw=payload[r['base']-PB:r['base']-PB+r['bytes']];parts.append((clone,raw));regions.append({'name':name+'_clone','base':clone,'bytes':len(raw)})
 patches.append({'site':r['base'],'before':raw[:6].hex(),'after':'4ef9'+struct.pack('>I',target).hex()})
blob=bytearray(cursor-B)
for address,data in parts:blob[address-B:address-B+len(data)]=data
assert max(r['base']+r['bytes'] for r in regions)<=STR
Path('work/os144/PC_ONLY-E10-step-editor.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-E10-step-editor.json').write_text(json.dumps({'PC_only':True,'base':B,'bytes':len(blob),'entries':{'turn':TURN,'render':DRAW,'edit':EDIT},'regions':regions,'patches':patches,'strings_base':STR,'strings_end':cursor,'controls':{'main_D':'Steps page','step_A':'Root','step_B':'Scale','step_C':'Length 1..16','step_D':'Return to main controls','step_E':'Selected step','step_F':'Scale-degree offset -24..24','step_G':'Rest on/off','step_H':'Sequence on/off'},'limits':['Native editor prototype in temporary PC RAM; no startup installation, project persistence or hardware-ready firmware.']},indent=2))
print('Native editor:',sum(r['bytes'] for r in regions),'code bytes;',cursor-STR,'string/table bytes')
