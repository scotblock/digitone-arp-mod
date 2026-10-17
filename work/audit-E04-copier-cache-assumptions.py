from pathlib import Path
import sys,json,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom
from dt2.container import sections
from capstone import Cs,CS_ARCH_M68K,CS_MODE_M68K_040
handoff=bootrom.load_handoff('work/os144/E04-loader-handoff.bin')
trace=json.loads(Path('outputs/Digitone-OS1.44E04-loader-cache-controls.json').read_text())
payload=Path('work/os144/fallback-final-payload.bin').read_bytes()
ctl=handoff['ctlregs'];assert ctl[2]==0x0008c000 and not ctl[2]&0xa0000000
bootstrap=Path('work/os144/startup-bootstrap-image.bin').read_bytes();base=0x80000400
assert bootstrap[0x80000644-base:0x80000648-base]==bytes.fromhex('4e7b0002')
cs=Cs(CS_ARCH_M68K,CS_MODE_M68K_040)
code=[{'pc':hex(i.address),'mnemonic':i.mnemonic,'operand':i.op_str,'bytes':i.bytes.hex()} for i in cs.disasm(bootstrap[0x80000634-base:0x80000654-base],0x80000634)]
# Narrow logical sensitivity model. Copyback dirty bytes are deliberately
# separate from RAM; invalidating them is not equivalent to pushing them.
def copied_ram(data_cache,copyback,invalidate=True,push=False):
 ram=b'\xa5'*len(payload);dirty=None
 if data_cache and copyback:dirty=payload
 else:ram=payload
 if push and dirty is not None:ram=dirty;dirty=None
 if invalidate:dirty=None
 return ram==payload
cases=[{'name':'observed_loader_data_cache_off','code_bytes_in_RAM_after_invalidate':copied_ram(False,False)},
       {'name':'hypothetical_data_cache_on_write_through','code_bytes_in_RAM_after_invalidate':copied_ram(True,False)},
       {'name':'hypothetical_data_cache_on_copyback_no_push','code_bytes_in_RAM_after_invalidate':copied_ram(True,True)},
       {'name':'hypothetical_copyback_with_push_before_invalidate','code_bytes_in_RAM_after_invalidate':copied_ram(True,True,push=True)}]
assert [x['code_bytes_in_RAM_after_invalidate'] for x in cases]==[True,True,False,True]
r={'PC_only':True,'hardware_measured':False,'inherited_controls':{hex(k):hex(v) for k,v in ctl.items()},
   'loader_cache_writes':trace['CACR_writes'],'loader_instruction_window':code,'instruction_window_source':'decoded section 2 bootstrap at 80000400; not section 4 updater occupying the same SRAM later',
   'source':{'start':'0x4029c5b0','end':hex(0x4029c5b0+len(payload)),'aligned_longword':True},
   'destination':{'start':'0x47be0000','end':hex(0x47be0000+len(payload)),'aligned_longword':True},
   'metadata_cleared':{'start':'0x47be1000','end':'0x47be1b74'},
   'inherited_D_enable':bool(ctl[2]&0x80000000),'inherited_store_buffer_enable':bool(ctl[2]&0x20000000),
   'inherited_I_enable':bool(ctl[2]&0x8000),'post_copy_control':'0xa50ce100',
   'logical_sensitivity':cases,'passed':True,
   'limits':['Logical sensitivity only; hypothetical copyback entry is not observed hardware state.','No new physical DDR/cache/pipeline visibility evidence.','Missing ACR entries in the saved handoff are not proof of physical zero.','Capstone names control registers using generic m68k conventions; ColdFire register indexes and raw opcodes govern interpretation.']}
Path('outputs/Digitone-E04-copier-cache-assumption-checks.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
