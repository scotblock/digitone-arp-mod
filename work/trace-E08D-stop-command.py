from pathlib import Path
s=Path('work/test-E08D-trial-note-lifecycle.py').read_text()
s=s.replace('Digitone-E08D-trial-note-lifecycle.json','Digitone-E08D-stop-command.json')
s=s.replace("record('after_held_Stop');assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]",
    "record('after_held_Stop');s.tap(s.code('STOP'),hold_ms=100,after_ms=300);record('after_second_Stop')")
start=s.index("    phase='sustain_down'");end=s.index('    preserved(s);',start)
s=s[:start]+s[end:]
anchor='def state():'
extra=r'''
from unicorn.m68k_const import UC_M68K_REG_A0
out['task_commands']=[]
def command(u,pc,n,d):
    p=u.reg_read(UC_M68K_REG_A0)
    out['task_commands'].append({'phase':phase,'ms':s.now_ms(),'command':rd(u,p),'words':[hex(rd(u,p+i*4)) for i in range(5)],'state':[rd(u,S+x) for x in [4,8,12,16,280]]})
s.at(0x400f4088,command)
'''
s=s.replace(anchor,extra+'\n'+anchor)
exec(compile(s,'E08D-stop-command','exec'))
