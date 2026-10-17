"""Repeat warm/diagnostic guard checks with populated bank/clipboard/cache."""
from pathlib import Path
source=Path('work/test-PC-E10-bound-reset-refusal.py').read_text(encoding='utf-8')
anchor="exec(compile(definitions,'E10-reset-definitions','exec'))"
changes=[('PC_ONLY-E10-bound','PC_ONLY-E10-life'),('Digitone-E10-PC-bound-startup.json','Digitone-E10-PC-life-startup.json'),("['E10_persistence_metadata','E10_pattern_binding_metadata']","['E10_persistence_metadata','E10_pattern_binding_metadata','E10_lifecycle_metadata']")]
injection=''.join('definitions=definitions.replace('+repr(a)+','+repr(b)+')\n' for a,b in changes)
old="    assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]"
new="    assert rd(s.m.uc,S)==0x4d314131"
inner="exec(compile(prefix,'E10-bound-panel-definitions','exec'))"
replacement='prefix=prefix.replace('+repr(old)+','+repr(new)+')\n'+inner
injection+='definitions=definitions.replace('+repr(inner)+','+repr(replacement)+')\n'
assert anchor in source;source=source.replace(anchor,injection+anchor)
source=source.replace('outputs/Digitone-E10-PC-bound-panel-patterns.json','outputs/Digitone-E10-PC-life-copy-cache.json').replace("proof['checkpoints']['reloaded-two-patterns']","proof['unsaved_snapshot']").replace("bank==b''.join(bytes.fromhex(x) for x in proof['expected_records'])","bank==bytes.fromhex(proof['expected_bank'])[:64]")
source=source.replace("(0x41392fa4,4)]","(0x41392fa4,4),(0x40555ee4,0x2a7514)]")
source=source.replace('outputs/Digitone-E10-PC-bound-reset-refusal.json','outputs/Digitone-E10-PC-life-reset-refusal.json')
exec(compile(source,'E10-life-reset-guards','exec'))
