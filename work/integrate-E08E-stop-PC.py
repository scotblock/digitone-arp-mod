from pathlib import Path
s=Path('work/integrate-E08D-owner-PC.py').read_text().replace('E08D','E08E')
# Assemble on the unchanged C baseline, as D did, retaining its exact init
# update. E helpers include the prior D owner guards and the added Stop bridge.
s=s.replace("main[base['copy_source']-MB:]=payload", "\nfor h in c['hooks']:\n    if h['site']==0x400f4aec:\n        off=h['site']-MB;assert main[off:off+h['length']].hex()==h['original']\n        main[off:off+h['length']]=bytes.fromhex(h['replacement'])\n        base['hooks'].append(h);full['hooks'].append(h)\nmain[base['copy_source']-MB:]=payload")
exec(compile(s,'E08E-PC-stop-layout','exec'))
