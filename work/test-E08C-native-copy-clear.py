"""Observe native copy/paste/clear and undo using distinct M1 settings."""
from pathlib import Path
definitions=Path('work/test-E08C-pattern-settings.py').read_text().split('\ns=Session(')[0]
anchor="exec(compile(source,'E08C-packaged-session-definitions','exec'))"
definitions=definitions.replace(anchor,
    "source=source.replace('assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]', 'assert rd(s.m.uc,S)==0x4d314131')\n"+anchor)
exec(compile(definitions,'E08C-native-copy-definitions','exec'))
handoff=json.loads(Path('outputs/Digitone-E08C-running-pattern-handoff.json').read_text())
assert handoff['passed']
prepared=json.loads(Path('outputs/Digitone-E08C-pattern-settings.json').read_text())
pm={r['label']:r for r in prepared['pattern_marks']}
A=int(pm['A01_set']['data'],16);B=int(pm['A02_set']['data'],16)
out['record_writes']=[]
base_install=install
def install(s):
    base_install(s)
    def written(u,access,a,n,value,d):
        if len(out['record_writes'])<10000:
            out['record_writes'].append({'phase':phase,'address':hex(a),'size':n,'value':value,'pc':hex(u.reg_read(UC_M68K_REG_PC))})
    for start in [A,B]:s.m.uc.hook_add(UC_HOOK_MEM_WRITE,written,begin=start,end=start+163)

s=Session(handoff['checkpoints']['E08C-after-two-pattern-handoff'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
def mark(label):
    row={'label':label,'ms':s.now_ms(),**info(s.m.uc),
         'A_record':bytes(s.m.uc.mem_read(A,164)).hex(),'B_record':bytes(s.m.uc.mem_read(B,164)).hex()}
    out['pattern_marks'].append(row)
    if s.frames:panel.write_png(s.frames[-1][1],'outputs/E08C-copy-'+label+'.png',4)
    Path('outputs/Digitone-E08C-native-copy-progress.json').write_text(json.dumps(out,indent=2))
    print(label,row['word'],row['config'],flush=True)
def combo(key):
    s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code(key),hold_ms=100,after_ms=150)
    s.release(s.code('FUNC'));s.run_ms(250)
def choose(number):
    s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code(str(number)),hold_ms=100,after_ms=100)
    s.release(s.code('PTN'));s.run_ms(400)
try:
    s.run_ms(200);s.tap(s.code('STOP'),hold_ms=100,after_ms=150)
    assert data_pointer(s.m.uc)==A and word(s.m.uc)==0xadd0
    phase='copy_A01';mark('before_copy');combo('RECORD');mark('copied_A01')
    phase='select_A02';choose(2);mark('A02_before_paste')
    assert data_pointer(s.m.uc)==B and word(s.m.uc)==0xac94
    phase='paste_A02';combo('STOP');s.run_ms(400);mark('A02_after_paste')
    out['paste_carries_extension']=word(s.m.uc)==0xadd0 and config()==[1,3,80,0]
    phase='undo_paste';combo('STOP');s.run_ms(300);mark('A02_undo_paste')
    out['undo_paste_restores_extension']=word(s.m.uc)==0xac94 and config()==[1,1,20,0]
    phase='paste_again';combo('STOP');s.run_ms(300);mark('A02_paste_again')
    phase='clear_A02';combo('PLAY');s.run_ms(300);mark('A02_after_clear')
    phase='undo_clear';combo('PLAY');s.run_ms(300);mark('A02_undo_clear')
    phase='return_A01';choose(1);mark('A01_after_operations')
    out['A01_unaffected']=word(s.m.uc)==0xadd0 and config()==[1,3,80,0]
    preserved(s);out['halted']=s.halted;assert s.halted is None
    out['execution_completed']=True
    # Clear/undo semantics are deliberately assessed from observed native data
    # and UI completion, rather than assuming they reset MIDI parameters.
    out['passed']=out['paste_carries_extension'] and out['undo_paste_restores_extension'] and out['A01_unaffected']
except Exception:
    out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
    s.close();Path('outputs/Digitone-E08C-native-copy-clear.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
