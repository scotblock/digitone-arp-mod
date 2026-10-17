"""Native panel routes on stock and corrected E08E, isolated emulator cards."""
from pathlib import Path
import sys,os,json,struct,traceback,shutil
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,longrun,panel,sparse
from emu.session import Session
from emu.dtim import Dtims
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_A7,UC_M68K_REG_PC
original_build=longrun.build
def build(*a,**k):k['unblock']=False;return original_build(*a,**k)
longrun.build=build
fix=json.loads(Path('work/os144/PC_ONLY-E08E-menu-fix-layout.json').read_text())
layout=json.loads(Path('outputs/Digitone-E08E-PC-path-layout.json').read_text())
payload=Path('work/os144/E08E-PC-layout-payload.bin').read_bytes()
rd=lambda u,a:int.from_bytes(u.mem_read(a,4),'big')
def selection(u):
    root=rd(u,0x419f0de0);data=rd(u,root+0x30+16)
    return rd(u,data+8)
report={'PC_only':True,'firmware_unchanged':True,'cases':[],'limits':['Emulated panel/peripherals and saved emulator state, not physical hardware.','Corrected helpers overlaid after startup; corrected packaged startup remains separate.']}
for label in ['stock','corrected']:
    oldcase=next(x for x in json.loads(Path('outputs/Digitone-E07-PC-startup-comparison.json').read_text())['cases'] if x['image']=='stock_restored') if label=='stock' else json.loads(Path('outputs/Digitone-E08E-PC-startup-comparison.json').read_text())['cases'][0]
    syx=Path('outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx' if label=='stock' else 'work/os144/E08E-PC-path-candidate.syx').resolve()
    baseline=Path(oldcase['ui_snapshot']).parents[2]
    root=Path('work/PC-menu-panel-'+label).resolve();root.mkdir(exist_ok=True)
    paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()))
    if (baseline/'devices').exists():shutil.copytree(baseline/'devices',root/'devices',dirs_exist_ok=True)
    Path(paths.sections).mkdir(parents=True,exist_ok=True)
    Path(paths.sections,'section_7_BLOB.bin').write_bytes(Path('work/os144/section-7-stored.bin').read_bytes())
    Path(paths.main_img).write_bytes(Path('work/os144/section-3.bin' if label=='stock' else 'work/os144/E08E-PC-layout-main.bin').read_bytes())
    with (baseline/'plusdrive.img').open('rb') as src,Path(paths.card).open('wb') as dst:
        sparse.make_sparse(dst);sparse.extend(dst,(baseline/'plusdrive.img').stat().st_size)
        while b:=src.read(1024*1024):
            if b.strip(b'\0'):dst.seek(src.tell()-len(b));dst.write(b)
    os.environ.update(paths.env())
    row={'label':label,'page_calls':[],'marks':[],'tag_writes':[]};report['cases'].append(row);phase='warm'
    def install(s):
        if label=='corrected':
            for r in layout['regions']:
                if r['base']>=0x47be0000:s.m.install_isa_patches_scoped(payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']],r['base'])
            for r in fix['regions']:
                assert bytes(s.m.uc.mem_read(r['base'],r['span'])).hex()==r['before']
                data=bytes.fromhex(r['after']);s.m.uc.mem_write(r['base'],data);s.m.install_isa_patches_scoped(data[:r['bytes']],r['base'])
        def called(u,pc,n,d):
            sp=u.reg_read(UC_M68K_REG_A7)
            row['page_calls'].append({'phase':phase,'index':rd(u,sp+8),'selected':selection(u)})
        s.at(0x4003f13e,called)
        def written(u,access,addr,size,value,d):
            if value==0x4d314352 and size==4:row['tag_writes'].append({'phase':phase,'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(addr),'selected':selection(u)})
        s.m.uc.hook_add(UC_HOOK_MEM_WRITE,written,begin=0x40000000,end=0x47ffffff)
    s=Session(oldcase['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=False,on_machine=install)
    def mark(name):
        p=Path('outputs')/('PC-menu-'+label+'-'+name+'.png')
        if s.frames:panel.write_png(s.frames[-1][1],str(p),4)
        row['marks'].append({'phase':name,'selected':selection(s.m.uc),'screen':str(p)})
        print(label,name,selection(s.m.uc),flush=True)
    def select(track):
        want_midi=track>=4
        if (selection(s.m.uc)>=4)!=want_midi:s.tap(s.code('MIDI'),hold_ms=80,after_ms=150)
        s.tap(s.code('T'+str(track%4+1)),hold_ms=80,after_ms=150)
        assert selection(s.m.uc)==track
    def combo(key):
        s.press(s.code('FUNC'));s.run_ms(80);s.tap(s.code(key),hold_ms=80,after_ms=150);s.release(s.code('FUNC'));s.run_ms(150)
    try:
        if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
            t=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);t.now=s.pits.now;s.pits.sources=s.pits.sources+(t,)
        s.run_ms(800);s.tap(s.code('STOP'),hold_ms=80,after_ms=100)
        for track in [4,5,0]:
            select(track)
            for key in ['TRIG','SYN1','SYN2','FLTR','AMP','LFO']:
                phase=str(track)+'-'+key;s.tap(s.code(key),hold_ms=80,after_ms=180);mark(phase)
        for track,key in [(0,'SYN1'),(5,'SYN2'),(4,'SYN2')]:
            select(track);phase=str(track)+'-SYN1-reset'
            s.tap(s.code('SYN1'),hold_ms=80,after_ms=150)
            phase=str(track)+'-FUNC-'+key;combo(key);mark(phase)
            s.tap(s.code('NO'),hold_ms=80,after_ms=120)
        select(4);phase='4-SYN1-after-custom';s.tap(s.code('SYN1'),hold_ms=80,after_ms=150);mark(phase)
        select(0);phase='0-FUNC-SYN1-after-custom';combo('SYN1');mark(phase)
        s.tap(s.code('NO'),hold_ms=80,after_ms=120)
        for entry in row['page_calls']:
            if '-FUNC-' not in entry['phase'] and entry['phase']!='warm':
                key=entry['phase'].split('-')[1]
                assert entry['index']==['TRIG','SYN1','SYN2','FLTR','AMP','LFO'].index(key),entry
        assert not row['tag_writes'] if label=='stock' else row['tag_writes'] and all(x['phase']=='4-FUNC-SYN2' and x['selected']==4 for x in row['tag_writes']),row['tag_writes']
        assert s.halted is None
        row['passed']=True
    except Exception:
        row['passed']=False;row['failure']=traceback.format_exc();print(row['failure'],flush=True)
    finally:
        s.close();Path('outputs/Digitone-E08E-PC-menu-panel.json').write_text(json.dumps(report,indent=2))
report['passed']=all(x.get('passed') for x in report['cases'])
Path('outputs/Digitone-E08E-PC-menu-panel.json').write_text(json.dumps(report,indent=2))
if not report['passed']:raise SystemExit(1)
