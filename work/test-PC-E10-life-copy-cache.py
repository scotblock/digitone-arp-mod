"""Native panel clipboard/undo/clear and an unsaved retained edit, PC only."""
from pathlib import Path
import json
def adapt_fixture(s):
 anchor="exec(compile(definitions,'E10-bound-handoff-definitions','exec'))"
 changes=[('PC_ONLY-E10-bound','PC_ONLY-E10-life'),('Digitone-E10-PC-bound-startup.json','Digitone-E10-PC-life-startup.json'),("['E10_persistence_metadata','E10_pattern_binding_metadata']","['E10_persistence_metadata','E10_pattern_binding_metadata','E10_lifecycle_metadata']")]
 injection=''.join('definitions=definitions.replace('+repr(a)+','+repr(b)+')\n' for a,b in changes)
 assert anchor in s;s=s.replace(anchor,injection+anchor)
 s=s.replace(" and proof['post_reload_pattern_recall']",'')
 s=s.replace("proof['checkpoints']['reloaded-two-patterns']","case['ui_snapshot']").replace("proof['private_card']","paths.card")
 s=s.replace("with open(paths.card,'rb') as src","with open(source_paths.card,'rb') as src")
 return s
source=Path('work/probe-PC-E10-copy-cache.py').read_text(encoding='utf-8')
anchor="exec(compile(source,'E10-copy-cache-probe-definitions','exec'))"
assert anchor in source;source=source.replace(anchor,'source=adapt_fixture(source)\n'+anchor)
source=source.replace('E10-copy-cache-audit','E10-life-copy-cache').replace('outputs/E10-copy-cache-','outputs/E10-life-copy-cache-')
source=source.replace('Digitone-E10-PC-copy-cache-audit.json','Digitone-E10-PC-life-copy-cache.json')
source=source.replace("s.run_ms(200);tap('STOP');tap('NO');choose(1)","s.run_ms(200);tap('STOP')\n for _ in range(4):tap('NO',80)\n ui_root=rd(s.m.uc,0x419f0de0);selection=rd(s.m.uc,rd(s.m.uc,ui_root+0x40)+8)\n if selection<4:tap('MIDI')\n tap('T1');s.run_ms(150);choose(1)")
needle=" s.run_ms(200);tap('STOP')"
ready="""
 ui_ready=[False]
 def main_ui(u,pc,n,d):ui_ready[0]=True
 s.at(0x4014a056,main_ui)
 for _ in range(40):
  s.run_ms(250)
  if ui_ready[0]:break
 assert ui_ready[0],('Native project-load handler did not return to UI service',s.halted,hex(s.pc))
 print('native_ui_service_reached',s.now_ms(),flush=True)
 s.run_ms(200);tap('STOP')
"""
assert needle in source;source=source.replace(needle,ready,1)
# Populate both records through actual native editor actions in this session;
# this avoids serializing a live EMAC interrupt and performs no Save Project.
populate="""
 phase='A01_native_program';tap('SYN1');combo('A');combo('SYN2')
 if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=150)
 s.turn(3,-16,after_ms=120);s.turn(6,16,after_ms=120);s.turn(8,16,after_ms=120)
 first=bytes(s.m.uc.mem_read(BANK,32));assert first[:4]==b'MS10'
 tap('NO');choose(2);tap('SYN1');combo('A');combo('SYN2')
 if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=150)
 s.turn(1,16,after_ms=120);s.turn(6,-16,after_ms=120);s.turn(8,16,after_ms=120)
 second=bytes(s.m.uc.mem_read(BANK+32,32));assert second[:4]==b'MS10' and second!=first
 proof['expected_records']=[first.hex(),second.hex()]
 tap('NO');choose(1);tap('SYN1');combo('SYN2')
"""
source=source.replace("if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=150)\n phase='unsaved_step'",populate+" if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=150)\n phase='unsaved_step'",1)
source=source.replace("phase='unsaved_step';observe('before_unsaved_edit')","if s.frames:panel.write_png(s.frames[-1][1],'outputs/E10-life-editor-admission.png',4)\n assert rd(s.m.uc,X+56)==1 and rd(s.m.uc,X+28)==owner(),('M1 step editor did not open',selection,rd(s.m.uc,X+56),hex(owner()))\n phase='unsaved_step';observe('before_unsaved_edit')")
source=source.replace("out['operations'].append(row);print(label", "out['operations'].append(row)\n if s.frames:panel.write_png(s.frames[-1][1],'outputs/E10-life-operation-'+label+'.png',4)\n print(label")
needle=" assert s.halted is None;out['execution_passed']=True"
extra="""
 rows={r['label']:r for r in out['operations']}
 assert rows['before_unsaved_edit']['bank'][0]!=rows['after_unsaved_edit']['bank'][0]
 assert rows['after_unsaved_edit']['bank']==rows['after_unsaved_edit']['mirror']
 assert rows['pasted']['native_words'][1]==rows['before_copy']['native_words'][0]
 assert rows['pasted']['bank'][1]==rows['before_copy']['bank'][0]
 assert rows['undo_paste']['bank'][1]==rows['before_paste']['bank'][1]
 assert rows['pasted_again']['bank'][1]==rows['pasted']['bank'][1]
 assert rows['cleared']['bank']==rows['undo_clear']['bank']==rows['pasted_again']['bank']
 for label in ['pasted','undo_paste','pasted_again','cleared','undo_clear']:
  assert rows[label]['bank']==rows[label]['mirror'],label
 assert rows['undo_clear']['bank'][0]==rows['before_copy']['bank'][0]
 # Make one more edit without Save Project. This checkpoint is the input for
 # the explicit stock retained-bank writer and subsequent native cold boot.
 phase='final_unsaved_edit';choose(1);tap('SYN1');combo('SYN2')
 if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=150)
 s.turn(6,16,after_ms=200);observe('final_unsaved_edit')
 bank=bytes(s.m.uc.mem_read(BANK,4096));mirror=0x40555ff4
 assert all(bytes(s.m.uc.mem_read(mirror+0x240200+i*0xa00+0x940,32))==bank[32*i:32*i+32] for i in range(128))
 assert bank[:32].hex()!=proof['expected_records'][0]
 header=bytes(s.m.uc.mem_read(0x40555ee4,0x68))
 assert header[:4]==b'COKI' and int.from_bytes(header[4:8],'big')==sum(int.from_bytes(header[8+i*4:12+i*4],'big')^(i+1) for i in range(24))&0xffffffff
 from emu.snapshot import save
 checkpoint='work/E10-life-copy-cache/unsaved-edit.snap'
 save(s.m,checkpoint,components={**s.ev['checkpoint_components'],'timers':s.pits},manifest=s.ev.get('checkpoint_manifest'))
 s.ev['esdhc'].card.flush();preserved(s)
 out.update(passed=True,pattern_paste_and_undo_preserve_steps=True,clear_and_undo_retain_steps=True,unsaved_editor_mirror_synchronized=True,all_128_retained_records_match_bank=True,native_header_checksum_verified=True,unsaved_snapshot=checkpoint,private_card=paths.card,expected_bank=bank.hex(),no_manual_project_save_in_scenario=True)
 assert s.halted is None;out['execution_passed']=True
"""
assert needle in source;source=source.replace(needle,extra).replace("out['limits']=['Observational baseline, not a correctness certification. No extra E10 records/hooks/helpers/settings are host-written.','Native clipboard/undo operations and working-mirror observations on a private PC card. No physical power loss.']","out['limits']=['Copier-installed lifecycle image; native panel operations only. No bank/record/settings/hook/helper host writes.','Stopped full-pattern copy/paste/undo and trig clear/undo; arp settings follow native MIDI-setting clear semantics.','Unsaved records match the retained RAM image; native storage write/cold restore is a separate explicit PC control, not physical power loss.']")
exec(compile(source,'E10-life-native-copy-cache','exec'))
