"""Run the prepared distinct patterns, keeping native input and transition ordering."""
from pathlib import Path
definitions=Path('work/test-E08C-pattern-settings.py').read_text().split('\ns=Session(')[0]
anchor="exec(compile(source,'E08C-packaged-session-definitions','exec'))"
assert anchor in definitions
definitions=definitions.replace(anchor,
    "source=source.replace('assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]', 'assert rd(s.m.uc,S)==0x4d314131')\n"+anchor)
exec(compile(definitions,'E08C-handoff-definitions','exec'))
prepared=json.loads(Path('outputs/Digitone-E08C-pattern-settings.json').read_text())
assert prepared['passed'] and prepared['two_pattern_settings_isolated']
marks={r['label']:r for r in prepared['pattern_marks']}
old_data=int(marks['A01_set']['data'],16);new_data=int(marks['A02_set']['data'],16)
out.update(preparation='outputs/Digitone-E08C-pattern-settings.json',queued_old_note_witnesses=[])
base_install=install
def install(s):
    base_install(s)
    def context_done(u,pc,n,d):
        ptr=u.reg_read(UC_M68K_REG_A2)
        if rd(u,ptr)==2:event('context_applied',u,descriptor=hex(ptr),**info(u))
    s.at(0x400f40ba,context_done)
    def settings_write(u,access,a,n,value,d):
        event('pending_settings_word',u,writer=hex(u.reg_read(UC_M68K_REG_PC)),value=value,**info(u))
    s.m.uc.hook_add(UC_HOOK_MEM_WRITE,settings_write,begin=S+324,end=S+327)
    def configured(u,pc,n,d):
        sp=u.reg_read(UC_M68K_REG_A7)
        event('configure_called',u,caller=hex(rd(u,sp)),rate_index=rd(u,sp+4),gate_percent=rd(u,sp+8),**info(u))
    s.at(native['entries']['configure'],configured)

s=Session(prepared['checkpoints']['E08C-two-patterns-prepared'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
def mark(label):
    row={'label':label,'ms':s.now_ms(),**info(s.m.uc)};out['pattern_marks'].append(row)
    if s.frames:panel.write_png(s.frames[-1][1],'outputs/E08C-handoff-'+label+'.png',4)
    Path('outputs/Digitone-E08C-running-pattern-progress.json').write_text(json.dumps(out,indent=2))
    print(label,row,flush=True)
def choose(number):
    s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code(str(number)),hold_ms=100,after_ms=100)
    s.release(s.code('PTN'));s.run_ms(100)
def wait_for(data,target):
    begin=len(out['events'])
    for _ in range(24):
        s.run_ms(250)
        if data_pointer(s.m.uc)==data and config()==target and any(e['kind']=='context_applied' and e['data']==hex(data) for e in out['events'][begin:]):
            return True
    return False
def checkpoint(name):
    path=Path('work/os144')/(name+'.snap')
    save(s.m,str(path),components={**s.ev['checkpoint_components'],'timers':s.pits},manifest=s.ev.get('checkpoint_manifest'))
    out.setdefault('checkpoints',{})[name]=str(path.resolve())
try:
    s.run_ms(200);assert data_pointer(s.m.uc)==old_data and config()==[1,3,80,0]
    # Exercise the native channel page and decode the actual serial channels.
    # A bulk encoder request does not establish a requested channel number.
    phase='channel_A01';s.tap(s.code('SYN1'),hold_ms=100,after_ms=150);s.turn(1,127,after_ms=250);mark('A01_channel_setup')
    choose(2);s.run_ms(400);assert data_pointer(s.m.uc)==new_data
    phase='channel_A02';s.tap(s.code('SYN1'),hold_ms=100,after_ms=150);s.turn(1,127,after_ms=250);mark('A02_channel_setup')
    choose(1);s.run_ms(400);assert data_pointer(s.m.uc)==old_data
    checkpoint('E08C-handoff-ready')
    mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
    gate=rd(s.m.uc,0x41368d64);out['input_gate_fixture']={'before':gate,'after':gate|3}
    if gate|3!=gate:s.m.uc.mem_write(0x41368d64,struct.pack('>I',gate|3))
    channel=rd(s.m.uc,0x41368d2c)&15
    def send(data):
        for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*.00032,byte)
        mi.received+=len(data);s.run_ms(60)
    chord=[0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100]
    release=[0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]
    phase='A01_held';s.tap(s.code('PLAY'),hold_ms=100,after_ms=150);send(chord);s.run_ms(300);mark('A01_held')
    assert rd(s.m.uc,S+8)==1 and rd(s.m.uc,S+16)==3
    phase='request_A02';request=len(out['events']);old_backing=rd(s.m.uc,0x4138f214);choose(2);mark('A02_request')
    phase='handoff_A02';out['A02_context_applied']=wait_for(new_data,[1,1,20,0]);mark('A02_completed')
    assert out['A02_context_applied'] and rd(s.m.uc,0x4138f214)!=old_backing
    out['completion_witness']='Receiving MIDI context was consumed/applied and native backing/data pointers changed; the periodic service probe is not a completion witness.'
    s.run_ms(900);mark('A02_held_playback')
    phase='A02_release';send(release);s.run_ms(350);mark('A02_released')
    assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    phase='request_A01';choose(1)
    phase='handoff_A01';out['A01_context_applied']=wait_for(old_data,[1,3,80,0]);mark('A01_completed')
    assert out['A01_context_applied']
    phase='A01_fresh';send(chord);s.run_ms(500);send(release);s.run_ms(350);mark('A01_fresh_released')
    assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
    checkpoint('E08C-after-two-pattern-handoff')
    preserved(s);out['MIDI_received']=mi.received;out['MIDI_delivered']=mi.delivered
    out['halted']=s.halted;assert s.halted is None
    out['passed']=True
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
    s.close();Path('outputs/Digitone-E08C-running-pattern-handoff.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
