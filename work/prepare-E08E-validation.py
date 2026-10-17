from pathlib import Path
for suffix in ['packaged-panel-playback','pattern-settings','running-pattern-handoff','trial-note-lifecycle']:
    source=Path(f'work/test-E08D-{suffix}.py').read_text().replace('E08D','E08E')
    Path(f'work/test-E08E-{suffix}.py').write_text(source)
