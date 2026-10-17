"""Panel edits to current/incoming owners across a real native handoff."""
from pathlib import Path
source=Path('work/test-E08E-running-pattern-handoff.py').read_text().split('\ntry:')[0]
source=source.replace("prepared['checkpoints']['E08E-two-patterns-prepared']", "'work/os144/E08E-handoff-ready.snap'")
source=source.replace('Digitone-E08E-running-pattern-progress','Digitone-E08E-live-edit-progress')
exec(compile(source,'E08E-live-edit-session-definitions','exec'))
out.update(test='native current-owner and incoming-bank panel edits',settings_host_written=False)

def page():
    s.press(s.code('FUNC'));s.run_ms(100)
    s.tap(s.code('SYN2'),hold_ms=100,after_ms=150)
    s.release(s.code('FUNC'));s.run_ms(150)

def close():s.tap(s.code('NO'),hold_ms=100,after_ms=150)

def panel_probe(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7)
    event('panel_handler',u,handler=hex(pc),args=[hex(rd(u,sp+i*4)) for i in range(4)],**info(u))
for pc in [0x47be5f00,0x47be6300]:s.at(pc,panel_probe)

def snapshot_mark(label):
    mark(label)
    return out['pattern_marks'][-1]

try:
    s.run_ms(200)
    assert data_pointer(s.m.uc)==old_data and config()==[1,3,80,0]
    mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
    channel=rd(s.m.uc,0x41368d2c)&15
    def send(data):
        for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*.00032,byte)
        mi.received+=len(data);s.run_ms(60)
    chord=[0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100]
    release=[0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]
    phase='A01_live_start';s.tap(s.code('PLAY'),hold_ms=100,after_ms=150);send(chord)
    page();s.turn(3,-16,after_ms=150)
    snapshot_mark('A01_live_edit')
    assert word(s.m.uc)==0xadb2 and config()==[1,3,50,0]
    assert rd(s.m.uc,S+336)==old_data
    # Keep the page open so the actual encoder event can reach the incoming
    # UI record during the short look-ahead window. PTN remains a stock route.
    phase='request_A02';begin=len(out['events']);choose(2)
    snapshot_mark('A02_requested')
    phase='await_incoming_UI';s.press(s.code('FUNC'))
    for _ in range(700):
        if data_pointer(s.m.uc)==new_data:break
        s.run_ms(5)
    assert data_pointer(s.m.uc)==new_data,'native pattern request did not rebind UI'
    before=snapshot_mark('incoming_UI_before_context')
    assert rd(s.m.uc,S+336)==old_data and config()==[1,3,50,0],before
    # Native pattern rebinding closes the page. Reopen it with real input,
    # keeping the edit inside the observed ~125 ms look-ahead interval.
    phase='edit_incoming_before_context'
    s.tap(s.code('SYN2'),hold_ms=30,after_ms=10)
    s.release(s.code('FUNC'));s.run_ms(10)
    s.turn(3,16,after_ms=30)
    after=snapshot_mark('incoming_edit_deferred')
    reached=word(s.m.uc)==0xacb2
    out['incoming_panel_edit_reached']=reached
    out['incoming_panel_attempt']={'before':before,'after':after,
        'limit':'Only a changed saved word establishes that the incoming encoder edit reached the native controls.'}
    assert word(s.m.uc) in [0xac94,0xacb2],after
    assert rd(s.m.uc,S+336)==old_data and config()==[1,3,50,0],after
    phase='consume_A02'
    for _ in range(100):
        s.run_ms(20)
        if rd(s.m.uc,S+336)==new_data and config()==[1,1,50 if reached else 20,0]:break
    snapshot_mark('incoming_edit_applied')
    assert rd(s.m.uc,S+336)==new_data and config()==[1,1,50 if reached else 20,0]
    assert any(e['kind']=='context_applied' and e['data']==hex(new_data) for e in out['events'][begin:])
    phase='A02_live_edit';close();page();s.turn(3,16,after_ms=150)
    snapshot_mark('A02_live_edit')
    target_word=0xacd0 if reached else 0xacb2
    target_gate=80 if reached else 50
    assert word(s.m.uc)==target_word and config()==[1,1,target_gate,0]
    close();s.run_ms(500)
    phase='release';send(release);s.run_ms(400)
    assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    s.tap(s.code('STOP'),hold_ms=100,after_ms=150)
    phase='return_saved_A01';choose(1);s.run_ms(400)
    snapshot_mark('saved_A01_return')
    assert word(s.m.uc)==0xadb2 and config()==[1,3,50,0]
    phase='return_saved_A02';choose(2);s.run_ms(400)
    snapshot_mark('saved_A02_return')
    assert word(s.m.uc)==target_word and config()==[1,1,target_gate,0]
    preserved(s);out['MIDI_received']=mi.received;out['MIDI_delivered']=mi.delivered
    out['halted']=s.halted;assert s.halted is None
    out['passed']=True
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
    s.close();Path('outputs/Digitone-E08E-live-edit-handoff.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
