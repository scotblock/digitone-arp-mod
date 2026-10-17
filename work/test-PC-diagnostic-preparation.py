from pathlib import Path
s=Path('work/test-PC-diagnostic-command-exit.py').read_text()
s=s.replace('for diagnostic_entry in [False,True]:','for diagnostic_entry in [True]:').replace('rd(u,0x402296f0)&~0x80000','rd(u,0x402296f0)|0x80000').replace('Digitone-E04-PC-diagnostic-command-exit.json','Digitone-E04-PC-diagnostic-preparation.json')
extra=r'''
def execute_until(m,entry,args,stop,sr=0x231f):
 u=m.uc;stack=0x47fdff00;u.mem_write(stack,u32(0xdeadbee0)+b''.join(u32(x) for x in args));u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,stack)
 hits=[]
 def pause(u,pc,n,d):hits.append(pc);u.emu_stop()
 h=u.hook_add(UC_HOOK_CODE,pause,begin=stop,end=stop);u.emu_start(entry,0xdeadbee0,count=2000000);u.hook_del(h)
 if not hits:
  Path('outputs/Digitone-E04-PC-diagnostic-preparation.json').write_text(json.dumps({'PC_only':True,'completed':False,'stopped_pc':hex(u.reg_read(UC_M68K_REG_PC)),'instruction_budget':2000000,'reason':'Preparation path did not reach reset within isolated execution budget; no subcall stub or fake acknowledgement used.'},indent=2))
  raise SystemExit('Preparation needs a peripheral/scheduler model at '+hex(u.reg_read(UC_M68K_REG_PC)))
 return {r:u.reg_read(r) for r in REGS}
'''
s=s.replace('\nresults=[]',extra+'\nresults=[]',1)
exec(compile(s,'diagnostic-preparation-path','exec'))
