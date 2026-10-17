"""Native editor value changes through the atomic publication API."""
from pathlib import Path
import json
prefix=Path('work/test-PC-E10-step-publication.py').read_text().split('checks=[]\nargs=reset();')[0]
exec(compile(prefix,'E10-editor-native-fixtures','exec'))
editor=json.loads(Path('work/os144/PC_ONLY-E10-step-editor.json').read_text());ui_blob=Path('work/os144/PC_ONLY-E10-step-editor.bin').read_bytes()
for p in range(editor['base'],editor['base']+len(ui_blob),4096):m.ensure(p)
u.mem_write(editor['base'],ui_blob)
for r in editor['regions']:
 code=ui_blob[r['base']-editor['base']:r['base']-editor['base']+r['bytes']];offset=0
 while offset<len(code):
  ins=cfisa.decode(lambda x:int.from_bytes(code[offset+x:offset+x+2],'big'),r['base']+offset)
  assert ins.length and not ins.flags&(cfisa.FPU|cfisa.LINEF|cfisa.ILLEGAL) and not audit['move_restriction'](int.from_bytes(code[offset:offset+2],'big')),(r['name'],offset,ins)
  offset+=ins.length
 m.install_isa_patches_scoped(code,r['base'])
edit=lambda encoder,delta,owner=DATA:invoke(editor['entries']['edit'],[owner,encoder,delta&0xffffffff])
checks=[];reset();before=bytes(u.mem_read(KIT,0x1000))
assert edit(4,16)==1 and get(X+56)==1 and get(X+28)==DATA
assert [get(X+x) for x in [4,8,20,24]]==[0,16,0xffff,0x80000080]
checks.append('D opens the step page and binds a disabled, blank 16-step sequence to the current M1 settings owner.')
assert edit(1,16)==1 and get(X+24)==0x80000081
assert edit(1,-16)==1 and get(X+24)==0x80000080
assert edit(2,16)==1 and get(X+24)==0x80000100
assert edit(2,-16)==1 and get(X+24)==0x80000080
checks.append('A/B independently edit root and selected scale, in both directions.')
assert edit(3,-16)==1 and get(X+8)==15
assert edit(5,16)==1 and get(X+16)==1
assert edit(6,-16)==1 and u.mem_read(X+33,1)[0]==255
assert edit(7,16)==1 and get(X+20)==0xfffd
assert edit(7,-16)==1 and get(X+20)==0xffff
assert edit(8,16)==1 and get(X+4)==1
assert edit(8,-16)==1 and get(X+4)==0
checks.append('C/E/F/G/H edit length, step, signed scale offset, rest and sequence enable without using CC fields.')
for _ in range(30):assert edit(6,-16)==1
assert u.mem_read(X+33,1)[0]==(-24&255)
for _ in range(60):assert edit(6,16)==1
assert u.mem_read(X+33,1)[0]==24
for _ in range(20):assert edit(3,-16)==1
assert get(X+8)==1 and get(X+16)==0
checks.append('Offset and length limits clamp correctly; shortening length clamps the selected step.')
assert edit(4,-16)==1 and get(X+56)==0
checks.append('D returns to the existing main controls.')
put(S+8,1);put(S+336,DATA+0xa4);put(X+28,DATA+0xa4)
saved=bytes(u.mem_read(X,64));assert edit(4,16)==0 and bytes(u.mem_read(X,64))==saved
checks.append('A different active playback owner refuses the complete edit, including page/binding changes.')
assert bytes(u.mem_read(KIT,0x1000))==before
checks.append('Stock MIDI/CC parameter storage remains byte-for-byte unchanged.')
out={'passed':True,'PC_only':True,'strict_ColdFire_regions_checked':True,'checks':checks,'groups':len(checks),'controls':editor['controls'],
     'limits':['Isolated native editor API calls, not native panel-event/render coverage. Startup/storage/persistence/hardware integration remains unfinished.']}
Path('outputs/Digitone-E10-PC-step-editor.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
