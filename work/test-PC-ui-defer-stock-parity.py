from pathlib import Path
exec(Path('work/test-PC-ui-defer-overlay.py').read_text().split('\nresults=[]')[0])
checks=[]
def run(route,kind,recursive,overlay):
 m,M,TASK,H,A,P,O,PP,C,app,cbs=fixture(recursive);u=m.uc;RH=H;requested=P;RC=C
 if kind=='ordinary':requested,RH,RC=unrelated(m,O,H)
 if route=='retained':
  call(m,0x401774c0,[O+0x8c,RH],stack_top=RESETSTACK,limit=100000);PH=H+0x80;u.reg_write(UC_M68K_REG_A0,PH);call(m,0x400e43fc,[app,PP],stack_top=RESETSTACK,limit=100000);fn=0x400e6352;args=[M,PH,0]
 else:call(m,0x400e562a,[PP,M],stack_top=RESETSTACK,limit=100000);fn=0x400e47e6;args=[O,RH]
 if overlay:install(m,live=kind!='audio')
 u.mem_write(0x47fdff00,u32(0xdeadbee0)+b''.join(u32(x) for x in args));u.reg_write(UC_M68K_REG_SR,0x201f);u.reg_write(UC_M68K_REG_A7,0x47fdff00);u.emu_start(fn,0xdeadbee0,count=500000);assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0
 node=rd(u,M+20)
 return {'CPU':[u.reg_read(r) for r in REGS],'parent':bytes(u.mem_read(O+0x38,0x64)).hex(),'child':bytes(u.mem_read(requested,0x50)).hex(),'control':bytes(u.mem_read(RC,16)).hex(),'manager':bytes(u.mem_read(M,0x40)).hex(),'node':bytes(u.mem_read(node,16)).hex(),'state':state_of(m),'registry':registry(u,app)}
for route in ['retained','explicit']:
 for kind in ['audio','ordinary']:
  for recursive in [False,True]:
   baseline=run(route,kind,recursive,False);modified=run(route,kind,recursive,True);assert baseline==modified,(route,kind,recursive,[k for k in baseline if baseline[k]!=modified[k]])
   checks.append({'route':route,'kind':kind,'recursive':recursive,'all_CPU_including_CCR_and_observed_state_identical':True});print('PASS stock parity',route,kind,recursive,flush=True)
Path('outputs/Digitone-E04-PC-ui-defer-stock-parity.json').write_text(json.dumps({'PC_only':True,'passed':True,'cases':checks,'limits':['Parity covers compared CPU and state regions; not every memory alias or hardware cache/timing.','Audio comparison uses test-disabled guard; ordinary page comparison uses live guard.']},indent=2))
