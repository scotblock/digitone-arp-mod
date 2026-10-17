"""Execute corrected native owner selection with hostile lock-list pointers."""
from pathlib import Path
import json,struct,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from emu import cfisa
c=json.loads(Path('work/os144/PC_ONLY-E09-sequence-owner-helper.json').read_text())
code=Path('work/os144/PC_ONLY-E09-sequence-owner-helper.bin').read_bytes();base=c['region']['base']
m=Machine(ddr=0x8000000);u=m.uc
E=0x47bc8000;KIT=E+0x1000;STACK=E+0x7f00
for a in [base,E,KIT,STACK,0x419c5000]:m.ensure(a)
u.mem_write(base,code);m.install_isa_patches_scoped(code,base)
put=lambda a,v:u.mem_write(a,struct.pack('>I',v&0xffffffff))
checks=[]
for label,change,expected in [
 ('sequenced_lock_list_is_not_parameters',{},KIT+0x5ce),
 ('cached_lock_list_is_not_parameters',{'cache':0xdeadbeef},KIT+0x5ce),
 ('null_lock_list',{'locks':0},KIT+0x5ce),
 ('live_input_uses_same_consumed_pattern',{'mode':2,'gate':0},KIT+0x5ce),
 ('live_rejects_multiple_notes',{'mode':2,'count':3},0),
 ('sequence_accepts_chord',{'count':3},KIT+0x5ce),
 ('sequence_accepts_eight_notes',{'count':8},KIT+0x5ce),
 ('other_MIDI_track',{'track':1},0),
 ('release',{'onoff':2},0),
 ('not_selected',{'selected':0},0),
 ('empty_chord',{'count':0},0),
 ('too_many_notes',{'count':9},0),
 ('invalid_note',{'note':128},0),
 ('unknown_mode',{'mode':7},0),
 ('invalid_sequence_gate',{'gate':0},0),
 ('missing_consumed_pattern',{'kit':0},0),
 ('timer_is_not_source',{'kind':3},0),
]:
 v={'kind':0,'track':0,'onoff':1,'selected':1,'count':1,'note':60,'gate':2700000,'locks':0xdeadbeef,'cache':0xcafebabe,'mode':1,'kit':KIT};v.update(change)
 u.mem_write(E,bytes(52))
 for off,key in [(0,'kind'),(4,'track'),(8,'onoff'),(12,'selected'),(16,'count'),(28,'gate'),(40,'locks'),(44,'mode')]:put(E+off,v[key])
 u.mem_write(E+20,bytes([v['note']])*min(8,v['count']))
 put(0x419c5b10,v['kit']);put(0x419c5b14,v['cache'])
 actual=call(m,base,[E],stack_top=STACK,limit=10000)
 assert actual==expected,(label,hex(actual),hex(expected))
 checks.append(label)
offset=0
while offset<c['executed_bytes']:
 ins=cfisa.decode(lambda x:int.from_bytes(code[offset+x:offset+x+2],'big'),base+offset)
 assert ins.length and not ins.flags&(cfisa.FPU|cfisa.LINEF|cfisa.ILLEGAL),(offset,ins)
 offset+=ins.length
out={'passed':True,'PC_only':True,'cases':checks,'case_count':len(checks),'no_invalid_lock_pointer_dereference':True,
     'limits':['Isolated source-owner helper, not full sequencer or hardware coverage.']}
Path('outputs/Digitone-E09-PC-sequence-owner-contracts.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
