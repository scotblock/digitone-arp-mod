"""Synthetic cut after the first actual 32-KB shutdown command.
Uses the actual stock cold selector/reader; no firmware patch or writer call.
"""
from pathlib import Path
import json,struct,sys
proof_auto=json.loads(Path('outputs/Digitone-E10-PC-auto-powerfail.json').read_text());assert proof_auto['passed']
cut_bytes=int(sys.argv[1],0) if len(sys.argv)>1 else 0x8000
suffix='' if cut_bytes==0x8000 else '-'+str(cut_bytes)
post_card=proof_auto['card'];pending=proof_auto['pending_bank'];selected=proof_auto['selected_bank']
source=Path('work/test-PC-E10-auto-powerfail.py').read_text(encoding='utf-8').split('from emu.intfrc import ForcedInterrupts')[0]
source=source.replace('work/E10-auto-powerfail','work/E10-powerfail-cut-first-command'+suffix)
anchor="s=Session(snapshot"
insert="""
# Failure fixture: only the prefix completed before power disappeared. Bytes
# come from the actual successful transfer; the old bank is left untouched.
dest=[0xf400000,0xf800000][pending]
with open(post_card,'rb') as f:f.seek(dest);prefix=f.read(cut_bytes)
with open(paths.card,'r+b') as f:f.seek(dest);f.write(prefix)
"""
assert anchor in source;source=source.replace(anchor,insert+anchor)
exec(compile(source,'E10-cut-card-reader-fixture','exec'))
from emu.harness import call
from unicorn.m68k_const import UC_M68K_REG_PC
r=dict(PC_only=True,synthetic_power_cut=True,completed_command_prefix_bytes=cut_bytes,writer_injected=False,reader_entry_fixture=True,pending_bank=pending,previous_bank=selected,old_bank_untouched=True,source_actual_shutdown_report='outputs/Digitone-E10-PC-auto-powerfail.json',failure=None)
try:
 with open(paths.card,'rb') as f:
  headers=[]
  for addr in [0xf400000,0xf800000]:f.seek(addr);headers.append(f.read(4).hex())
 r['bank_magics']=headers
 # The real boot selector and full-image reader are called through one test
 # frame. The guest reads the private card via its native eSDHC driver.
 value=call(s.m,0x400a8360,[],stack_top=0x47fdff00,limit=20_000_000)
 assert s.m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0,'Native reader did not return'
 chosen=rd(s.m.uc,0x402369e4)
 restored=b''.join(bytes(s.m.uc.mem_read(0x40555ff4+0x240200+i*0xa00+0x940,32)) for i in range(128))
 expected=bytes.fromhex(proof_auto['expected_bank']);previous=bytes.fromhex(proof_auto['previous_bank'])
 r.update(selected_bank=chosen,all_new_records=restored==expected,all_previous_records=restored==previous,new_record_matches=sum(restored[32*i:32*i+32]==expected[32*i:32*i+32] for i in range(128)),actual_records=restored[:64].hex(),expected_new_records=expected[:64].hex(),expected_previous_records=previous[:64].hex(),balanced_reader_return=True)
 r['observed_partial_new_bank_selection']=chosen==pending and restored!=expected and restored!=previous
 if cut_bytes==0:assert chosen==selected and restored==previous
 if cut_bytes==0x8000:assert r['observed_partial_new_bank_selection']
 if cut_bytes==0x2a8000:assert chosen==pending and restored==expected
 r['test_completed']=True
except Exception:
 import traceback
 r.update(test_completed=False,failure=traceback.format_exc());print(r['failure'],flush=True)
finally:s.close()
r['limits']=['One synthetic command-boundary loss of remaining writes, constructed from actual controller payload and the untouched prior card. Not physical flash failure.','Native cold reader runs in a stopped entry fixture with an existing boot snapshot, not a full cold reboot of the interrupted card.','This audits the stock two-bank protocol; the E10 firmware bytes are unchanged.']
Path('outputs/Digitone-E10-PC-powerfail-cut-first-command'+suffix+'.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2),flush=True)
if not r['test_completed']:raise SystemExit(1)
