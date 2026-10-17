from pathlib import Path
source=Path('work/test-os144-pattern-isolation.py').read_text().split("exec(compile(s,'stock-pattern-isolation','exec'))")[0]
exec(compile(source,'build-pattern-control','exec'))
s=s.replace('Digitone-OS1.44-stock-pattern-isolation.json','Digitone-OS1.44-stock-sustain-transition.json')
s=s.replace("mark('initial')","mi=midi.MidiIn();mi.attach(session.m,session.ips);session.sources=session.sources+(mi,);mark('initial')")
s=s.replace("mark('request 1')", """mark('request 1')
 setting=0x41368d64;before=rd(session.m.uc,setting);session.m.uc.mem_write(setting,u32(before|3));channel=rd(session.m.uc,0x41368d2c)&15
 r['fixtures'].append({'kind':'MIDI input enable','address':hex(setting),'before':hex(before),'after':hex(before|3),'auto_channel_zero_based':channel})
 send([0xb0|channel,64,127],'CC64 on');send([0x90|channel,60,100],'MIDI note on');session.run_ms(40);send([0x80|channel,60,0],'note off while sustained');session.run_ms(40);mark('sustained waiting for handoff')""")
s=s.replace("r['inputs']=session.inputs;r['halted']=session.halted", """mark('confirmed handoff or bounded failure')
 send([0xb0|channel,64,0],'CC64 off');session.run_ms(100);mark('sustain release settled')
 send([0x90|channel,62,100],'fresh receiving note on');session.run_ms(80);send([0x80|channel,62,0],'fresh receiving note off');session.run_ms(100);mark('fresh note release settled')
 accepted=[e for e in r['events'] if e['kind']=='acceptance' and e.get('publication')]
 r['cross_pattern_acceptances']=[e for e in accepted if e['backing']!=e['publication']['backing']]
 r['checks']={'no_engine_halt':session.halted is None,'queue_publication_and_acceptance':bool(accepted),'matching_event_generations':bool(accepted) and all(e['generation']==e['publication']['generation'] for e in accepted),'all_midi_delivered':mi.received==mi.delivered,'actual_playing_handoff':r['actual_playing_handoff']}
 r['inputs']=session.inputs;r['halted']=session.halted""")
exec(compile(s,'stock-sustain-transition','exec'))
