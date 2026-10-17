from pathlib import Path

for suffix in ['packaged-panel-playback','pattern-settings','running-pattern-handoff']:
    text=Path(f'work/test-E08C-{suffix}.py').read_text().replace('E08C','E08D')
    if suffix=='pattern-settings':
        text=text.replace("'held':[rd(u,S+x) for x in [8,12,16,280]]}",
            "'held':[rd(u,S+x) for x in [8,12,16,280]], 'owner':hex(rd(u,S+336)), 'request_owner':hex(rd(u,S+340)), 'stock_kit':hex(rd(u,0x419c5b10)), 'stock_cache':hex(rd(u,0x419c5b14))}")
    Path(f'work/test-E08D-{suffix}.py').write_text(text)
