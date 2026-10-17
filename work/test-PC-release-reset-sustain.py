from pathlib import Path
source=Path('work/test-PC-input-live-sustain-panel.py').read_text()
source=source.replace('Digitone-E04-PC-input-live-sustain-panel.json','Digitone-E04-PC-release-reset-sustain.json')
source=source.replace("input_manifest=json.loads", "release_manifest=json.loads(Path('work/os144/PC_ONLY-release-reset-overlay.json').read_text());release_code=Path('work/os144/PC_ONLY-release-reset-overlay.bin').read_bytes()\ninput_manifest=json.loads")
anchor="   points={'packet'"
installation="""   if mode!='LIVE_stock_entries':
    s.m.load(release_code,release_manifest['base']);s.m.install_isa_patches_scoped(release_code,release_manifest['base'])
    for h in release_manifest['hooks']:
     assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['stock'],h['name']
     s.m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
"""
assert anchor in source;source=source.replace(anchor,installation+anchor)
source=source.replace("  s.tap(s.code('KEYBOARD')", "  if mode=='LIVE_held_then_closed':\n   assert rd(u,0x47be2840)==0x494e4954 and bytes(u.mem_read(0x419afff4,8))[0]==1\n   assert 'publish' not in r['marks'][-1]['events']\n   u.mem_write(0x47be2840,struct.pack('>I',0x4c495645))\n   send([0xb0|ch,64,0],'release after fixture LIVE resume')\n   assert bytes(u.mem_read(0x419afff4,8))==bytes(8) and all(rd(u,0x419afffc+i*8)==0 for i in range(8))\n   assert 'publish' in r['marks'][-1]['events']\n  s.tap(s.code('KEYBOARD')")
exec(compile(source,'release-reset-sustain','exec'))
