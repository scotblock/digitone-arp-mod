"""Native editor/keyboard/sequence playback from packaged loader startup."""
from pathlib import Path
import json
source=Path('work/test-PC-E10-integrated-playback.py').read_text(encoding='utf-8')
for a,b in [('PC_ONLY-E10-startup','PC_ONLY-E10-package'),('Digitone-E10-PC-integrated-startup.json','Digitone-E10-PC-package-startup.json'),('Digitone-E10-PC-integrated-playback.json','Digitone-E10-PC-package-playback.json')]:source=source.replace(a,b)
anchor="exec(compile(source,'E10-copied-native-editor-and-playback','exec'))"
old="    for region in native['data_regions']:"
new=old+"\n        if region['name'] in ['E10_persistence_metadata','E10_pattern_binding_metadata','E10_lifecycle_metadata']:continue"
injection="source=source.replace(\"exec(compile(prefix,'M1-both-port-definitions','exec'))\", 'prefix=prefix.replace('+repr("+repr(old)+")+','+repr("+repr(new)+")+')\\n'+\"exec(compile(prefix,'M1-both-port-definitions','exec'))\")\n"
# Select an unused native pattern, leaving the two restored programs intact.
select="""
    s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
    restored_bank=bytes(s.m.uc.mem_read(native['E10']['bank'],4096))
    assert restored_bank[:64]!=bytes(64) and restored_bank[64:96]==bytes(32)
    s.press(s.code('PTN'));s.run_ms(80);s.tap(s.code('3'),hold_ms=80,after_ms=80);s.release(s.code('PTN'));s.run_ms(300)
    out['native_selected_test_pattern']='A03'
"""
injection+='source=source.replace('+repr("    s.tap(s.code('STOP'),hold_ms=100,after_ms=100)")+','+repr(select)+',1)\n'
injection+='source=source.replace('+repr("    phase='native_editor'")+','+repr("    phase='native_editor'")+')\n'
select_M1="""
    selection=rd(s.m.uc,rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x40)+8)
    if selection<4:s.tap(s.code('MIDI'),hold_ms=100,after_ms=100)
    s.tap(s.code('T1'),hold_ms=100,after_ms=100);s.run_ms(200)
    assert rd(s.m.uc,rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x40)+8)==4
"""
original_M1="    s.press(s.code('MIDI'));s.tap(s.code('T1'),hold_ms=100,after_ms=100);s.release(s.code('MIDI'));s.run_ms(200)"
injection+='source=source.replace('+repr(original_M1)+','+repr(select_M1)+',1)\n'
check="""    assert s.halted is None;preserved(s)
    assert bytes(s.m.uc.mem_read(native['E10']['bank'],64))==restored_bank[:64]
    record=bytes(s.m.uc.mem_read(native['E10']['bank']+64,32))
    assert record[:4]==b'MS10' and record[6]==4 and record[12:16]==bytes([0,1,2,3])
    assert sum(record[:28])==int.from_bytes(record[28:32],'big')
    out['restored_A01_A02_preserved']=True;out['A03_native_editor_record_valid']=True
"""
injection+='source=source.replace('+repr("    assert s.halted is None;preserved(s)")+','+repr(check)+',1)\n'
assert anchor in source;source=source.replace(anchor,injection+anchor)
exec(compile(source,'E10-packaged-native-editor-playback','exec'))
p=Path('outputs/Digitone-E10-PC-package-playback.json');r=json.loads(p.read_text());assert r['passed'] and r['matching_note_pairs']>=12
r.update(loader_derived_E10_state=True,firmware_container_created=True,internal_loader_test_only=True,firmware_release_created=False,hardware_ready=False,native_project_persistence=True,automatic_pattern_binding=True)
r['limits']=['Source snapshot is the actual internal E10 package loader/handoff/native copier/init/logo path. Keyboard and native sequencer use native panel-created A03 steps.','Inherited MIDI input/routing/USB endpoint handoff fixtures remain; no physical port/timing guarantee. No E10 bank/settings/helper/hook bytes are host-inserted.','Stock power handling is the accepted inherited assumption. Abrupt-loss recovery is not guaranteed.']
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
