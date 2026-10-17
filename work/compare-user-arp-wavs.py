from pathlib import Path
import sys,wave,json,hashlib
sys.path.insert(0,'work/emulator-deps')
import numpy as np
files={'modified':'inputs/recordings/digitone-20261006-184404.wav','stock':'inputs/recordings/digitone-20261006-185018.wav'}
out={'comparison':'User-labelled modified and stock Digiemu exports','files':{},'limits':['The exact pattern/sound/scale/effects state and emulator scheduling are not available in these recordings.','This is a waveform comparison, not a listening judgment or proof of hardware behavior.']}
for label,path in files.items():
 p=Path(path)
 with wave.open(str(p),'rb') as w:
  sr=w.getframerate();channels=w.getnchannels();width=w.getsampwidth();assert width==2
  x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,channels)
 z=x.astype(np.float64)/32768;d=np.max(np.abs(np.diff(z,axis=0)),axis=1);frames=np.arange(1,len(x));means=[float(d[frames%32==k].mean()) for k in range(32)];phase=int(np.argmax(means));boundary=frames%32==phase
 big=d>.02;top=np.argsort(d)[-100:];peak=float(np.max(np.abs(z)))
 out['files'][label]={'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sample_rate':sr,'channels':channels,'sample_width':width,'frames':len(x),'duration_seconds':len(x)/sr,'peak_dbfs':float(20*np.log10(max(peak,1e-15))),'rms_dbfs':float(10*np.log10(max(float(np.mean(z*z)),1e-30))),'full_scale_samples':int(np.sum((x==32767)|(x==-32768))),'channels_identical':bool(channels==2 and np.array_equal(x[:,0],x[:,1])),'strongest_boundary_phase_mod32':phase,'boundary_mean_jump':means[phase],'interior_mean_jump':float(d[~boundary].mean()),'boundary_to_interior_ratio':float(means[phase]/d[~boundary].mean()),'jumps_over_0_02':int(big.sum()),'jumps_over_0_02_on_boundary':int((big&boundary).sum()),'jumps_over_0_02_per_second':float(big.sum()/(len(x)/sr)),'top100_jumps_on_boundary':int(boundary[top].sum()),'largest_jump':float(d.max()),'largest_jumps':[{'seconds':float((i+1)/sr),'before':x[i].tolist(),'after':x[i+1].tolist(),'phase32':int((i+1)%32)} for i in top[-5:][::-1]]}
Path('outputs/Digitone-user-stock-modified-WAV-comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
