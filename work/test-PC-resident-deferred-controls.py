from pathlib import Path
s=Path('work/test-PC-deferred-release-controls.py').read_text().replace('PC_ONLY-deferred-release-overlay','PC_ONLY-resident-deferred-release-overlay').replace('Digitone-E04-PC-deferred-release-controls.json','Digitone-E04-PC-resident-deferred-controls.json')
s=s.replace("m.ensure(defer_cfg['count']);m.uc.mem_write(defer_cfg['count'],bytes(defer_cfg['storage_bytes']))", "m.ensure(defer_cfg['count']);assert bytes(m.uc.mem_read(defer_cfg['count'],defer_cfg['storage_bytes']))==bytes(defer_cfg['storage_bytes'])")
exec(compile(s,'resident-deferred-controls','exec'))
