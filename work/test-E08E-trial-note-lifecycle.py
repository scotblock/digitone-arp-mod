"""Native held Stop, CC64/release, and OFF/UP controls before trial review."""
from pathlib import Path
source=Path('work/test-E08E-running-pattern-handoff.py').read_text().split('\ntry:')[0]
source=source.replace("prepared['checkpoints']['E08E-two-patterns-prepared']", "'work/os144/E08E-handoff-ready.snap'")
source=source.replace('Digitone-E08E-running-pattern-progress','Digitone-E08E-trial-note-progress')
exec(compile(source,'E08E-trial-note-lifecycle-definitions','exec'))

def state():return [rd(s.m.uc,S+x) for x in [4,8,12,16,280]]
def record(label):
    row={'label':label,'ms':s.now_ms(),'state':state(),**info(s.m.uc)}
    out['marks'].append(row);print(label,row['state'],flush=True)
def page():
    s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN2'),hold_ms=100,after_ms=150)
    s.release(s.code('FUNC'));s.run_ms(150)
def close():s.tap(s.code('NO'),hold_ms=100,after_ms=150)

try:
    s.run_ms(200)
    assert config()==[1,3,80,0]
    mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
    channel=rd(s.m.uc,0x41368d2c)&15
    def send(raw):
        for i,b in enumerate(raw):mi._push(s.pits.now+(i+1)*s.ips*.00032,b)
        mi.received+=len(raw);s.run_ms(100)
    chord=sum(([0x90|channel,n,100] for n in [60,64,67]),[])
    release=sum(([0x80|channel,n,0] for n in [60,64,67]),[])
    phase='held_Stop';s.tap(s.code('PLAY'),hold_ms=100,after_ms=150);send(chord);s.run_ms(300)
    record('before_held_Stop');assert state()[1:4]==[1,1,3]
    out['held_Stop_ms']=s.now_ms();s.tap(s.code('STOP'),hold_ms=100,after_ms=300)
    record('after_held_Stop');assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    phase='release_after_Stop';send(release);s.run_ms(250);record('release_after_Stop')
    phase='sustain_down';s.tap(s.code('PLAY'),hold_ms=100,after_ms=150);send(chord);send([0xb0|channel,64,127]);s.run_ms(200)
    record('sustain_held');assert rd(s.m.uc,S+16)==3
    phase='sustain_keys_up';send(release);s.run_ms(250);record('sustain_keys_up')
    out['held_count_after_keys_up_with_CC64']=rd(s.m.uc,S+16)
    phase='sustain_pedal_up';send([0xb0|channel,64,0]);s.run_ms(300);record('sustain_pedal_up')
    assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    phase='mode_OFF_held';send(chord);page();s.turn(1,-16,after_ms=250);record('mode_OFF_held')
    assert config()[:3]==[0,3,80] and rd(s.m.uc,S+8)==0
    close();phase='release_while_OFF';send(release);s.run_ms(250);record('release_while_OFF')
    phase='re_enable_idle';page();s.turn(1,16,after_ms=250);close();s.run_ms(250);record('re_enable_idle')
    assert config()[:3]==[1,3,80] and rd(s.m.uc,S+8)==0
    phase='fresh_after_re_enable';send(chord);s.run_ms(300);record('fresh_after_re_enable');assert rd(s.m.uc,S+16)==3
    phase='final_release';send(release);s.run_ms(300);s.tap(s.code('STOP'),hold_ms=100,after_ms=200);record('final_stop')
    assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    preserved(s);out['MIDI_received']=mi.received;out['MIDI_delivered']=mi.delivered
    out['halted']=s.halted;assert s.halted is None
    out['passed']=True
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
    s.close();Path('outputs/Digitone-E08E-trial-note-lifecycle.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
