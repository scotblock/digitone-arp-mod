"""Exact instruction anchors for proposed metadata lifecycle boundaries."""
from pathlib import Path
import hashlib,json
b=Path('work/section-3.bin').read_bytes();base=0x40000400
anchors={
'allocator private-slot result':(0x400f0658,'2008'),
'recycle masked entry':(0x400f0676,'46fc2700'),
'recycle publishes slot':(0x400f0684,'23ca4199fea0'),
'common-copy destination':(0x400f0694,'246f000c'),
'common-copy source':(0x400f0698,'266f0010'),
'common-copy byte call':(0x400f06c4,'4eb9400ec23c'),
'common-copy completion':(0x400f06ca,'4fef000c'),
'held-cache first event write':(0x400efa5a,'2941000c'),
'held raw copy 1':(0x400efbe0,'4e95'),
'held publication 1':(0x400efbe4,'4eb9400f0886'),
'held raw copy 2':(0x400efc08,'4e95'),
'held raw copy 3':(0x400efc2a,'4eb9400ec23c'),
'held publication tail':(0x400efc3e,'4ef9400f0886'),
'queue free pop':(0x400efe88,'23d0431dc4c4'),
'queue valid-track branch':(0x400efec4,'6c10'),
'queue reject free publication':(0x400efecc,'23c8431dc4c4'),
'queue pending first link':(0x400efede,'2688'),
'queue due alloc':(0x400eff9c,'4e93'),
'queue event publication':(0x400efffa,'4e94'),
'queue free publication':(0x400f0024,'23ca431dc4c4'),
'clone byte copy':(0x4009bda6,'4eb9400ec23c'),
'clone first link write':(0x4009bdd2,'256b00440044'),
'clone source overwrite':(0x4009bdc6,'256b0008003c'),
'accepted return nonzero test':(0x4009de12,'4a83'),
'accepted incoming identity write':(0x4009de1c,'27430040'),
'accepted retained copy':(0x4009de40,'4eb9400f0690'),
'scheduled retained copy':(0x4009ce3c,'4eb9400f0690'),
'scheduled tick first link':(0x4009ce68,'2b6b00440044'),
'live first publication head':(0x400f08de,'23c84199fe94'),
'live append existing chain':(0x400f08aa,'21420044'),
'live new before existing head':(0x400f08de,'23c84199fe94'),
'timed head publication':(0x400f0874,'23c84199fe94'),
'timed middle publication':(0x400f085c,'25400010'),
'timed append existing event chain':(0x400f083a,'21420044'),
'drain routes actual event free':(0x400f0934,'4e95'),
'cached sequencer synth construction':(0x40094476,'4ebaf7ae'),
'fresh sequencer synth construction':(0x40095250,'4ebae9d4'),
'sequencer source pattern argument':(0x40093c30,'266f0064'),
'sequencer source track argument':(0x40093c3a,'282f0060'),
'sequencer reused cache type':(0x40093e7e,'2480'),
'sequencer fresh alloc':(0x40093e82,'4eb9400f0626'),
'sequencer success return value':(0x40093f6e,'200a'),
'sequencer raw cache emission 1':(0x4009344e,'4e91'),
'sequencer raw cache emission 2':(0x40093892,'4eb9400ec23c'),
'sequencer emission timed publish 1':(0x400934ac,'4e96')}
rows=[]
for label,(a,h) in anchors.items():
 actual=b[a-base:a-base+len(h)//2].hex()
 assert actual==h,(label,hex(a),actual,h)
 rows.append({'label':label,'pc':hex(a),'bytes':h})
r=json.load(open('outputs/Digitone-persistent-context-integration-execution.json'))
completion={t.get('pc') for c in r['actual_cases'] for t in c['trace'] if t['kind']=='copy completed'}
assert {'0x400efbe2','0x400efc0a','0x400efc30','0x400f06ca','0x4009bdac'}<=completion
result={'anchors_verified':len(rows),'anchors':rows,'all_three_held_copy_sites_executed':True,'section_sha256':hashlib.sha256(b).hexdigest(),'scope':'listed instruction bytes; not a reachable whole-program coverage proof'}
Path('outputs/Digitone-persistent-context-integration-anchors.json').write_text(json.dumps(result,indent=2))
print('Verified',len(rows),'anchors and three held-copy execution boundaries')
