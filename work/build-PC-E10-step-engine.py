"""PC-only M1 16-step engine. No firmware images or stock settings changed."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
c=json.loads(Path('work/os144/E09A-PC-install-layout.json').read_text())
S=c['state'];A=c['arena'];PB=c['base'];B=0x47be8800;CLONE=B+0x300;CLEAR=B+0x400;CLEAR_CLONE=B+0x480;X=B+0x800
payload=Path('work/os144/E09A-PC-layout-payload.bin').read_bytes()
regions=[];parts=[]
def absop(a,op,v):absolute(a,op,v)
def js(a,v):absop(a,'4eb9',v)
def jump(a,v):absop(a,'4ef9',v)
def add(name,base,a,limit):
 code=a.done();assert len(code)<=limit,(name,len(code),limit);parts.append((base,code));regions.append({'name':name,'base':base,'bytes':len(code)})

# Called by the E09A dispatcher with A2=source, A3=M1 state, D7=now.
# It remains inside the original fully preserving IPL-masked consumer wrapper.
a=Asm();absop(a,'2039',X);a.emit('0c804d535131');a.branch('6600','ordinary')
absop(a,'4ab9',X+4);a.branch('6700','ordinary')
absop(a,'2039',X+28);a.emit('b0ab0150');a.branch('6600','ordinary')
absop(a,'2239',X+8);a.emit('0c8100000001');a.branch('6500','ordinary');a.emit('0c8100000010');a.branch('6200','ordinary')
absop(a,'2a39',X+12);a.emit('ba81');a.branch('6500','index_ok');a.emit('7a00')
a.label('index_ok');a.emit('20055280b081');a.branch('6500','cursor_ok');a.emit('7000')
a.label('cursor_ok');absop(a,'23c0',X+12)
# Every due step advances, including rests and pitches outside MIDI range.
absop(a,'2039',X+20);a.emit('0b00');a.branch('6700','rest')
a.emit('202b0014b0ab0010');a.branch('6500','chord_index');a.emit('7000')
a.label('chord_index');a.emit('24330c40');absop(a,'41f9',X);a.emit('760016305820488348c3')
# E06's actual helper: degree(fallback, context, selected_note, offset, octave).
a.emit('42a72f032f02');absop(a,'2f39',X+24);a.emit('2002d0832f00');js(a,0x47be0a00);a.emit('4fef001428004a84');a.branch('6b00','clipped');a.emit('0c840000007f');a.branch('6200','clipped')
# Raw emitter retains native descriptor ownership, gate and normal routing.
js(a,CLONE);absop(a,'41f9',A);a.emit('11440014');absop(a,'52b9',X+60);absop(a,'203c',A);a.emit('4e75')
a.label('rest');absop(a,'52b9',X+48);a.branch('6000','silent')
a.label('clipped');absop(a,'52b9',X+52)
a.label('silent');a.emit('202b0014b0ab0010');a.branch('6500','silent_index');a.emit('7000')
a.label('silent_index');a.emit('528027400014202b0020d1ab001827470120200a4e75')
a.label('ordinary');jump(a,CLONE);add('M1_step_emit',B,a,0x300)
old_emit=next(r for r in c['regions'] if r['name']=='emit_descriptor')
raw=payload[old_emit['base']-PB:old_emit['base']-PB+old_emit['bytes']]
parts.append((CLONE,raw));regions.append({'name':'M1_original_emit_clone','base':CLONE,'bytes':len(raw)})
old_clear=next(r for r in c['regions'] if r['name']=='clear_members')
raw=payload[old_clear['base']-PB:old_clear['base']-PB+old_clear['bytes']]
parts.append((CLEAR_CLONE,raw));regions.append({'name':'M1_original_clear_clone','base':CLEAR_CLONE,'bytes':len(raw)})
a=Asm();js(a,CLEAR_CLONE);absop(a,'42b9',X+12);a.emit('4e75');add('M1_step_clear',CLEAR,a,0x80)
patches=[]
for old,target in [(old_emit,B),(old_clear,CLEAR)]:
 before=payload[old['base']-PB:old['base']-PB+6]
 patches.append({'site':old['base'],'before':before.hex(),'after':'4ef9'+struct.pack('>I',target).hex()})
blob=bytearray(X+64-B)
for address,code in parts:blob[address-B:address-B+len(code)]=code
seed=bytearray(64)
for off,value in [(0,0x4d535131),(4,0),(8,16),(20,0xffff),(24,0x80000080)]:struct.pack_into('>I',seed,off,value)
blob[X-B:X-B+64]=seed
out={'PC_only':True,'firmware_container_created':False,'base':B,'bytes':len(blob),'state':X,'state_bytes':64,
     'entries':{'emit':B,'raw_emit':CLONE,'clear':CLEAR},'regions':regions,'patches':patches,
     'state_fields':{'magic':0,'enabled':4,'length':8,'play_cursor':12,'edit_cursor':16,'enabled_step_mask':20,'root_scale_word':24,'owner':28,'signed_offsets':32,'rest_count':48,'clipped_count':52,'reserved':56,'emitted_count':60},
     'initialization':'Explicit PC host fixture; disabled, length 16, offsets zero, all steps enabled, C Ionian context. No native startup integration.',
     'limits':['Temporary PC RAM overlay only. Physical ownership, startup/copy/reset, device controls and saved settings not integrated.',
               'Owner is an explicit PC fixture matched against E09A consumed owner; pointer reuse/lifetime not certified.',
               'Root/scale is an explicit prototype configuration; native MIDI keyboard scale capture is not claimed.']}
Path('work/os144/PC_ONLY-E10-step-engine.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-E10-step-engine.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'code_bytes':sum(r['bytes'] for r in regions),'state_bytes':64,'overlay_bytes':len(blob)},indent=2))
