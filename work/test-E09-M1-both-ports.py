"""Actual E08F M1 scheduler through DIN and USB encoding, endpoint handoff fixture."""
from pathlib import Path
prefix=Path('work/test-E08F-packaged-panel-playback.py').read_text().split('\ns = Session(')[0]
exec(compile(prefix,'M1-both-port-definitions','exec'))
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_A7,UC_M68K_REG_PC
out['USB_packets']=[];original_install=install
def install(s):
    original_install(s)
    def bulk(u,pc,n,d):
        sp=u.reg_read(UC_M68K_REG_A7);length=rd(u,sp+4);ptr=rd(u,sp+8)
        out['USB_packets'].append({'phase':phase,'bytes':list(u.mem_read(ptr,length))})
        u.reg_write(UC_M68K_REG_PC,rd(u,sp));u.reg_write(UC_M68K_REG_A7,sp+4)
    s.m.uc.hook_add(UC_HOOK_CODE,bulk,begin=0x40004a6e,end=0x40004a6e)
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
try:
    if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
        t=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);t.now=s.pits.now;s.pits.sources=s.pits.sources+(t,)
    for _ in range(10):
        s.run_ms(1000)
        if s.ev['dsplink'].booted and s.ev['dsplink'].renders>100:break
    s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
    s.press(s.code('MIDI'));s.tap(s.code('T1'),hold_ms=100,after_ms=100);s.release(s.code('MIDI'));s.run_ms(200)
    s.tap(s.code('SYN1'),hold_ms=100,after_ms=100)
    s.press(s.code('FUNC'));s.tap(s.code('A'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(150)
    s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN2'),hold_ms=100,after_ms=150);s.release(s.code('FUNC'));s.run_ms(150)
    s.turn(1,16,after_ms=200);s.tap(s.code('NO'),hold_ms=100,after_ms=150)
    mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
    s.m.uc.mem_write(0x41368d64,struct.pack('>I',rd(s.m.uc,0x41368d64)|3))
    channel=rd(s.m.uc,0x41368d2c)&15
    for a,v in [(0x419c5df4,3),(0x40529244,1),(0xfc0b01c4,1),(0x40529248,0),(0x4052924c,0),(0x40529234,0)]:s.m.uc.mem_write(a,struct.pack('>I',v))
    def send(data):
        for i,b in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*.00032,b)
        mi.received+=len(data);s.run_ms(80)
    out['wire']=[];out['USB_packets']=[];phase='UP_both'
    send([v for note in [60,64,67] for v in [0x90|channel,note,100]])
    s.run_ms(1200)
    phase='release';send([v for note in [60,64,67] for v in [0x80|channel,note,0]])
    s.run_ms(300);s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
    def notes(raw):
        status=None;data=[];result=[]
        for b in raw:
            if b>=0xf8:continue
            if b&128:status=b;data=[];continue
            if status is None:continue
            data.append(b)
            if len(data)==(1 if status&0xf0 in [0xc0,0xd0] else 2):
                if status&0xf0 in [0x80,0x90]:result.append([status,*data])
                data=[]
        return result
    din=notes([b for e in out['wire'] for b in e['bytes']]);usb=[]
    for e in out['USB_packets']:
        raw=e['bytes'];assert len(raw)%4==0
        for i in range(0,len(raw),4):
            p=raw[i:i+4]
            if p[0]&15 in [8,9]:usb.append(p[1:4])
    assert din==usb and len(din)>=12,(din,usb)
    active=set();ons=0
    for status,n,v in din:
        k=status&15,n
        if status&0xf0==0x90 and v:assert k not in active;active.add(k);ons+=1
        else:assert k in active;active.remove(k)
    assert not active and [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    assert s.halted is None;preserved(s)
    out.update(passed=True,DIN_notes=din,USB_notes=usb,matching_note_pairs=ons,
      route_and_USB_state_are_fixtures=True,USB_endpoint_handoff_is_fixture=True,
      physical_port_delivery_verified=False)
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:s.close();Path('outputs/Digitone-E09-M1-both-ports.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
