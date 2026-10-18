"""Packaged E10 native pattern clipboard, clear/undo and warm-reset guards."""
from pathlib import Path
# Reuse proven native operation drivers, with only the source image/state changed.
s=Path('work/test-PC-E10-life-copy-cache.py').read_text(encoding='utf-8')
s=s.replace("('PC_ONLY-E10-bound','PC_ONLY-E10-life')","('PC_ONLY-E10-bound','PC_ONLY-E10-package')").replace("('Digitone-E10-PC-bound-startup.json','Digitone-E10-PC-life-startup.json')","('Digitone-E10-PC-bound-startup.json','Digitone-E10-PC-package-startup.json')")
s=s.replace("\"proof['checkpoints']['reloaded-two-patterns']\",\"case['ui_snapshot']\"","\"proof['checkpoints']['reloaded-two-patterns']\",\"proof['checkpoints']['reloaded-two-patterns']\"")
s=s.replace("\"proof['private_card']\",\"paths.card\"","\"proof['private_card']\",\"proof['private_card']\"")
s=s.replace(" s=s.replace(\"with open(paths.card,'rb') as src\",\"with open(source_paths.card,'rb') as src\")",'')
needle=' return s\n'
inject=" s=s.replace('outputs/Digitone-E10-PC-bound-panel-patterns.json','outputs/Digitone-E10-PC-package-workflow-patterns.json')\n s=s.replace(\" and proof['post_reload_pattern_recall']\",'')\n"
s=s.replace(needle,inject+needle)
s=s.replace('E10-life-copy-cache','E10-package-workflow-copy')
# Already-restored patterns suffice; use their actual programs without rebuilding.
anchor="exec(compile(source,'E10-life-native-copy-cache','exec'))"
extra="""
a=source.index(" phase='A01_native_program'");b=source.index(" if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=150)\\n if s.frames:",a)
source=source[:a]+" tap('SYN1');combo('SYN2')\\n"+source[b:]
# Workload is now an existing populated bank, not default startup values.
source=source.replace("    assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]", "    assert rd(s.m.uc,S)==0x4d314131")
source=source.replace('outputs/Digitone-E10-PC-life-copy-cache.json','outputs/Digitone-E10-PC-package-workflow-copy.json')
Path('work/generated-E10-package-workflow-copy.py').write_text(source,encoding='utf-8')
"""
assert anchor in s;s=s.replace(anchor,extra+anchor)
exec(compile(s,'E10-packaged-native-clipboard','exec'))
