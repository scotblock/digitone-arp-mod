"""Actual sequenced chords restored from the generated project, no settings injection."""
from pathlib import Path
source=Path('work/test-E08E-pattern-settings.py').read_text().split('\ns=Session(')[0]
# Its nested definitions also read the packaged panel test prefix. Redirect only
# the startup report read, leaving baseline reports and cards untouched.
source=source.replace("exec(compile(source,'E08E-packaged-session-definitions','exec'))", "source=source.replace('outputs/Digitone-E08E-PC-startup-comparison.json','outputs/Digitone-E08E-test-project-startup.json')\nexec(compile(source,'E08E-project-session-definitions','exec'))")
exec(compile(source,'test-project-playback-definitions','exec'))
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)

def select(number):
    s.press(s.code('PTN'));s.run_ms(100)
    s.tap(s.code(str(number)),hold_ms=100,after_ms=100)
    s.release(s.code('PTN'));s.run_ms(400)

def mark(label):
    row={'label':label,**info(s.m.uc)};out.setdefault('project_marks',[]).append(row)
    print(label,row,flush=True)

try:
    if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
        timer=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);timer.now=s.pits.now;s.pits.sources=s.pits.sources+(timer,)
    s.run_ms(6500);s.tap(s.code('STOP'),hold_ms=100,after_ms=150)
    if selection(s.m.uc)<4:s.tap(s.code('MIDI'),hold_ms=100,after_ms=150)
    s.tap(s.code('T1'),hold_ms=100,after_ms=150)
    assert selection(s.m.uc)==4
    mark('restored_A01')
    # The saved mirror also has an active edit buffer outside the flat image.
    # Explicitly select another slot before judging the generated saved kit.
    phase='A02_select';select(2);mark('A02_UP')
    out['saved_M1_tag_restored']=word(s.m.uc)==0xad32
    out['restored_M1_channel']=int.from_bytes(s.m.uc.mem_read(data_pointer(s.m.uc)+0x22,1),'big')+1
    # Exercise sequenced pitches on the observed restored channel independently
    # of channel persistence; do not host-write the target channel into RAM.
    if not out['saved_M1_tag_restored']:
        phase='manual_UP'
        s.press(s.code('FUNC'));s.run_ms(100)
        s.tap(s.code('SYN2'),hold_ms=100,after_ms=200)
        s.release(s.code('FUNC'));s.run_ms(150)
        s.turn(1,16,after_ms=250)
        assert word(s.m.uc)==0xad32
        s.tap(s.code('NO'),hold_ms=100,after_ms=200)
        out['manual_MODE_UP_required']=True
    phase='A02_play';s.tap(s.code('PLAY'),hold_ms=100,after_ms=100);s.run_ms(2500)
    mark('A02_playing')
    phase='stop';s.tap(s.code('STOP'),hold_ms=100,after_ms=400)
    mark('stopped')
    notes=[];pending=None
    # MidiOut's observer normally reports one byte per callback; support either
    # message-sized or byte-sized batches and MIDI running status.
    status=None;data=[]
    for entry in out['wire']:
        for b in entry['bytes']:
            if b>=0xf8:continue
            if b&0x80:status=b;data=[];continue
            if status is None:continue
            data.append(b)
            needed=1 if status&0xf0 in [0xc0,0xd0] else 2
            if len(data)==needed:
                if status&0xf0==0x90 and data[1]>0:notes.append({'channel':(status&15)+1,'pitch':data[0]})
                data=[]
    out['generated_project_note_ons']=notes
    assert len(notes)>=6,notes
    assert all(n['channel']==out['restored_M1_channel'] and n['pitch'] in [60,64,67] for n in notes),notes
    assert [n['pitch'] for n in notes[:6]]==[60,64,67,60,64,67],notes
    assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    preserved(s);assert s.halted is None
    out['passed']=True
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
    s.close();Path('outputs/Digitone-E08E-test-project-playback.json').write_text(json.dumps(out,indent=2))
if not out['passed']:raise SystemExit(1)
