"""Panel edits to current/incoming owners across a real native handoff."""
from pathlib import Path
source=Path('work/test-E08E-running-pattern-handoff.py').read_text().split('\ntry:')[0]
source=source.replace("prepared['checkpoints']['E08E-two-patterns-prepared']", "'work/os144/E08E-handoff-ready.snap'")
source=source.replace('Digitone-E08E-running-pattern-progress','Digitone-E08E-complete-panel-race-progress')
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

from unicorn.m68k_const import UC_M68K_REG_D2,UC_M68K_REG_A4,UC_M68K_REG_A0
def detailed(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7)
    row=dict(handler=hex(pc),a4=hex(u.reg_read(UC_M68K_REG_A4)),d2=hex(u.reg_read(UC_M68K_REG_D2)),
        args=[hex(rd(u,sp+i*4)) for i in range(4)])
    if pc in [0x47be6300,0x47be6500,0x47be6000]:
        view=rd(u,sp+4);row['view']=hex(view);row['view_tag']=hex(rd(u,view+0x2c8))
    event('detailed_panel',u,**row,**info(u))
for pc in [0x47be5f00,0x47be6300,0x47be6500,0x47be6c80,0x47be6600,0x4003fc42,0x4003fc60,0x47be7000]:s.at(pc,detailed)



from unicorn.m68k_const import UC_M68K_REG_D0
returns={}
def boundary(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);ret=rd(u,sp)
    count={0x47be5900:4,0x4014eff8:2,0x47be7000:3}[pc]
    args=[rd(u,sp+4+i*4) for i in range(count)]
    event('panel_boundary_enter',u,callee=hex(pc),args=[hex(v) for v in args],return_pc=hex(ret),**info(u))
    returns.setdefault(ret,[]).append((pc,args))
    if len(returns[ret])==1 and ret not in hooked:
        hooked.add(ret);s.at(ret,boundary_return)
def boundary_return(u,pc,n,d):
    frames=returns.get(pc)
    if not frames:return
    callee,args=frames.pop()
    event('panel_boundary_return',u,callee=hex(callee),args=[hex(v) for v in args],result=hex(u.reg_read(UC_M68K_REG_D0)),**info(u))
hooked=set()
for pc in [0x47be5900,0x4014eff8,0x47be7000]:s.at(pc,boundary)

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
    snapshot_mark('A02_requested');checkpoint('E08E-panel-race-requested')
    phase='await_incoming_UI'
    for _ in range(700):
        if data_pointer(s.m.uc)==new_data:break
        s.run_ms(5)
    assert data_pointer(s.m.uc)==new_data,'native pattern request did not rebind UI'
    before=snapshot_mark('incoming_UI_before_context')
    assert rd(s.m.uc,S+336)==old_data and config()==[1,3,50,0],before
    phase='edit_incoming_before_context';s.turn(3,16,after_ms=80)
    after=snapshot_mark('incoming_edit_deferred')
    reached=word(s.m.uc)==0xacb2
    assert reached, 'The actual incoming panel edit must reach the native record in this test'
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
    s.close();Path('outputs/Digitone-E08E-complete-panel-race-handoff.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
