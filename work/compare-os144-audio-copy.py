from pathlib import Path
import sys,json
sys.path.insert(0,'work/emulator-deps')
import numpy as np
names=sys.argv[1:] or ['stock','repeat','helpers','allocator','held']
runs={v:json.loads(Path('outputs/Digitone-OS1.44-audio-copy-'+v+'.json').read_text()) for v in names}
out={'firmware_modified':False,'comparisons':[],'runs':{}}
for v,r in runs.items():
 out['runs'][v]={k:r.get(k) for k in ['failure','halted','audio_bytes','audio_sha256','helper_hits','storage_checks','first_copy_guards','copy_checks']}
 print(v,'failure',r['failure'],'hits',r.get('helper_hits'),'first guards',len(r.get('first_copy_guards',[])))
a=runs[names[0]];x=np.frombuffer(Path('work/audio-copy-'+names[0]+'.pcm').read_bytes(),dtype='<i2').reshape(-1,2)
for v,b in list(runs.items())[1:]:
 y=np.frombuffer(Path('work/audio-copy-'+v+'.pcm').read_bytes(),dtype='<i2').reshape(-1,2);n=min(len(x),len(y));bad=np.flatnonzero(np.any(x[:n]!=y[:n],axis=1))
 c={'right':v,'equal':len(x)==len(y) and not len(bad),'different_frames':len(bad),'first_frame':int(bad[0]) if len(bad) else None,'first_ms':float(bad[0]/48) if len(bad) else None}
 for label,key in [('packet','packet'),('voice','voice')]:
  pairs=list(zip(a['dsp'],b['dsp']));i=next((i for i,(p,q) in enumerate(pairs) if p[key]!=q[key]),None)
  c[label+'_count']=[len(a['dsp']),len(b['dsp'])];c['first_'+label+'_difference']=i
  if i is not None:c['first_'+label+'_records']=[pairs[i][0],pairs[i][1]]
 c['first_ssi_difference']=next((i for i,(p,q) in enumerate(zip(a['ssi_chunks'],b['ssi_chunks'])) if p['sha256']!=q['sha256']),None)
 c['pitch_sequences_equal']=[p['fixed_pitch'] for p in a['pitch_outputs']]==[p['fixed_pitch'] for p in b['pitch_outputs']]
 out['comparisons'].append(c);print(c)
Path('outputs/Digitone-OS1.44-audio-copy-comparison.json').write_text(json.dumps(out,indent=2))
