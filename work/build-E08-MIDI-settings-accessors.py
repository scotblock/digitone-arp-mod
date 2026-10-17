"""Isolated PC native accessors. Proposed padding use is not integrated."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
B=0x47be5800;W=B+0x100;VT=0x40193b90;DEFAULT=0xa932
def finish(a):a.emit('2f400000');restore(a);a.emit('4e75');return a.done()
a=Asm();save(a);a.emit('206f00444a88');a.branch('6700','bad');a.emit('20100c8040193b90');a.branch('6600','bad');a.emit('226800104a89');a.branch('6700','bad');a.emit('70003029009e240002820000f8000c820000a800');a.branch('6600','default');a.emit('220002810000007f0c8100000001');a.branch('6500','default');a.emit('0c8100000063');a.branch('6200','default');a.branch('6000','end');a.label('default');a.emit('203c0000a932');a.branch('6000','end');a.label('bad');a.emit('7000');a.label('end');read=finish(a)
a=Asm();save(a);a.emit('206f00444a88');a.branch('6700','bad');a.emit('20100c8040193b90');a.branch('6600','bad');a.emit('226800104a89');a.branch('6700','bad');a.emit('202f00480c8000000001');a.branch('6200','bad');a.emit('222f004c0c8100000007');a.branch('6200','bad');a.emit('242f00500c8200000001');a.branch('6500','bad');a.emit('0c8200000063');a.branch('6200','bad');a.emit('e188e588ef89');a.emit('8081808200800000a8003340009e7001');a.branch('6000','end');a.label('bad');a.emit('7000');a.label('end');write=finish(a)
assert len(read)<=256 and len(write)<=256
blob=bytearray(512);blob[:len(read)]=read;blob[256:256+len(write)]=write
Path('work/os144/E08-PC-settings-accessors.bin').write_bytes(blob)
cfg={'PC_only':True,'base':B,'bytes':512,'entries':{'read':B,'write':W},'regions':[{'name':'read_MIDI_settings','base':B,'bytes':len(read)},{'name':'write_MIDI_settings','base':W,'bytes':len(write)}],'MIDI_vtable':VT,'proposed_record_offset':0x9e,'encoding':{'marker_mask':0xf800,'marker':0xa800,'mode_shift':10,'rate_shift':7,'gate_mask':127,'default_word':DEFAULT},'integrated':False,'limits':['The 0x9e word is a candidate padding location, not certified owned storage.','These isolated accessors do not mark a project dirty or provide device controls or save persistence.']}
Path('work/os144/E08-PC-settings-accessors-layout.json').write_text(json.dumps(cfg,indent=2));print('Native accessor bytes',len(read)+len(write))
