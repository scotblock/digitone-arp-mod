from pathlib import Path
s=Path('work/test-E08-M1-tempo-playback.py').read_text()
s=s.replace('E07-PC-candidate.syx','E08-PC-path-candidate.syx').replace('Digitone-E07-PC-startup-comparison.json','Digitone-E08-PC-startup-comparison.json').replace("=='E07_restored'","=='E08_restored'").replace('Digitone-E07-PC-candidate-layout.json','Digitone-E08-PC-path-layout.json').replace('E07-PC-payload.bin','E08-PC-layout-payload.bin')
a=s.index(" for address in [native['base']");z=s.index(' def queue_observe',a)
s=s[:a]+''' for r in native['regions']+native['data_regions']:
  expected=native_blob[r['base']-native['base']:r['base']-native['base']+r['bytes']]
  assert bytes(s.m.uc.mem_read(r['base'],r['bytes']))==expected,r['name']
 for h in native['hooks']:assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['replacement']
 assert [rd(s.m.uc,native['state']+x) for x in [0,4,304,308]]==[0x4d314131,0,2,50]
 out['helpers_host_loaded']=False;out['loader_startup_state_verified']=True
''' + s[z:]
s=s.replace('Digitone-E08-M1-tempo-playback.json','Digitone-E08-loader-playback.json')
s=s.replace("'firmware_unchanged':True","'firmware_unchanged':True,'native_packaged_path':True")
exec(compile(s,'E08-packaged-loader-playback','exec'))
