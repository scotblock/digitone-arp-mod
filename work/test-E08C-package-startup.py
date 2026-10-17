from pathlib import Path
import sys

mode = sys.argv[1]
scripts = {'copy': 'test-E08-PC-copier-initialization.py',
           'loader': 'test-E08-packed-loader.py',
           'startup': 'test-E08-loader-startup.py'}
source = Path('work', scripts[mode]).read_text().replace('E08', 'E08C')
if mode == 'copy':
    source = source.replace(
        "  if pc in [cfg['bootstrap'],cfg['entries']['init'],cfg['entries']['configure']]:seen.append(hex(pc))",
        "  if pc in [cfg['bootstrap'],cfg['entries']['init'],cfg['entries']['configure']]:seen.append(hex(pc))\n"
        "  if label=='cold' and pc==cfg['entries']['init']:uc.mem_write(cfg['state']+312,b'\\xa7'*24)")
    source = source.replace(' rows.append(',
        " assert bytes(u.mem_read(cfg['state']+312,24))==bytes(24)\n rows.append(")
    source = source.replace("'exact_native_code_copy':True", "'exact_native_code_copy':True,'settings_tail_zeroed':True,'poisoned_before_native_init':label=='cold'")
exec(compile(source, f'E08C-packaged-{mode}', 'exec'))
