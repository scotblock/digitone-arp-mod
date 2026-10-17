from pathlib import Path
import json,struct
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
target=0x4009c6d0;refs=[]
for p in range(0,len(d)-6,2):
 w=int.from_bytes(d[p:p+2],'big');pc=b+p
 if w in [0x4eba,0x4efa] and pc+2+int.from_bytes(d[p+2:p+4],'big',signed=True)==target:refs.append({'pc':hex(pc),'kind':'PC-relative JSR/JMP candidate'})
 if w&0xff00 in [0x6000,0x6100]:
  q=w&255;disp=int.from_bytes(bytes([q]),'big',signed=True) if q not in [0,255] else int.from_bytes(d[p+2:p+(6 if q==255 else 4)],'big',signed=True)
  if pc+2+disp==target:refs.append({'pc':hex(pc),'kind':'relative branch/call candidate'})
 if d[p:p+4]==target.to_bytes(4,'big'):refs.append({'pc':hex(pc),'kind':'literal pointer candidate'})
static=json.loads(Path('outputs/Digitone-E04-PC-parent-counter-lifetime-static.json').read_text())
thunks=[x for x in static['increment_sites'] if x['following_code_is_jmp_thunk']]
assert len(thunks)==80 and not any(x['literal_thunk_references'] for x in thunks)
out={'PC_only':True,'diagnostic_entry':hex(target),'references':refs,'preceding_instruction':'4009c6ce RTS; entry begins with A3/A2 pushes then call to pool wrapper','diagnostic_body_after_inner_refusal':'Allocates and publishes events; observed in prior native test. Candidate must refuse outer entry before pushes/allocation.','shutdown':{'startup_counter':94,'literal_increment_sites':94,'literal_decrement_sites':94,'startup_table_entries':133,'adjacent_finalizer_jump_thunks':80,'literal_references_to_these_thunks':0,'continuous_queue_owner_stable':True,'global_release_deletes_parent_at_zero':True,'conclusion':'Evidence supports global startup lifetime rather than per-pattern destruction. Full shutdown dispatch and worker exclusion at zero remain unproven.'},'candidate_policy':'Refuse unsupported diagnostic queue entry; retain existing live reset/UI refusal guards. Do not replace or suppress global parent release.','limits':['Even-address scans yield candidates; unresolved computed references and alternate/interior entries remain possible.','No complete finalization call graph or hardware shutdown timing is established.','New candidate is explicitly PC-only, with unresolved lifetime and physical ownership limits recorded.']}
Path('outputs/Digitone-E05-shutdown-diagnostic-audit.json').write_text(json.dumps(out,indent=2));print('Audit:',len(refs),'diagnostic reference candidates; 80 unreferenced literal finalizer thunks; shutdown exclusion unresolved')
