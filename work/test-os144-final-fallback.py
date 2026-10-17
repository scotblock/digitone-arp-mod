from pathlib import Path
import sys,json,struct
mode=sys.argv[1]
source=Path('work/test-os144-fallback-continuous.py').read_text()
source=source.replace("root=Path('work/os144-fallback-prepared-'+mode)","root=Path('work/os144-fallback-final-'+mode)")
source=source.replace("report=Path('outputs/Digitone-OS1.44-fallback-continuous-'+mode+'.json')","report=Path('outputs/Digitone-OS1.44-fallback-final-'+mode+'.json')")
source=source.replace("def install(m,ev,stage):",'''ENTRY=RAM+len(blob)
assert ENTRY==0x47be08a4
payload=blob+code
assert len(payload)%4==0 and RAM+len(payload)<PTR
Path('work/os144/fallback-final-payload.bin').write_bytes(payload)
STAGE=0x4029c4b0
r['placement']={'entry':hex(ENTRY),'end':hex(RAM+len(payload)),'payload_bytes':len(payload),'fallback_bytes':len(code),'gap_to_pointer':PTR-(RAM+len(payload)),'payload_sha256':hashlib.sha256(payload).hexdigest(),'PC_overlay_only':True}
r['entry']=hex(ENTRY)
r['copy_events']=[];r['copier_stores']=0
def install(m,ev,stage):''')
source=source.replace("m.ensure(ENTRY);m.load(code,ENTRY);m.install_isa_patches_scoped(code,ENTRY)",'''m.ensure(RAM);m.install_isa_patches_scoped(code,ENTRY)
 if stage=='ladder':
  # Change the source and word count; only guest copier stores populate RAM.
  m.load(payload,STAGE+256)
  assert bytes(uc.mem_read(STAGE+12,2))==bytes.fromhex('203c')
  uc.mem_write(STAGE+14,u32(len(payload)//4))
  uc.mem_write(RAM,bytes([0xa5])*len(payload))
 def copied(uc,pc,n,d):
  row={'stage':stage,'pc':hex(pc),'CACR':hex(m.ctlregs.get(2,0)),'ACR0':hex(m.ctlregs.get(4,0))}
  if pc==STAGE:assert bytes(uc.mem_read(STAGE+256,len(payload)))==payload;row['source_exact']=True
  else:assert bytes(uc.mem_read(RAM,len(payload)))==payload;row['destination_exact']=True
  if pc==0x4000053e:assert not m.ctlregs.get(2,0)&0xa0000000
  if pc==0x40000568:assert m.ctlregs.get(2,0)==0xa50ce100 and m.ctlregs.get(4,0)==0x4007e020
  r['copy_events'].append(row)
 for pc in [STAGE,0x4000053e,0x40000568]:uc.hook_add(UC_HOOK_CODE,copied,begin=pc,end=pc)
 def store(uc,access,address,size,value,d):
  assert STAGE<=uc.reg_read(UC_M68K_REG_PC)<STAGE+94
  assert not m.ctlregs.get(2,0)&0xa0000000
  r['copier_stores']+=1
 uc.hook_add(UC_HOOK_MEM_WRITE,store,begin=RAM,end=RAM+len(payload)-1)''')
# The copier-store probe must only cover the initial copy; subsequent execution
# writes context, outside the copied payload, so its range remains immutable.
source=source.replace("r['startup_entries'].append({'stage':stage", "assert bytes(uc.mem_read(RAM,len(payload)))==payload\n  r['startup_entries'].append({'stage':stage")
source=source.replace("assert r['startup_entries'] and", "assert r['copier_stores']==len(payload)//4\n  assert len(r['copy_events'])==3\n  assert r['startup_entries'] and")
exec(compile(source,'final-placement-continuous','exec'))
