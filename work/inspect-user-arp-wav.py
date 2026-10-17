from pathlib import Path
import sys,wave,json,hashlib
sys.path.insert(0,'work/emulator-deps')
import numpy as np
SOURCE=Path('inputs/recordings/digitone-20261006-184404.wav')
with wave.open(str(SOURCE),'rb') as w:
 params={'channels':w.getnchannels(),'sample_width':w.getsampwidth(),'sample_rate':w.getframerate(),'frames':w.getnframes(),'compression':w.getcomptype()};raw=w.readframes(w.getnframes())
assert params['sample_width']==2 and params['compression']=='NONE'
x=np.frombuffer(raw,dtype='<i2').reshape(-1,params['channels']);z=x.astype(np.float64)/32768;sr=params['sample_rate']
r={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),**params,'duration_seconds':len(x)/sr,'channels_metrics':[]}
for c in range(x.shape[1]):
 a=z[:,c];d=np.diff(a);power=np.mean(a*a);r['channels_metrics'].append({'peak':float(np.max(np.abs(a))),'peak_dbfs':float(20*np.log10(max(np.max(np.abs(a)),1e-15))),'rms_dbfs':float(10*np.log10(max(power,1e-30))),'dc_offset':float(np.mean(a)),'full_scale_samples':int(np.sum((x[:,c]==32767)|(x[:,c]==-32768))),'near_full_scale_samples':int(np.sum(np.abs(a)>=0.99)),'jump_max':float(np.max(np.abs(d))),'jumps_over_half_full_scale':int(np.sum(np.abs(d)>0.5)),'jump_mod32_mean':[float(np.mean(np.abs(d[np.arange(len(d))%32==k]))) for k in range(32)]})
 amp=np.max(np.abs(z),axis=1)
silent=amp==0
edges=np.flatnonzero(np.diff(np.r_[False,silent,False]));r['zero_runs_over_1ms']=[{'start_seconds':float(a/sr),'duration_ms':float((b-a)*1000/sr)} for a,b in edges.reshape(-1,2) if b-a>=sr/1000]
blocks=x[:len(x)//32*32].reshape(-1,32,x.shape[1]);equal=np.all(blocks[1:]==blocks[:-1],axis=(1,2));active=np.max(np.abs(blocks[:-1].astype(np.int32)),axis=(1,2))>100
r['identical_adjacent_active_32_frame_blocks']={'count':int(np.sum(equal&active)),'examples_seconds':(np.flatnonzero(equal&active)[:30]*32/sr).tolist()}
diff=np.max(np.abs(np.diff(z,axis=0)),axis=1);largest=np.argsort(diff)[-20:][::-1];r['largest_jumps']=[{'frame':int(i+1),'seconds':float((i+1)/sr),'magnitude':float(diff[i]),'before':x[i].tolist(),'after':x[i+1].tolist(),'phase32':int((i+1)%32)} for i in largest]
r['windows']=[]
for start in range(0,len(x),int(sr*.1)):
 a=z[start:start+int(sr*.1)];r['windows'].append({'start_seconds':start/sr,'rms':float(np.sqrt(np.mean(a*a))),'peak':float(np.max(np.abs(a)))})
Path('outputs/Digitone-user-WAV-analysis.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in ['duration_seconds','sample_rate','channels_metrics','zero_runs_over_1ms','identical_adjacent_active_32_frame_blocks','largest_jumps']},indent=2))
