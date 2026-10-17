"""PC-only pattern clipboard/undo and retained working-image synchronization."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text(encoding='utf-8').split('parts=[]')[0])
c=json.loads(Path('work/os144/PC_ONLY-E10-bound-layout.json').read_text());PB=c['base'];S=c['state'];X=c['E10']['state'];BANK=c['E10']['bank'];BM=c['binding']['meta'];PM=c['persistence']['meta']
payload=Path('work/os144/PC_ONLY-E10-bound-payload.bin').read_bytes();stock=Path('work/os144/section-3.bin').read_bytes();MB=0x40000400
B=0x47bf4000;SYNC=B;CAP=B+0x400;EMIT=B+0x600;EDIT=B+0x800;KIT=B+0xa00;TRAMP=B+0xc00;COPY=B+0xe00
CAPCLONE=B+0x1000;EMITCLONE=B+0x1400;EDITCLONE=B+0x1800;Z=B+0x2000;CLIPS=Z+0x40
RESOLVE=c['binding']['entries']['resolve'];RECALL=c['binding']['entries']['recall'];VALID=c['E10']['entries']['validate'];NATIVE_COPY=0x400fbad8
MIRROR=0x40555ff4;FIELD=MIRROR+0x240200+0x940
parts=[];regions=[];patches=[];main_hooks=[]
def op(a,o,v):absolute(a,o,v)
def js(a,v):op(a,'4eb9',v)
def add(name,p,a,limit):
 raw=a.done() if isinstance(a,Asm) else bytes(a);assert len(raw)<=limit,(name,len(raw),limit)
 parts.append((p,raw));regions.append(dict(name=name,base=p,bytes=len(raw)))
def field_address(a):
 # D4 is the checked slot. A2 receives the 32-byte serialized extension.
 op(a,'45f9',FIELD);a.emit('20044a80');a.branch('6700','field_done')
 a.label('field_loop');a.emit('d5fc00000a005380');a.branch('6600','field_loop');a.label('field_done')
def mirror_bind(a):
 op(a,'2039',PM+8);a.emit('0c80407fd3f8');a.branch('6600','done')
 op(a,'23c0',Z+8);op(a,'2039',PM+12);op(a,'23c0',Z+4);op(a,'203c',0x4d434831);op(a,'23c0',Z)
def end_void(a):restore(a);a.emit('4e75')

# sync(slot): only the known active project/mirror pairing and generation may
# update COKI. The stock helper invalidates/rechecksums/publishes its header.
a=Asm();save(a);a.emit('4fefffe0282f00640c840000007f');a.branch('6200','deny')
op(a,'2039',Z);a.emit('0c804d434831');a.branch('6600','deny')
op(a,'4ab9',PM+4);a.branch('6700','deny');op(a,'2039',PM+8);a.emit('0c80407fd3f8');a.branch('6600','deny');op(a,'b0b9',Z+8);a.branch('6600','deny')
op(a,'2039',PM+12);op(a,'b0b9',Z+4);a.branch('6600','deny')
op(a,'2039',0x40555ee4);a.emit('0c80434f4b49');a.branch('6600','deny')
op(a,'2039',MIRROR);a.emit('0c80beefbace');a.branch('6600','deny');op(a,'2039',MIRROR+4);a.emit('0c800000000e');a.branch('6600','deny')
op(a,'2039',0x40555ef0);a.emit('0c8000000058');a.branch('6600','deny')
a.emit('487940555ee4');js(a,0x40085138);a.emit('588f');op(a,'b0b9',0x40555ee8);a.branch('6600','deny')
op(a,'47f9',BANK);a.emit('2004eb88d7c02f0b');js(a,VALID);a.emit('588f4a80');a.branch('6600','source_ready')
a.emit('204f7207');a.label('zero');a.emit('42985381');a.branch('6a00','zero');a.emit('264f')
a.label('source_ready');field_address(a);a.emit('487800202f0b2f0a');js(a,0x400852b4);a.emit('4fef000c');op(a,'52b9',Z+12);a.emit('7001');a.branch('6000','return')
a.label('deny');op(a,'52b9',Z+16);a.emit('7000')
a.label('return');a.emit('2f4000204fef0020');end_void(a);add('E10_sync_retained_pattern',SYNC,a,0x400)

# Captures revoke the previous mirror binding before admitting another project.
a=Asm();save(a);op(a,'42b9',Z);a.emit('2f2f00482f2f0048');js(a,CAPCLONE);a.emit('508f2f4000004a80');a.branch('6700','done')
a.emit('202f00440c8040555ff4');a.branch('6600','done');mirror_bind(a)
a.label('done');end_void(a);add('E10_capture_mirror_generation',CAP,a,0x200)

# Only a matching full encode into the fixed retained image establishes its
# new generation. Exports elsewhere leave the active binding intact.
a=Asm();save(a);a.emit('2f2f00482f2f0048');js(a,EMITCLONE);a.emit('508f2f400000242f00440c8240555ff4');a.branch('6600','done')
op(a,'42b9',Z);a.emit('4a80');a.branch('6700','done');mirror_bind(a)
a.label('done');end_void(a);add('E10_emit_mirror_generation',EMIT,a,0x200)

# Run original editor admission/publication/notification first. Synchronize
# after that notification so its native parameter updates cannot undo the edit.
a=Asm();save(a);a.code[-4:]=bytes.fromhex('4e714e71')
for _ in range(3):a.emit('2f2f004c')
js(a,EDITCLONE);a.emit('4fef000c2f40000046fc27004a80');a.branch('6700','done')
a.emit('2f2f0044');js(a,RESOLVE);a.emit('588f4a80');a.branch('6b00','done');a.emit('2f00');js(a,SYNC);a.emit('588f')
a.label('done');end_void(a);add('E10_edit_retained_sync',EDIT,a,0x200)

# Native incremental kit writes only: exact active-project source and exact
# retained-image destination. Arbitrary caller buffers receive no extra writes.
a=Asm()
for _ in range(3):a.emit('2f2f000c')
js(a,TRAMP);a.emit('4fef000c');save(a);a.emit('0c8000000001');a.branch('6600','done')
a.emit('202f00480680000005ce2f00');js(a,RESOLVE);a.emit('588f4a80');a.branch('6b00','done');a.emit('2800')
field_address(a);a.emit('200a048000000940b0af0044');a.branch('6600','done');a.emit('2f04');js(a,SYNC);a.emit('588f')
a.label('done');end_void(a);add('E10_incremental_kit_retained_sync',KIT,a,0x200)
head=stock[0x400095f4-MB:0x400095fc-MB];assert head.hex()=='4fefffe448d73c1c'
add('E10_stock_kit_encoder_trampoline',TRAMP,head+bytes.fromhex('4ef9')+struct.pack('>I',0x400095fc),0x200)
main_hooks.append(dict(site=0x400095f4,length=8,before=head.hex(),after='4ef9'+struct.pack('>I',KIT).hex()+'4e71'))

# Four verified native function-pointer loads use this wrapper. All ordinary
# memcpy operations run unchanged; only the five observed 0x988 kit calls are
# sidecar producers/consumers. Clip/undo records are project-generation scoped.
a=Asm()
for _ in range(3):a.emit('2f2f000c')
js(a,NATIVE_COPY);a.emit('4fef000c');save(a);a.emit('242f004c0c8200000988');a.branch('6600','done')
a.emit('282f0040')
for caller,index in [(0x400288dc,0),(0x400280ea,1),(0x40028764,2)]:
 a.emit('0c84'+struct.pack('>I',caller).hex());a.branch('6600','next_'+str(index));op(a,'49f9',CLIPS+48*index);a.branch('6000','capture')
 a.label('next_'+str(index))
for caller in [0x4002815a,0x400282ce]:
 a.emit('0c84'+struct.pack('>I',caller).hex());a.branch('6700','paste')
a.branch('6000','done')
a.label('capture');a.emit('42ac0008242f0044262f004820030680000005ce2f00');js(a,RESOLVE);a.emit('588f4a80');a.branch('6b00','done')
a.emit('eb88');op(a,'41f9',BANK);a.emit('d1c043ec000c7207');a.label('capture_record');a.emit('201822c05381');a.branch('6a00','capture_record')
a.emit('2882');op(a,'2039',PM+12);a.emit('29400004700129400008');op(a,'52b9',Z+24);a.branch('6000','done')
a.label('paste');a.emit('242f0044262f004820020680000005ce2f00');js(a,RESOLVE);a.emit('588f4a80');a.branch('6b00','done');a.emit('2800eb88');op(a,'45f9',BANK);a.emit('d5c0')
op(a,'49f9',CLIPS);a.emit('7a02')
a.label('find');a.emit('4aac0008');a.branch('6700','next_clip');a.emit('b694');a.branch('6600','next_clip');op(a,'2039',PM+12);a.emit('b0ac0004');a.branch('6700','found')
a.label('next_clip');a.emit('49ec00305385');a.branch('6a00','find')
# Missing/legacy/stale clipboard data yields absent/disabled steps, never a
# leftover destination program. This is deliberately not cross-project paste.
a.emit('204a7207');a.label('absent');a.emit('42985381');a.branch('6a00','absent');op(a,'52b9',Z+20);a.branch('6000','updated')
a.label('found');a.emit('41ec000c224a7207');a.label('restore_record');a.emit('201822c05381');a.branch('6a00','restore_record')
a.label('updated');op(a,'52b9',Z+28);a.emit('2f04');js(a,SYNC);a.emit('588f20020680000005ce');op(a,'b0b9',X+28);a.branch('6600','done')
op(a,'42b9',BM);op(a,'42b9',X+28);a.emit('42a72f00');js(a,RECALL);a.emit('508f')
a.label('done');end_void(a);add('E10_native_pattern_clipboard_bridge',COPY,a,0x1000)
for site in [0x400280c0,0x4002827a,0x40028732,0x400288b0]:
 before=stock[site-MB:site-MB+6];assert before[2:]==struct.pack('>I',NATIVE_COPY)
 main_hooks.append(dict(site=site,length=6,before=before.hex(),after=before[:2].hex()+struct.pack('>I',COPY).hex()))

for name,entry,clone,limit in [('E10_capture_project_records',CAP,CAPCLONE,0x400),('E10_emit_project_records',EMIT,EMITCLONE,0x400),('E10_pattern_editor_admission',EDIT,EDITCLONE,0x400)]:
 r=next(r for r in c['regions'] if r['name']==name);raw=payload[r['base']-PB:r['base']-PB+r['bytes']];add(name+'_lifecycle_clone',clone,raw,limit)
 patches.append(dict(site=r['base'],length=6,before=raw[:6].hex(),after='4ef9'+struct.pack('>I',entry).hex()))
blob=bytearray(CLIPS+3*48-B)
for p,raw in parts:blob[p-B:p-B+len(raw)]=raw
out=dict(PC_only=True,base=B,bytes=len(blob),regions=regions,patches=patches,main_hooks=main_hooks,meta=Z,meta_bytes=len(blob)-(Z-B),clips=CLIPS,entries=dict(sync=SYNC,capture=CAP,emit=EMIT,edit=EDIT,kit=KIT,copy=COPY),clones=dict(capture=CAPCLONE,emit=EMITCLONE,edit=EDITCLONE),known_project_owner=0x407fd3f8,mirror=MIRROR,limits=['PC-only. No hardware timing, cache coherence, automatic power-fail dispatch or complete RAM ownership certification.','Clipboard and undo extension records are generation-scoped; unknown/stale/cross-project kit sources restore absent disabled steps.','Pattern clear follows stock MIDI-setting semantics: it clears trigs while retaining arp settings.','Only the verified native pattern clipboard handlers and native incremental retained-kit serializer are adapted; other copy/reset/bypass families remain unproven.'])
Path('work/os144/PC_ONLY-E10-lifecycle.bin').write_bytes(blob);Path('work/os144/PC_ONLY-E10-lifecycle.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Lifecycle native code',sum(r['bytes'] for r in regions),'bytes; overlay',len(blob))
