"""E11 PC-only synth-style M1 step editor; retain E10 playback/storage APIs."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text(encoding='utf-8').split('parts=[]')[0])
c=json.loads(Path('work/os144/PC_ONLY-E10-package-layout.json').read_text(encoding='utf-8'));payload=Path('work/os144/PC_ONLY-E10-package-payload.bin').read_bytes();PB=c['base'];X=c['E10']['state']
B=0x47bf6400;TURN=B;KEY=B+0x300;DRAW=B+0x600;STR=B+0xe00;TC=B+0x1400;KC=B+0x1700;DC=B+0x1900
entry=lambda name:next(r for r in c['regions'] if r['name']==name)
SEL=entry('selected_track')['base'];HANDLE=entry('M1_handle')['base'];EDIT=entry('M1_step_ui_edit')['base']
oldturn=entry('M1_step_encoder_dispatch');oldkey=entry('M1_controls_key');olddraw=entry('M1_step_render_binding_clone')
parts=[];regions=[];patches=[]
def op(a,o,v):absolute(a,o,v)
def js(a,v):op(a,'4eb9',v)
def jump(a,v):op(a,'4ef9',v)
def ui_save(a):save(a);a.code[-4:]=bytes.fromhex('4e714e71')
def add(name,base,a,limit):
 code=a.done() if isinstance(a,Asm) else bytes(a);assert len(code)<=limit,(name,len(code),limit);parts.append((base,code));regions.append(dict(name=name,base=base,bytes=len(code)))
def guard(a):
 ui_save(a);a.emit('206f0044202802c80c804d314352');a.branch('6600','original');js(a,SEL);a.emit('0c8000000004');a.branch('6600','original');op(a,'4ab9',X+56);a.branch('6700','original')
def dispatch_edit(a):
 js(a,HANDLE);a.emit('2040202800102f032f022f00');js(a,EDIT);a.emit('4fef000c2f2f0044');js(a,0x400e539e);a.emit('588f')
def handled(a):a.emit('70012f400000');restore(a);a.emit('4e75')
a=Asm();guard(a);a.emit('246f0048242a000c262a00100c8200000005');a.branch('6600','length');a.emit('7406');a.branch('6000','edit');a.label('length');a.emit('0c8200000006');a.branch('6600','unused');a.emit('7403');a.branch('6000','edit');a.label('unused');a.emit('0c8200000003');a.branch('6700','done');a.label('edit');dispatch_edit(a);a.label('done');handled(a);a.label('original');restore(a);jump(a,TC);add('M1_synth_style_encoder',TURN,a,0x300)
# Firmware event IDs are the observed Digitone logical button codes, not panel wire channels.
a=Asm();guard(a);a.emit('206f00482428000c');a.emit('0c820000000f');a.branch('6500','original');a.emit('0c8200000012');a.branch('6200','original');a.emit('2228001008010000');a.branch('6700','done')
a.emit('0c8200000011');a.branch('6700','left');a.emit('0c8200000012');a.branch('6700','right');a.emit('0c820000000f');a.branch('6700','up');a.emit('74077601');a.branch('6000','edit')
a.label('up');a.emit('740776ff');a.branch('6000','edit');a.label('left');a.emit('740576ff');a.branch('6000','edit');a.label('right');a.emit('74057601');a.label('edit');dispatch_edit(a);a.label('done');handled(a);a.label('original');restore(a);jump(a,KC);add('M1_synth_style_arrows',KEY,a,0x300)
strings={};cursor=STR
for key,text in [('title','M1 ARP STEPS'),('root','A ROOT %s'),('scale','B %s'),('offset','E OFS %+d'),('length','F LEN %02d'),('grid','%s'),('help','<>STEP ^vREST'),('seq','H %s'),('on','ON'),('off','OFF')]:
 strings[key]=cursor;raw=text.encode()+b'\0';parts.append((cursor,raw));cursor+=len(raw)
roots=[];scales=[]
for text in ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']:
 roots.append(cursor);raw=text.encode()+b'\0';parts.append((cursor,raw));cursor+=len(raw)
for row in json.loads(Path('outputs/Digitone-OS1.42-scale-map.json').read_text(encoding='utf-8'))['scales']:
 scales.append(cursor);raw=row['short_name'][:4].encode()+b'\0';parts.append((cursor,raw));cursor+=len(raw)
cursor=(cursor+3)&~3;ROOTS=cursor;raw=b''.join(struct.pack('>I',v) for v in roots);parts.append((cursor,raw));cursor+=len(raw);SCALES=cursor;raw=b''.join(struct.pack('>I',v) for v in scales);parts.append((cursor,raw));cursor+=len(raw)
def draw(a,key,x,y,arg=None):
 if arg:a.emit(arg)
 op(a,'4879',strings[key]);a.emit('487800024878'+struct.pack('>H',y).hex()+'4878'+struct.pack('>H',x).hex());op(a,'4879',0x418e934c);a.emit('2f0c');js(a,0x400de120);a.emit('4fef'+('001c' if arg else '0018'))
a=Asm();guard(a);a.emit('286f0048');draw(a,'title',64,58)
op(a,'2039',X+24);a.emit('02800000007f');op(a,'41f9',ROOTS);draw(a,'root',32,44,'2f300c00');op(a,'2039',X+24);a.emit('ee8802800000003f');op(a,'41f9',SCALES);draw(a,'scale',96,44,'2f300c00')
op(a,'2039',X+16);op(a,'41f9',X+32);a.emit('720012300800488148c1');draw(a,'offset',32,32,'2f01');draw(a,'length',96,32,'2f39'+struct.pack('>I',X+8).hex())
a.emit('4fefffe041d77400');op(a,'2639',X+8);op(a,'2839',X+20);op(a,'2a39',X+16)
a.label('cell');a.emit('7c2eb483');a.branch('6400','store');a.emit('7c2b0504');a.branch('6600','enabled');a.emit('7c2d');a.label('enabled');a.emit('b485');a.branch('6600','store');a.emit('7c580504');a.branch('6600','store');a.emit('7c2a');a.label('store');a.emit('10c652820c8200000010');a.branch('6500','cell');a.emit('4210204f');draw(a,'grid',64,17,'2f08');a.emit('4fef0020');draw(a,'help',44,3)
op(a,'4ab9',X+4);a.branch('6700','off');op(a,'203c',strings['on']);a.branch('6000','seq');a.label('off');op(a,'203c',strings['off']);a.label('seq');draw(a,'seq',110,3,'2f00');restore(a);a.emit('4e75');a.label('original');restore(a);jump(a,DC);add('M1_synth_style_grid',DRAW,a,0x800)
for old,target,clone,limit in [(oldturn,TURN,TC,0x300),(oldkey,KEY,KC,0x200),(olddraw,DRAW,DC,0x600)]:
 raw=payload[old['base']-PB:old['base']-PB+old['bytes']];add(old['name']+'_E11_fallback',clone,raw,limit);patches.append(dict(site=old['base'],before=raw[:6].hex(),after='4ef9'+struct.pack('>I',target).hex()))
end=max(p+len(raw) for p,raw in parts);assert end<0x47c00000 and B>=PB+len(payload)
blob=bytearray(end-B)
for p,raw in parts:blob[p-B:p-B+len(raw)]=raw
Path('work/os144/PC_ONLY-E11-synth-style-editor.bin').write_bytes(blob)
result=dict(PC_only=True,base=B,bytes=len(blob),regions=regions,patches=patches,entries=dict(turn=TURN,key=KEY,render=DRAW),additional_RAM_state_bytes=0,E10_storage_format_unchanged=True,controls={'LEFT_RIGHT':'Select step','E':'Scale-degree offset','F':'Length 1..16','UP':'Enable selected step','DOWN':'Rest selected step','A_B':'Explicit root/scale retained','D':'Back to main arp controls','H':'Step sequence on/off','C':'Unused on step page','G':'Legacy rest encoder retained'},limits=['Host-installed PC overlay only; startup copying/cache handoff and hardware not tested.','M1 only. Main arp UP mode/rate/gate and E10 persistence/ownership APIs retained; no new synth arp modes or range engine.','Grid uses + enabled, - rest, X selected enabled, * selected rest, . outside length. This is not pixel-identical stock artwork.'])
Path('work/os144/PC_ONLY-E11-synth-style-editor.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('E11 PC editor:',len(blob),'bytes;',sum(r['bytes'] for r in regions),'code bytes; no new state or firmware.')
