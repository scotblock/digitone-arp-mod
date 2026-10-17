"""Observe unmodified E10 bank behavior under native edits and pattern operations."""
from pathlib import Path
import json,struct,traceback
source=Path('work/test-PC-E10-bound-running-handoff.py').read_text(encoding='utf-8').split('\ntry:')[0]
source=source.replace('work/E10-bound-running-handoff','work/E10-copy-cache-audit').replace('outputs/E10-bound-handoff-','outputs/E10-copy-cache-')
exec(compile(source,'E10-copy-cache-probe-definitions','exec'))
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC
out.update(operations=[],native_copy_calls=[],native_codec_calls=[],record_writes=[])
for address,label in [(0x400fbad8,'memcpy'),(0x4018aa40,'bulk_copy'),(0x400095f4,'kit_encode'),(0x400093d0,'kit_decode'),(0x4000eb10,'project_encode'),(0x400852b4,'mirror_update')]:
 def entered(u,pc,n,d,label=label):
  sp=u.reg_read(UC_M68K_REG_A7);args=[rd(u,sp+i) for i in [4,8,12]]
  if label in ['memcpy','bulk_copy']:
   if label=='memcpy' and args[2] not in [0x988,0x16114,0x164a0,164]:return
   rows=out['native_copy_calls']
  else:rows=out['native_codec_calls']
  if len(rows)<4000:rows.append(dict(kind=label,phase=phase,caller=hex(rd(u,sp)),args=[hex(v) for v in args]))
 s.at(address,entered)
for address in [0x41306900,0x41307288]:
 def changed(u,access,a,n,value,d):
  if len(out['record_writes'])<2000:out['record_writes'].append(dict(phase=phase,address=hex(a),size=n,value=value,pc=hex(u.reg_read(UC_M68K_REG_PC))))
 s.m.uc.hook_add(UC_HOOK_MEM_WRITE,changed,begin=address,end=address+1)
def observe(label):
 mirror=0x40555ff4
 row=dict(label=label,phase=phase,ms=s.now_ms(),owner=hex(owner()),bank=[bytes(s.m.uc.mem_read(BANK+32*i,32)).hex() for i in [0,1]],mirror=[bytes(s.m.uc.mem_read(mirror+0x240200+i*0xa00+0x940,32)).hex() for i in [0,1]],mirror_ready=rd(s.m.uc,0x40555ee0),mirror_header=bytes(s.m.uc.mem_read(0x40555ee4,16)).hex(),generation=rd(s.m.uc,PM+12),fields=fields(),native_words=[int.from_bytes(s.m.uc.mem_read(p+158,2),'big') for p in [0x41306862,0x413071ea]])
 out['operations'].append(row);print(label,'words',row['native_words'],'bank',row['bank'][0][24:32],row['bank'][1][24:32],'mirror',row['mirror'][0][24:32],row['mirror'][1][24:32],flush=True)
try:
 if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
  t=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);t.now=s.pits.now;s.pits.sources=s.pits.sources+(t,)
 s.run_ms(200);tap('STOP');tap('NO');choose(1);tap('SYN1');combo('SYN2')
 if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=150)
 phase='unsaved_step';observe('before_unsaved_edit');s.turn(6,16,after_ms=200);observe('after_unsaved_edit');tap('NO')
 # Use distinct native settings as an independent completion witness for paste.
 for slot,turns in [(1,1),(2,2)]:
  phase='configure_'+str(slot);choose(slot);tap('SYN1');combo('SYN2')
  if rd(s.m.uc,X+56):s.turn(4,-16,after_ms=150)
  for _ in range(turns):s.turn(2,16,after_ms=150)
  tap('NO')
 phase='copy_A01';choose(1);tap('SYN1');observe('before_copy');combo('RECORD');observe('copied')
 phase='select_A02';choose(2);observe('before_paste')
 phase='paste_A02';combo('STOP');s.run_ms(200);observe('pasted')
 phase='undo_paste';combo('STOP');s.run_ms(200);observe('undo_paste')
 phase='paste_again';combo('STOP');s.run_ms(200);observe('pasted_again')
 phase='clear_A02';combo('PLAY');s.run_ms(200);observe('cleared')
 phase='undo_clear';combo('PLAY');s.run_ms(200);observe('undo_clear')
 assert s.halted is None;out['execution_passed']=True
except Exception:
 out.update(execution_passed=False,failure=traceback.format_exc());print(out['failure'],flush=True)
finally:
 s.close();out['limits']=['Observational baseline, not a correctness certification. No extra E10 records/hooks/helpers/settings are host-written.','Native clipboard/undo operations and working-mirror observations on a private PC card. No physical power loss.']
 Path('outputs/Digitone-E10-PC-copy-cache-audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
if not out.get('execution_passed'):raise SystemExit(1)
