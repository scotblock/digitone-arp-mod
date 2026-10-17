from pathlib import Path
import sys,json,hashlib,struct,collections
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import cfisa
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.m68k_const import *
main=Path('work/os144/emulator-E04-main.bin').read_bytes()
payload=Path('work/os144/fallback-final-payload.bin').read_bytes()
port=json.loads(Path('work/os144/helper-port.json').read_text())
def move_restriction(w):
 line=w>>12
 if line not in [1,2,3]:return None
 sm,sr=(w>>3)&7,w&7;dm,dr=(w>>6)&7,(w>>9)&7
 # CFPRM rev 3, page 4-48: source/destination combination table.
 # ISA_B/C allow immediate BYTE/WORD to d16, not longword.
 if sm==5 or (sm==7 and sr==2):
  forbidden=dm==6 or (dm==7 and dr in [0,1])
 elif sm==6 or (sm==7 and sr in [0,1,3,4]):
  forbidden=dm in [5,6] or (dm==7 and dr in [0,1])
  if sm==7 and sr==4 and dm==5 and line in [1,3]:forbidden=False
 else:forbidden=False
 return {'reason':'MOVE source/destination combination excluded by CFPRM 4-48','source_mode':sm,'source_register_field':sr,'destination_mode':dm,'destination_register_field':dr} if forbidden else None
regions=[('copier',0x4029c4b0,94,main,0x40000400),('startup_fallback',0x47be08a4,280,payload,0x47be0000)]+[(n,v['address'],v['size'],payload,0x47be0000) for n,v in port['layout'].items()]
out={'PC_only':True,'target':'MCF5441x V4 ISA_C; firmware-target identification retained from prior DDR/boot audit, not a new physical chip readback','manuals':['https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf','https://www.nxp.com/docs/en/reference-manual/CFPRM.pdf'],'scope':'Whole custom code layout plus real copier extent; lookup table and copier zero-padding excluded. All fallback branches inspected statically.','regions':[],'unsupported':[],'emulator_controls':[]}
for name,pc,length,data,base in regions:
 end=pc+length;rows=[]
 while pc<end:
  ins=cfisa.decode(lambda off:int.from_bytes(data[pc-base+off:pc-base+off+2],'big'),pc)
  assert ins.length>0 and pc+ins.length<=end,(name,hex(pc),ins)
  raw=data[pc-base:pc-base+ins.length];w=int.from_bytes(raw[:2],'big');bad=move_restriction(w)
  row={'pc':hex(pc),'bytes':raw.hex(),'length':ins.length,'op':ins.op,'size':ins.size,'flags':ins.flags,'privileged':bool(ins.flags&cfisa.PRIV),'local_decoder_illegal':bool(ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF))}
  if row['local_decoder_illegal']:out['unsupported'].append({'region':name,**row,'reason':'Existing decoder flag'})
  if bad:out['unsupported'].append({'region':name,**row,**bad})
  rows.append(row);pc+=ins.length
 out['regions'].append({'name':name,'start':hex(end-length),'end':hex(end),'instructions':rows})
assert len(out['unsupported'])==5
assert [x['pc'] for x in out['unsupported']]==['0x4029c4e0','0x4029c4ea','0x4029c4f4','0x4029c4fe','0x47be0998']
def engine():
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_CFV4E);u.reg_write(UC_M68K_REG_SR,0x2700);return u
for strict in [False,True]:
 u=engine();u.mem_map(0x4029c000,4096);u.mem_write(0x4029c4b0,main[0x4029c4b0-0x40000400:]);u.mem_map(0x47be0000,8192)
 hits=[]
 def guard(uc,pc,size,data):
  if strict:
   bad=move_restriction(int.from_bytes(uc.mem_read(pc,2),'big'))
   if bad:hits.append({'pc':hex(pc),**bad});uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,guard)
 u.emu_start(0x4029c4b0,0x40001df4,count=10000)
 pc=u.reg_read(UC_M68K_REG_PC);header=bytes(u.mem_read(0x47be1000,16))
 assert bytes(u.mem_read(0x47be0000,len(payload)))==payload
 if strict:assert pc==0x4029c4e0 and header==bytes(16) and len(hits)==1
 else:assert pc==0x40001df4 and header.hex()=='47bccf04534c43320000000200000b70'
 out['emulator_controls'].append({'name':'copier_with_documented_MOVE_guard' if strict else 'copier_permissive_V4e','pc':hex(pc),'payload_copied_exact':True,'metadata_header':header.hex(),'guard_hits':hits})
# Isolated instruction examples only: do not alter MAIN or package code.
for row in out['unsupported']:
 raw=bytes.fromhex(row['bytes']);value=int.from_bytes(raw[2:6],'big');destination=int.from_bytes(raw[6:10],'big')
 for legal in [False,True]:
  code=(bytes.fromhex('203c')+struct.pack('>I',value)+bytes.fromhex('23c0')+struct.pack('>I',destination)) if legal else raw
  u=engine();u.mem_map(0x50000000,4096);u.mem_write(0x50000000,code);u.mem_map(0x47be1000,4096)
  pc=0x50000000
  while pc<0x50000000+len(code):
   ins=cfisa.decode(lambda off:int.from_bytes(code[pc-0x50000000+off:pc-0x50000000+off+2],'big'),pc)
   bad=move_restriction(int.from_bytes(code[pc-0x50000000:pc-0x50000000+2],'big'))
   assert bool(bad)==(not legal);pc+=ins.length
  u.emu_start(0x50000000,0x50000000+len(code),count=10)
  assert int.from_bytes(u.mem_read(destination,4),'big')==value
  out['emulator_controls'].append({'name':'register_mediated_store_example' if legal else 'unsupported_store_accepted_by_V4e','original_site':row['pc'],'bytes':code.hex(),'destination':hex(destination),'stored_value':hex(value),'instruction_compatibility_check':legal,'scratch_register':'D0; example only, no claim of insertion-point preservation'})
trace=json.loads(Path('outputs/Digitone-E04-restored-capture-control-checks.json').read_text())['cases'][0]
pcs={int(i['pc'],16) for c in trace['producer_calls'] for i in c['isolated_replay']['instructions']}
out['restored_producer_executed_PC_count']=len(pcs)
out['restored_producer_unsupported_MOVE_hits']=[]
for pc in sorted(pcs):
 data,base=(payload,0x47be0000) if 0x47be0000<=pc<0x47be09bc else (main,0x40000400)
 if move_restriction(int.from_bytes(data[pc-base:pc-base+2],'big')):out['restored_producer_unsupported_MOVE_hits'].append(hex(pc))
assert not out['restored_producer_unsupported_MOVE_hits']
out['firmware_sha256']=hashlib.sha256(Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').read_bytes()).hexdigest()
assert out['firmware_sha256']=='76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c'
out['limits']=['Strict guard is software enforcement of the documented MOVE rule, not a silicon exception trace.','Opcode validity is separate from cache, privilege, memory backing and timing.','Existing cfisa decoder misses combined MOVE addressing restrictions; absence of its illegal flag alone is insufficient.','No complete corrected bootstrap, relocated fallback or installable firmware is produced.','Physical fault PC is unknown; the earliest unsupported copier instruction is a plausible cause, not a confirmed physical diagnosis.']
Path('outputs/Digitone-E04-startup-instruction-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print('Unsupported encodings:',[(x['region'],x['pc'],x['bytes']) for x in out['unsupported']])
print('Copier controls:',out['emulator_controls'][:2])
