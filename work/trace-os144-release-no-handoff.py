from pathlib import Path
source=Path('work/trace-os144-release-branches.py').read_text().split("exec(compile(s,'trace-release-branches','exec'))")[0]
exec(compile(source,'build-no-handoff-control','exec'))
s=s.replace('Digitone-OS1.44-release-branches.json','Digitone-OS1.44-release-no-handoff.json')
needle="session.press(session.code('PTN'));session.run_ms(100);session.tap(session.code('1'),hold_ms=100,after_ms=100);session.release(session.code('PTN'));session.run_ms(200);mark('request 1')"
assert needle in s;s=s.replace(needle,"session.run_ms(500);mark('same-pattern control')",1)
begin=s.index(" if not r['actual_playing_handoff']:");end=s.index(" mark('confirmed handoff or bounded failure')",begin)
s=s[:begin]+s[end:]
s=s.replace('range(32)','range(16)').replace("session.run_ms(2500);mark('delayed source observation after handoff')","mark('same-pattern delayed source observation')")
s=s.replace("'functional session", "'functional session")
exec(compile(s,'stock-no-handoff-control','exec'))
