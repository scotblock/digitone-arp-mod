from pathlib import Path
source=Path('work/test-E08C-packaged-panel-playback.py').read_text().split('\ns = Session(')[0]
exec(compile(source,'E08C-readback-definitions','exec'))
def inspect(s):
    for region in layout['regions']:
        if region['base'] >= 0x47be0000: continue
        start=region['base'];expected=main[start-0x40000400:start-0x40000400+region['bytes']]
        actual=bytes(s.m.uc.mem_read(start,region['bytes']))
        diffs=[{'address':hex(start+i),'expected':a,'actual':b} for i,(a,b) in enumerate(zip(expected,actual)) if a!=b]
        if diffs: print(region['name'], json.dumps(diffs[:32]))
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=inspect)
s.close()
