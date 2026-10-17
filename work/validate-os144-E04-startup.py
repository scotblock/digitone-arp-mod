from pathlib import Path
import sys
mode=sys.argv[1]
s=Path('work/test-os144-fallback-continuous.py').read_text()
s=s.replace('Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx','Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').replace("root=Path('work/os144-fallback-prepared-'+mode)","root=Path('work/os144-E04-loader-startup-'+mode)").replace('Digitone-OS1.44-fallback-continuous-','Digitone-OS1.44E04-startup-')
s=s.replace('def install(m,ev,stage):',"ENTRY=0x47be08a4\npayload=Path('work/os144/fallback-final-payload.bin').read_bytes()\nr['entry']=hex(ENTRY);r['packaged_candidate_without_code_overlays']=True\nr['loader_handoff']='work/os144/E04-loader-handoff.bin'\nr['copy_events']=[];r['copier_stores']=0\ndef install(m,ev,stage):")
s=s.replace("m.ensure(ENTRY);m.load(code,ENTRY);m.install_isa_patches_scoped(code,ENTRY)\n uc.mem_write(0x400ffed0,bytes.fromhex('4ef9')+u32(ENTRY))",'''m.ensure(RAM);m.install_isa_patches_scoped(payload[:1784],RAM);m.install_isa_patches_scoped(payload[2212:],ENTRY)
 assert bytes(uc.mem_read(0x400ffed0,6))==bytes.fromhex('4ef947be08a4')
 def boundary(uc,pc,n,d):
  if pc==0x4029c4b0:assert bytes(uc.mem_read(pc+256,len(payload)))==payload
  else:assert bytes(uc.mem_read(RAM,len(payload)))==payload
  if pc==0x40000568:assert m.ctlregs[2]==0xa50ce100
  r['copy_events'].append({'pc':hex(pc),'CACR':hex(m.ctlregs.get(2,0)),'exact':True})
 for pc in [0x4029c4b0,0x4000053e,0x40000568]:uc.hook_add(UC_HOOK_CODE,boundary,begin=pc,end=pc)
 def store(uc,access,address,size,value,d):
  assert 0x4029c4b0<=uc.reg_read(UC_M68K_REG_PC)<0x4029c50e and not m.ctlregs.get(2,0)&0xa0000000
  r['copier_stores']+=1
 uc.hook_add(UC_HOOK_MEM_WRITE,store,begin=RAM,end=RAM+len(payload)-1)''')
s=s.replace("sp=uc.reg_read(UC_M68K_REG_A7)\n  r['startup_entries']", "sp=uc.reg_read(UC_M68K_REG_A7)\n  assert bytes(uc.mem_read(RAM,len(payload)))==payload\n  r['startup_entries']",1)
s=s.replace("'on_machine':install}","'on_machine':install,'start_from':'work/os144/E04-loader-handoff.bin'}")
s=s.replace("assert r['startup_entries'] and", "assert r['copier_stores']==623 and len(r['copy_events'])==3\n  assert r['startup_entries'] and")
exec(compile(s,'E04-actual-packaged-startup','exec'))
