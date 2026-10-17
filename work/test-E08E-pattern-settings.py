"""Native panel preparation and real M1 pattern transitions, PC only."""
from pathlib import Path
source=Path('work/test-E08E-packaged-panel-playback.py').read_text().split('\ns = Session(')[0]
exec(compile(source,'E08E-packaged-session-definitions','exec'))
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_A2,UC_M68K_REG_A7,UC_M68K_REG_D0,UC_M68K_REG_PC
from emu.snapshot import save

out.update(events=[],pattern_marks=[],settings_writes_host_injected=False)
original_install=install
def config():return [rd(s.m.uc,S+x) for x in [4,304,308,320]]
def data_pointer(u):
    root=rd(u,0x419f0de0)
    return rd(u,root+0xff8+16) if root else 0
def word(u):
    data=data_pointer(u)
    return int.from_bytes(u.mem_read(data+158,2),'big') if data else None
def selection(u):
    root=rd(u,0x419f0de0)
    data=rd(u,root+0x30+16) if root else 0
    return rd(u,data+8) if data else -1
def info(u):return {'data':hex(data_pointer(u)),'word':word(u),'config':[rd(u,S+x) for x in [4,304,308,320]],
                    'pattern':bytes(u.mem_read(0x4138f20c,2)).hex(),'backing':hex(rd(u,0x4138f214)),
                    'transport':rd(u,0x4138f208),'selection':selection(u),
                    'held':[rd(u,S+x) for x in [8,12,16,280]], 'owner':hex(rd(u,S+336)), 'request_owner':hex(rd(u,S+340)), 'stock_kit':hex(rd(u,0x419c5b10)), 'stock_cache':hex(rd(u,0x419c5b14))}
def event(label,u,**fields):
    out['events'].append({'kind':label,'phase':phase,'ms':s.now_ms(),**fields})
def install(s):
    original_install(s)
    def queue(u,pc,n,d):
        ptr=u.reg_read(UC_M68K_REG_A2);kind=rd(u,ptr)
        if kind==2:
            kit=rd(u,ptr+4)
            event('context_consume',u,descriptor=hex(ptr),kit=hex(kit),
                  descriptor_word=int.from_bytes(u.mem_read(kit+0x66c,2),'big') if kit else None,
                  **info(u))
        elif kind in [0,1] and rd(u,ptr+4)==0 and rd(u,ptr+0x2c)==2:
            event('live_consume',u,descriptor=hex(ptr),onoff=rd(u,ptr+8),
                  notes=list(u.mem_read(ptr+20,min(8,rd(u,ptr+16)))),**info(u))
    s.at(0x400f40b4,queue)
    # 400964ce is periodic sequencer service, not a unique completion callback.
    for label,pc in [('pattern_publish',0x40094f4a),('sequencer_service',0x400964ce)]:
        s.at(pc,lambda u,p,n,d,label=label:event(label,u,**info(u)))

s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
def mark(label):
    row={'label':label,'ms':s.now_ms(),**info(s.m.uc)}
    out['pattern_marks'].append(row)
    if s.frames:panel.write_png(s.frames[-1][1],'outputs/E08E-pattern-'+label+'.png',4)
    print(label,row,flush=True)
    Path('outputs/Digitone-E08E-pattern-settings-progress.json').write_text(json.dumps(out,indent=2))
def select_pattern(number):
    s.press(s.code('PTN'));s.run_ms(100)
    s.tap(s.code(str(number)),hold_ms=100,after_ms=100)
    s.release(s.code('PTN'));s.run_ms(400)
def combo(key):
    s.press(s.code('FUNC'));s.run_ms(100)
    s.tap(s.code(key),hold_ms=100,after_ms=150)
    s.release(s.code('FUNC'));s.run_ms(150)
def page():combo('SYN2')
def close():s.tap(s.code('NO'),hold_ms=100,after_ms=150)
def checkpoint(name):
    path=Path('work/os144')/(name+'.snap')
    save(s.m,str(path),components={**s.ev['checkpoint_components'],'timers':s.pits},manifest=s.ev.get('checkpoint_manifest'))
    out.setdefault('checkpoints',{})[name]=str(path.resolve())

try:
    if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
        timer=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);timer.now=s.pits.now;s.pits.sources=s.pits.sources+(timer,)
    s.run_ms(6500)
    s.tap(s.code('STOP'),hold_ms=100,after_ms=150)
    if selection(s.m.uc)<4:s.tap(s.code('MIDI'),hold_ms=100,after_ms=150)
    s.tap(s.code('T1'),hold_ms=100,after_ms=150)
    assert selection(s.m.uc)==4
    phase='A01_prepare';select_pattern(1);mark('A01_initial')
    s.tap(s.code('SYN1'),hold_ms=100,after_ms=150);s.press(s.code('FUNC'));s.tap(s.code('A'),hold_ms=100,after_ms=150);s.release(s.code('FUNC'));s.run_ms(150)
    page();s.turn(1,16,after_ms=250);s.turn(2,16,after_ms=250);s.turn(3,16,after_ms=250);mark('A01_set')
    assert word(s.m.uc)==0xadd0 and config()==[1,3,80,0]
    close()
    phase='A02_prepare';select_pattern(2);mark('A02_initial')
    s.tap(s.code('SYN1'),hold_ms=100,after_ms=150);s.press(s.code('FUNC'));s.tap(s.code('A'),hold_ms=100,after_ms=150);s.release(s.code('FUNC'));s.run_ms(150)
    page();s.turn(1,16,after_ms=250);s.turn(2,-16,after_ms=250);s.turn(3,-16,after_ms=250);mark('A02_set')
    assert word(s.m.uc)==0xac94 and config()==[1,1,20,0]
    close()
    phase='A01_return';select_pattern(1);mark('A01_return')
    assert word(s.m.uc)==0xadd0 and config()==[1,3,80,0]
    checkpoint('E08E-two-patterns-prepared')
    out['two_pattern_settings_isolated']=True
    out['halted']=s.halted;assert s.halted is None
    preserved(s);out['passed']=True
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
    s.close();Path('outputs/Digitone-E08E-pattern-settings.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
