"""PC-only native editor-to-bank and consumed-pattern recall adapters."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text(encoding='utf-8').split('parts=[]')[0])
c=json.loads(Path('work/os144/PC_ONLY-E10-persistence-layout.json').read_text())
life=c['E10'];S=c['state'];X=life['state'];BANK=life['bank'];PM=c['persistence']['meta']
PB=c['base'];payload=Path('work/os144/PC_ONLY-E10-persistence-payload.bin').read_bytes()
B=0x47bf1400;RESOLVE=B;RECALL=B+0x300;PUB=B+0x900;EDIT=B+0xc00;DRAW=B+0xd00;SELECT=B+0xe00
PUBCLONE=B+0x1000;EDITCLONE=B+0x1400;DRAWCLONE=B+0x1800;SELECTCLONE=B+0x1e00;COMMIT=B+0x2000;META=B+0x2400
parts=[];regions=[];patches=[]
def op(a,o,v):absolute(a,o,v)
def js(a,v):op(a,'4eb9',v)
def add(name,p,a,limit):
 raw=a.done() if isinstance(a,Asm) else bytes(a)
 assert len(raw)<=limit,(name,len(raw),limit)
 parts.append((p,raw));regions.append(dict(name=name,base=p,bytes=len(raw)))
def finish(a):
 a.label('ok');a.emit('7001');a.branch('6000','return');a.label('deny');a.emit('7000')
 a.label('return');a.emit('2f400000');restore(a);a.emit('4e75')
def admitted(a):
 op(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','deny')
 op(a,'2039',X);a.emit('0c804d535131');a.branch('6600','deny')
def ui_owner(a,deny):
 op(a,'2079',0x419f0de0);a.emit('4a88');a.branch('6700',deny)
 a.emit('d1fc00000ff820100c8040193b90');a.branch('6600',deny);a.emit('20280010')

# resolve(owner) -> exact 0..127 kit-array slot, or -1. The project capture
# metadata supplies both the runtime project base and a replacement generation.
a=Asm();save(a);op(a,'2039',PM);a.emit('0c804d535031');a.branch('6600','bad')
op(a,'4ab9',PM+4);a.branch('6700','bad');op(a,'2039',PM+8)
a.emit('0c8040000000');a.branch('6500','bad');a.emit('0c8047494000');a.branch('6200','bad')
a.emit('068000b0946a242f004494800c820004c400');a.branch('6400','bad')
a.emit('7000');a.label('slot');a.emit('0c8200000988');a.branch('6500','remainder')
a.emit('0482000009885280');a.branch('6000','slot')
a.label('remainder');a.emit('4a82');a.branch('6600','bad');a.branch('6000','return')
a.label('bad');a.emit('70ff');a.label('return');a.emit('2f400000');restore(a);a.emit('4e75')
add('E10_resolve_project_pattern',RESOLVE,a,0x300)

# recall(owner, origin): origin 0 is after actual consumed-owner selection;
# origin 1 is the editor. A pending UI selection cannot replace playing state.
a=Asm();save(a);a.emit('262f0044282f00480c8400000001');a.branch('6200','deny');admitted(a)
a.emit('2f03');js(a,RESOLVE);a.emit('588f4a80');a.branch('6b00','deny');a.emit('2a00')
op(a,'2039',META);a.emit('0c804d534231');a.branch('6600','changed')
op(a,'2039',META+4);op(a,'b0b9',PM+12);a.branch('6600','changed')
op(a,'b6b9',META+12);a.branch('6600','changed');op(a,'b6b9',X+28);a.branch('6700','ok')
a.label('changed');a.emit('4a84');a.branch('6700','consumed')
ui_owner(a,'deny');a.emit('b083');a.branch('6600','deny')
for field in [8,16,280]:op(a,'4ab9',S+field);a.branch('6600','deny')
op(a,'2079',S+40);a.emit('4a88');a.branch('6700','choose');a.emit('20100c8000000001');a.branch('6600','choose')
op(a,'b6b9',S+336);a.branch('6600','deny');a.branch('6000','choose')
a.label('consumed');op(a,'b6b9',S+336);a.branch('6600','deny')
op(a,'4ab9',S+280);a.branch('6600','deny')
a.label('choose');op(a,'2e39',X+56);op(a,'45f9',BANK);a.emit('2005eb88d5c02f0a');js(a,life['entries']['validate']);a.emit('588f2c00')
# Fresh settings/cursors/counters, with magic last. Preserve the step-page view
# only if the UI still refers to the receiving owner.
op(a,'41f9',X);a.emit('7210');a.label('clear');a.emit('42985381');a.branch('6600','clear')
for off,v in [(8,16),(20,0xffff),(24,0x80000080)]:op(a,'203c',v);op(a,'23c0',X+off)
a.emit('4a86');a.branch('6700','blank')
a.emit('7000102a0005');op(a,'23c0',X+4);a.emit('7000102a0006');op(a,'23c0',X+8)
a.emit('7000302a000a');op(a,'23c0',X+20)
a.emit('7000102a0008ef887200122a00078081008080000000');op(a,'23c0',X+24)
a.emit('41ea000c');op(a,'43f9',X+32);a.emit('720f');a.label('copy');a.emit('101812c05381');a.branch('6a00','copy');a.branch('6000','bound')
a.label('blank');op(a,'52b9',META+28)
a.label('bound');op(a,'23c3',X+28);ui_owner(a,'view_done');a.emit('b083');a.branch('6600','view_done');op(a,'23c7',X+56)
a.label('view_done');op(a,'203c',0x4d535131);op(a,'23c0',X)
op(a,'2039',PM+12);op(a,'23c0',META+4);op(a,'23c5',META+8);op(a,'23c3',META+12);op(a,'52b9',META+16)
op(a,'203c',0x4d534231);op(a,'23c0',META);a.branch('6000','ok')
a.label('deny');op(a,'52b9',META+24);a.emit('4a84');a.branch('6600','refused')
op(a,'42b9',X+28);op(a,'42b9',META)
a.label('refused');a.emit('7000');a.branch('6000','return')
a.label('ok');a.emit('7001');a.label('return');a.emit('2f400000');restore(a);a.emit('4e75')
add('E10_recall_bound_pattern',RECALL,a,0x600)

# Publisher calls are one atomic recall -> original validation/publication ->
# validated snapshot commit. Editor cursor/page updates are not serialized.
a=Asm();save(a);a.emit('487800012f2f0048');js(a,RECALL);a.emit('508f4a80');a.branch('6700','deny')
for _ in range(6):a.emit('2f2f0058')
js(a,PUBCLONE);a.emit('4fef00184a80');a.branch('6700','deny')
a.emit('2f2f0044');op(a,'2f39',META+8);js(a,COMMIT);a.emit('508f4a80');a.branch('6600','committed')
op(a,'42b9',X+28);a.branch('6000','deny')
a.label('committed');op(a,'52b9',META+20);finish(a);add('E10_publish_and_save_pattern',PUB,a,0x300)

a=Asm();save(a);a.code[-4:]=bytes.fromhex('4e714e71');a.emit('487800012f2f0048');js(a,RECALL);a.emit('508f4a80');a.branch('6700','deny')
for _ in range(3):a.emit('2f2f004c')
js(a,EDITCLONE);a.emit('4fef000c2f4000004a80');a.branch('6700','return')
# Notify the same native parameter handle used by the existing M1 controls,
# outside the masked snapshot section. Cursor/page changes are not edits.
a.emit('202f00480c8000000004');a.branch('6700','return');a.emit('0c8000000005');a.branch('6700','return')
ui_owner(a,'return');a.emit('b0af0044');a.branch('6600','return');a.emit('42a72f08');js(a,0x4014eff8);a.emit('508f')
a.label('return');restore(a);a.emit('4e75')
a.label('deny');op(a,'42b9',X+56);a.emit('70002f400000');restore(a);a.emit('4e75');add('E10_pattern_editor_admission',EDIT,a,0x100)

# Keep expensive drawing outside the masked recall section.
a=Asm();save(a);a.code[-4:]=bytes.fromhex('4e714e71');op(a,'4ab9',X+56);a.branch('6700','draw')
ui_owner(a,'close');a.emit('487800012f00');js(a,RECALL);a.emit('508f4a80');a.branch('6600','draw')
a.label('close');op(a,'42b9',X+56)
a.label('draw');restore(a);op(a,'4ef9',DRAWCLONE);add('E10_pattern_render_admission',DRAW,a,0x100)

# This is the actual existing consumed-owner selector, not a panel request.
a=Asm();save(a);a.emit('2f2f0044');js(a,SELECTCLONE);a.emit('588f2f4000004a80');a.branch('6700','return')
a.emit('42a72f2f0048');js(a,RECALL);a.emit('508f')
a.label('return');restore(a);a.emit('4e75');add('E10_consumed_pattern_recall',SELECT,a,0x200)

for name,entry,clone,limit in [('E10_atomic_settings_publication',PUB,PUBCLONE,0x400),('M1_step_ui_edit',EDIT,EDITCLONE,0x400),('M1_step_render',DRAW,DRAWCLONE,0x600),('select_consumed_settings_owner',SELECT,SELECTCLONE,0x200)]:
 r=next(r for r in c['regions'] if r['name']==name);raw=payload[r['base']-PB:r['base']-PB+r['bytes']]
 add(name+'_binding_clone',clone,raw,limit)
 patches.append(dict(site=r['base'],length=6,before=raw[:6].hex(),after='4ef9'+struct.pack('>I',entry).hex()))

# Private snapshot variant: remove the four quiescence tests from the existing
# validated stack-record serializer. Only the owned publisher above calls it,
# with interrupts masked and all source fields validated. It touches no held
# notes, arena, transport or playback ownership; it merely snapshots settings.
lr=next(r for r in life['regions'] if r['name']=='E10_save_pattern_RAM')
raw=bytearray(payload[lr['base']-PB:lr['base']-PB+lr['bytes']])
for field in [8,12,16,280]:
 needle=bytes.fromhex('4ab9')+struct.pack('>I',S+field);assert raw.count(needle)==1
 off=raw.index(needle);assert raw[off+6:off+8]==bytes.fromhex('6600');raw[off:off+10]=bytes.fromhex('4e71')*5
add('E10_commit_validated_owned_snapshot',COMMIT,raw,0x400)
blob=bytearray(META+32-B)
for p,raw in parts:blob[p-B:p-B+len(raw)]=raw
Path('work/os144/PC_ONLY-E10-pattern-binding.bin').write_bytes(blob)
result=dict(PC_only=True,base=B,bytes=len(blob),regions=regions,patches=patches,meta=META,meta_bytes=32,entries=dict(resolve=RESOLVE,recall=RECALL,publish=PUB,edit=EDIT,render=DRAW,select=SELECT),clones=dict(publish=PUBCLONE,edit=EDITCLONE,render=DRAWCLONE,select=SELECTCLONE,commit=COMMIT),meta_fields=dict(magic=0,project_generation=4,slot=8,owner=12,recalls=16,edits=20,refusals=24,defaults=28),limits=['PC-only adapters. Physical storage/cache/timing and enlarged RAM ownership remain unverified.','Pattern identity is an exact kit-array slot within the project captured by the native decoder, plus its generation.','UI rebinding refuses active/held/arena or a different running consumer owner. Existing-owner edits use the original publisher checks.','Consumed recall requires the selected owner and no outstanding arena; refusal invalidates step ownership and retains the stock arp route.','Copy/clear/undo, incremental saves and asynchronous project replacement are not certified.'])
Path('work/os144/PC_ONLY-E10-pattern-binding.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('PC binding adapters:',sum(r['bytes'] for r in regions),'code bytes;',len(blob),'copied bytes')
