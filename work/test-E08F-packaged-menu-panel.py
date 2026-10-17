"""Native menu checks on startup-copied E08F helpers, no host overlay writes."""
from pathlib import Path
s=Path('work/test-PC-E08E-menu-panel.py').read_text()
s=s.replace("for label in ['stock','corrected']:","for label in ['corrected']:")
for path in ['outputs/Digitone-E08E-PC-path-layout.json','work/os144/E08E-PC-layout-payload.bin',
             'outputs/Digitone-E08E-PC-startup-comparison.json','work/os144/E08E-PC-path-candidate.syx',
             'work/os144/E08E-PC-layout-main.bin']:
    s=s.replace(path,path.replace('E08E','E08F'))
s=s.replace("==r['before']","==r['after']")
s=s.replace("s.m.uc.mem_write(r['base'],data);",'')
s=s.replace('work/PC-menu-panel-','work/PC-menu-F-packaged-')
s=s.replace("'PC-menu-'+label","'PC-menu-F-packaged-'+label")
s=s.replace('outputs/Digitone-E08E-PC-menu-panel.json','outputs/Digitone-E08F-packaged-menu-panel.json')
s=s.replace("'firmware_unchanged':True", "'firmware_unchanged':True,'menu_helpers_host_loaded':False,'overlay_host_writes':False")
s=s.replace("'Corrected helpers overlaid after startup; corrected packaged startup remains separate.'", "'Menu helpers supplied by the packaged native startup copier, verified before panel execution; peripheral/ISA modeling remains.'")
exec(compile(s,'E08F-packaged-native-menu-panel','exec'))
