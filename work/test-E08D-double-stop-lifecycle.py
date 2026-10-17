from pathlib import Path
s=Path('work/test-E08D-trial-note-lifecycle.py').read_text()
s=s.replace("record('after_held_Stop');assert [rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]",
            "record('after_held_Stop');s.tap(s.code('STOP'),hold_ms=100,after_ms=300);record('after_second_Stop');out['second_Stop_cleared_held']=[rd(s.m.uc,S+x) for x in [8,16,280]]==[0,0,0]")
s=s.replace('Digitone-E08D-trial-note-lifecycle.json','Digitone-E08D-double-stop-lifecycle.json')
exec(compile(s,'E08D-double-stop-lifecycle','exec'))
