from pathlib import Path
for suffix in ['live-edit-handoff','complete-panel-race']:
    s=Path(f'work/test-E08D-{suffix}.py').read_text().replace('E08D','E08E')
    Path(f'work/test-E08E-{suffix}.py').write_text(s)
Path('work/trace-E08E-panel-race.py').write_text(Path('work/trace-E08D-panel-race.py').read_text().replace('E08D','E08E'))
for suffix in ['complete-panel-race','project-readiness']:
    s=Path(f'work/verify-E08D-{suffix}.py').read_text().replace('E08D','E08E')
    if suffix=='complete-panel-race':
        s=s.replace('c6e2b327af09c46858ab3b902e0a35a0dce5bf355258952c0915983aabfc5099','74219ea223999ae190f5c935973b96bf67eea60148416a1009565af6f48dd3a3')
    if suffix=='project-readiness':
        s=s.replace('This directly tests E08E; E08E adds a Stop/OFF clear and requires its own playback regression.', 'This directly tests the corrected E08E package; asynchronous project-load/input overlap is not certified.')
    Path(f'work/verify-E08E-{suffix}.py').write_text(s)
Path('work/test-E08E-project-readiness.py').write_text(Path('work/test-E08D-project-readiness.py').read_text().replace('E08D','E08E'))
Path('work/audit-E08E-trial-startup-delta.py').write_text(Path('work/audit-E08D-trial-startup-delta.py').read_text().replace('E08D','E08E'))
