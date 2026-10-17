from pathlib import Path
import json
trace=json.loads(Path('outputs/Digitone-OS1.44E04-cache-order-valid.json').read_text())
assert trace['passed'] and trace['copy_events'][0]['CACR']=='0x8c000'
assert trace['cache_order'][0]['value']=='0xa50ce100' and trace['first_helper_execution']
payload=Path('work/os144/fallback-final-payload.bin').read_bytes()
# Deliberately small value-aware cache model: distinguish persistent stale tags
# from current RAM. It tests documented invalidate requirements, not silicon.
def run(ic_stale,dc_stale,branch_stale,control):
 ram=payload;i=b'\x5a'*len(payload) if ic_stale else None;d=b'\x6b'*len(payload) if dc_stale else None;branch=0x47f40000 if branch_stale else None
 # Copier writes bypass data cache and disabled store buffering; instruction
 # cache is enabled in the inherited loader state and may retain old data.
 if control&0x100:i=None
 if control&0x1000000:d=None
 if control&0x40000:branch=None
 return {'code_fetch_exact':(ram if i is None else i)==payload,'data_read_exact':(ram if d is None else d)==payload,'old_branch_target_invalidated':branch is None}
r={'PC_only':True,'hardware_measured':False,'source':'NXP MCF54418RM cache chapter, and actual E04 startup trace','inherited_CACR':'0x0008c000','instruction_cache_enabled_during_copy':True,'data_cache_enabled_during_copy':False,'store_buffer_enabled_during_copy':False,'handoff_CACR':'0xa50ce100','cases':[],'negative_controls':[],'first_helper':trace['first_helper_execution'],'limits':['Value-aware logical model only, not physical cache tags, invalidation latency or silicon execution.','Seeded stale code/data/branch state is adversarial test input, not observed device state.']}
for flags in [(False,False,False),(True,False,False),(True,True,True)]:
 outcome=run(*flags,0xa50ce100);assert all(outcome.values());r['cases'].append({'stale_I_D_branch':flags,**outcome})
for mask,key in [(0x100,'code_fetch_exact'),(0x1000000,'data_read_exact'),(0x40000,'old_branch_target_invalidated')]:
 outcome=run(True,True,True,0xa50ce100&~mask);assert not outcome[key];r['negative_controls'].append({'removed_bit':hex(mask),'detected':True,**outcome})
r['passed']=True;Path('outputs/Digitone-OS1.44E04-cache-stale-state-checks.json').write_text(json.dumps(r,indent=2));print('PASS stale-state cache logic, 3 positive / 3 negative controls')
