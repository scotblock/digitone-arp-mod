"""M1 panel configuration and MIDI playback from the packaged startup state.

No helper bytes, hooks, settings words or M1 initialization are host-written.
The inherited emulator input-gate fixture is disclosed separately.
"""
from pathlib import Path
import sys, os, json, struct, traceback, hashlib
sys.path[:0] = ['work/emulator-deps', 'work/upstream/digiemu']
from emu import bootstrap as bs, longrun, midi, panel
from emu.session import Session
from emu.dtim import Dtims

original = longrun.build
def build(*args, **kwargs):
    kwargs['unblock'] = False
    return original(*args, **kwargs)
longrun.build = build
folder = Path('work/os144')
layout = json.loads(Path('outputs/Digitone-E08D-PC-path-layout.json').read_text())
native = json.loads((folder/'E08D-PC-install-layout.json').read_text())
case = json.loads(Path('outputs/Digitone-E08D-PC-startup-comparison.json').read_text())['cases'][0]
syx = Path(layout['candidate'])
paths = bs.FirmwarePaths(str(Path(case['ui_snapshot']).parents[2]), syx.name,
                        str(Path('work/upstream/digiemu/devices').resolve()))
os.environ.update(paths.env())
payload = (folder/'E08D-PC-layout-payload.bin').read_bytes()
main = (folder/'E08D-PC-layout-main.bin').read_bytes()
phase = 'setup'
out = {'PC_only': True, 'helpers_host_loaded': False, 'hooks_host_patched': False,
       'M1_initializer_host_called': False, 'settings_host_written': False,
       'candidate_sha256': hashlib.sha256(syx.read_bytes()).hexdigest(),
       'startup_snapshot': case['ui_snapshot'], 'wire': [], 'marks': [],
       'samples': [], 'failure': None}
rd = lambda u, a: int.from_bytes(u.mem_read(a, 4), 'big')
S = native['state']

def preserved(s):
    for region in layout['regions']:
        data, base = (main, 0x40000400) if region['base'] < 0x47be0000 else (payload, 0x47be0000)
        expected = data[region['base']-base:region['base']-base+region['bytes']]
        actual = bytes(s.m.uc.mem_read(region['base'],region['bytes']))
        if region['name'] == 'copier':
            # This appended MAIN source area is reclaimed during stock startup.
            # Its execution/copy was checked before reclamation by the startup
            # test. It is not a resident playback routine.
            assert actual == bytes(region['bytes']), 'unexpected copier source contents'
            out['startup_copier_source_reclaimed'] = True
            continue
        assert actual == expected, region['name']
    for region in native['data_regions']:
        assert bytes(s.m.uc.mem_read(region['base'],region['bytes'])) == payload[region['base']-native['base']:region['base']-native['base']+region['bytes']], region['name']
    for hook in native['hooks']:
        assert bytes(s.m.uc.mem_read(hook['site'],hook['length'])).hex() == hook['replacement'], hook

def install(s):
    preserved(s)
    for region in layout['regions']:
        if region['base'] >= 0x47be0000:
            s.m.install_isa_patches_scoped(payload[region['base']-0x47be0000:region['base']-0x47be0000+region['bytes']], region['base'])
    assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]
    mo = midi.MidiOut(lambda data: out['wire'].append({'phase':phase,'ms':s.now_ms(),'bytes':list(data)}))
    mo.install(s.m); mo.attach(s.m,s.ips)
    s.sources = s.sources+(mo,)
    s.midi_mirror_observer = mo

s = Session(case['ui_snapshot'], syx=str(syx), ddr=0x8000000, audio=True, on_machine=install)

def config(): return [rd(s.m.uc,S+x) for x in [4,304,308,320]]
def settings_word():
    root = rd(s.m.uc,0x419f0de0)
    data = rd(s.m.uc,root+0xff8+16)
    return int.from_bytes(s.m.uc.mem_read(data+158,2),'big')
def mark(label):
    out['marks'].append({'label':label,'ms':s.now_ms(),'config':config(),
                         'settings_word':settings_word(),
                         'state':[rd(s.m.uc,S+x) for x in [8,16,280]]})
    print(label, config(), flush=True)
def page():
    s.press(s.code('FUNC')); s.run_ms(100)
    s.tap(s.code('SYN2'),hold_ms=100,after_ms=200)
    s.release(s.code('FUNC'));s.run_ms(150)
def sample(label, ms=1000):
    global phase
    phase = label
    start, clock, count = s.now_ms(), rd(s.m.uc,0x80004614), len(out['wire'])
    s.run_ms(ms)
    out['samples'].append({'phase':label,'begin_ms':start,'end_ms':s.now_ms(),
                          'clock_delta':(rd(s.m.uc,0x80004614)-clock)&0xffffffff,
                          'interval_units':rd(s.m.uc,S+32),'gate_units':rd(s.m.uc,S+36),
                          'wire':out['wire'][count:]})
    mark(label)

try:
    if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
        timer=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False)
        timer.now=s.pits.now;s.pits.sources=s.pits.sources+(timer,)
    for _ in range(10):
        s.run_ms(1000)
        if s.ev['dsplink'].booted and s.ev['dsplink'].renders>100: break
    mark('warm')
    s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
    s.press(s.code('MIDI'));s.tap(s.code('T1'),hold_ms=100,after_ms=100)
    s.release(s.code('MIDI'));s.run_ms(200)
    s.tap(s.code('SYN1'),hold_ms=100,after_ms=100)
    s.press(s.code('FUNC'));s.tap(s.code('A'),hold_ms=100,after_ms=100)
    s.release(s.code('FUNC'));s.run_ms(200)
    mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
    gate=rd(s.m.uc,0x41368d64)
    s.m.uc.mem_write(0x41368d64,struct.pack('>I',gate|3))
    channel=rd(s.m.uc,0x41368d2c)&15
    out['input_gate_fixture']={'before':gate,'after':gate|3}
    out['auto_channel']=channel+1
    def send(data):
        for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*.00032,byte)
        mi.received+=len(data);s.run_ms(60)
    chord=[0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100]
    release=[0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]
    phase='OFF_chord';begin=len(out['wire']);send(chord);s.run_ms(200);send(release);s.run_ms(200)
    out['OFF_wire']=out['wire'][begin:];assert config()==[0,2,50,0];mark('OFF_chord')
    phase='panel_UP';page()
    s.turn(1,16,after_ms=300);s.turn(2,16,after_ms=300);s.turn(3,16,after_ms=300)
    assert settings_word()==0xadd0 and config()==[1,3,80,0],(settings_word(),config())
    if s.frames:panel.write_png(s.frames[-1][1],'outputs/E08D-packaged-M1-controls.png',4)
    mark('panel_UP_1_32_gate80');s.tap(s.code('NO'),hold_ms=100,after_ms=200)
    phase='UP_start';send(chord);s.run_ms(200)
    sample('UP_1_32_gate80')
    s.tap(s.code('TEMPO'),hold_ms=70,after_ms=150)
    s.turn(s.encoder('9'),400,after_ms=400);sample('tempo_plus400_1_32')
    s.turn(s.encoder('9'),-800,after_ms=400);sample('tempo_minus800_1_32')
    phase='release_first';out['first_release_ms']=s.now_ms();send(release);s.run_ms(350)
    assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]
    mark('released_first')
    s.tap(s.code('NO'),hold_ms=100,after_ms=200)
    phase='panel_1_16';page();s.turn(2,-16,after_ms=300);s.turn(3,-16,after_ms=300)
    assert settings_word()==0xad32 and config()==[1,2,50,0],(settings_word(),config())
    mark('panel_UP_1_16_gate50');s.tap(s.code('NO'),hold_ms=100,after_ms=200)
    phase='UP_second';send(chord);s.run_ms(200);sample('UP_1_16_gate50')
    phase='release_second';out['last_release_ms']=s.now_ms();send(release);s.run_ms(350)
    s.tap(s.code('STOP'),hold_ms=100,after_ms=200);mark('final_stop')
    out['final_state']=[rd(s.m.uc,S+x) for x in [8,16,280]]
    assert out['final_state']==[0,0,0]
    preserved(s);out['code_and_tables_preserved']=True
    out['MIDI_received']=mi.received;out['MIDI_delivered']=mi.delivered
    out['halted']=s.halted;assert s.halted is None
    out['passed']=True
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
    s.close()
    Path('outputs/Digitone-E08D-packaged-panel-playback.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
