from pathlib import Path
import json,collections
r=json.loads(Path('outputs/Digitone-E04-PC-live-context-trace.json').read_text())['cases'][0]
t=r['trace'];print('counts',collections.Counter(x['label'] for x in t));print('path count',len(r.get('helper_paths',[])))
def frame(x):return [int.from_bytes(bytes.fromhex(x['private_tail'])[i:i+4],'big') for i in range(256,272,4)]
def show(x):
 return {'label':x['label'],'pc':x['pc'],'ms':round(x['ms'],3),'stage':x['stage'],'D0':hex(x['regs']['D0']),'A0':hex(x['regs']['A0']),'A2':hex(x['regs']['A2']),'A3':hex(x['regs']['A3']),'stack':[hex(a) for a in x['stack'][:5]],'frame':[hex(v) for v in frame(x)],'events':[e for e in x['events'] if e['slot']]}
for label in ['commit','read','read return','copy','first_copy','producer_capture','stock queue_publish','candidate_store']:
 seq=[x for x in t if x['label']==label]
 print('\n',label,'total',len(seq))
 for x in seq[:4]:print(json.dumps(show(x)))
commits=[x for x in t if x['label']=='commit' and x['stack'][3]==0]
if commits:
 first=commits[0];i=t.index(first)
 print('\nFIRST ZERO COMMIT')
 for x in t[max(0,i-13):i+8]:print(json.dumps(show(x)))
Path('outputs/Digitone-E04-PC-live-context-trace-index.json').write_text(json.dumps({'counts':dict(collections.Counter(x['label'] for x in t)),'first_zero_commit':show(commits[0]) if commits else None,'first_events':[show(x) for x in t[:8]]},indent=2))
