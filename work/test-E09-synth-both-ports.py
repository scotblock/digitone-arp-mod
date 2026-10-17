"""Actual synth arp playback with E09 PC helper overlay; USB endpoint fixture."""
from pathlib import Path
prefix=Path('work/test-E08F-packaged-panel-playback.py').read_text().split('\ns = Session(')[0]
exec(compile(prefix,'synth-both-definitions','exec'))
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_A7,UC_M68K_REG_D0,UC_M68K_REG_PC
dual=json.loads(Path('work/os144/E09-PC-dual-port-layout.json').read_text());dp=Path('work/os144/E09-PC-dual-port-payload.bin').read_bytes()
out['USB_packets']=[];out['arp_step_fixtures']=[];original_install=install
def install(s):
    original_install(s);u=s.m.uc;pb=dual['base']
    for p in range(pb+len(payload)//4096*4096,pb+len(dp),4096):s.m.ensure(p)
    u.mem_write(pb+len(payload),dp[len(payload):])
    for p in dual['patches']:
        assert bytes(u.mem_read(p['base'],p['bytes'])).hex()==p['before'];u.mem_write(p['base'],bytes.fromhex(p['after']))
    for r in dual['regions']+dual['patches']:s.m.install_isa_patches_scoped(dp[r['base']-pb:r['base']-pb+r['bytes']],r['base'])
    def submit(u,pc,n,d):
        sp=u.reg_read(UC_M68K_REG_A7);desc=rd(u,sp+8);size=rd(u,desc+0x20);ptr=rd(u,desc+8)
        out['USB_packets'].append({'phase':phase,'bytes':list(u.mem_read(ptr,size))})
        u.reg_write(UC_M68K_REG_D0,0);u.reg_write(UC_M68K_REG_PC,rd(u,sp));u.reg_write(UC_M68K_REG_A7,sp+4)
    s.m.uc.hook_add(UC_HOOK_CODE,submit,begin=0x40005f1e,end=0x40005f1e)
    def steps(u,pc,n,d):
        track=rd(u,u.reg_read(UC_M68K_REG_A7)+4)
        if track>=4:return
        ptr=rd(u,0x413915f4+track*40+0x20)
        if not 0x40000000<=ptr<0x48000000:return
        u.mem_write(ptr+0x111,bytes([0]));u.mem_write(ptr+0x113,bytes([7]));u.mem_write(ptr+0x114,bytes.fromhex('00ff'));u.mem_write(ptr+0x116,bytes(range(8)))
        out['arp_step_fixtures'].append({'track':track,'settings':hex(ptr),'length':8,'offsets':list(range(8))})
    s.at(0x40097e46,steps)
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
try:
    if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
        t=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);t.now=s.pits.now;s.pits.sources=s.pits.sources+(t,)
    for _ in range(10):
        s.run_ms(1000)
        if s.ev['dsplink'].booted and s.ev['dsplink'].renders>100:break
    s.tap(s.code('STOP'),hold_ms=100,after_ms=100);s.tap(s.code('T1'),hold_ms=100,after_ms=100)
    s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN1'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(150)
    s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('KEYBOARD'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(150)
    s.tap(s.code('NO'),hold_ms=100,after_ms=100)
    for back in {rd(s.m.uc,0x4138f214),0x407fd414,0x40813531}:
        for track in range(4):s.m.uc.mem_write(back+track*0x3d0+0x3cb,bytes([60]));s.m.uc.mem_write(back+track*0x3d0+0x3ce,bytes([0]))
    mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
    s.m.uc.mem_write(0x41368d64,struct.pack('>I',rd(s.m.uc,0x41368d64)|3));ch=rd(s.m.uc,0x41368d2c)&15
    pool=0x47bf0000;s.m.ensure(pool)
    for i in range(64):s.m.uc.mem_write(pool+i*64,bytes(64));s.m.uc.mem_write(pool+i*64+0x34,struct.pack('>I',pool+(i+1)*64 if i<63 else 0))
    for a,v in [(0x419c5df4,3),(0x41368d30,0),(0x40529244,1),(0xfc0b01c4,1),(0x40529248,0),(0x4052924c,0),(0x40529234,0),(0x40529388,pool),(0x429f23b8,0)]:s.m.uc.mem_write(a,struct.pack('>I',v))
    def send(data):
        for i,b in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*.00032,b)
        mi.received+=len(data);s.run_ms(80)
    out['wire']=[];out['USB_packets']=[];phase='synth_UP_both'
    s.tap(s.code('PLAY'),hold_ms=100,after_ms=150);send([0x90|ch,60,100]);s.run_ms(2000)
    phase='release';send([0x80|ch,60,0]);s.run_ms(700);s.tap(s.code('STOP'),hold_ms=100,after_ms=300)
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
            if raw[i]&15 in [8,9]:usb.append(raw[i+1:i+4])
    assert din==usb and len(din)>=12,(din,usb)
    active=set();on=[]
    for status,n,v in din:
        k=status&15,n
        if status&0xf0==0x90 and v:assert k not in active;active.add(k);on.append(n)
        else:assert k in active;active.remove(k)
    assert not active and out['arp_step_fixtures']
    for base in [layout['MIDI_records'],dual['USB_records']]:assert all(rd(s.m.uc,base+v*16)==0 for v in range(8))
    assert s.halted is None
    out.update(passed=True,DIN_notes=din,USB_notes=usb,matching_note_pairs=len(on),helpers_host_loaded=True,
      USB_endpoint_submit_is_fixture=True,extra_USB_state_host_initialized=True,physical_port_delivery_verified=False)
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:s.close();Path('outputs/Digitone-E09-synth-both-ports.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
