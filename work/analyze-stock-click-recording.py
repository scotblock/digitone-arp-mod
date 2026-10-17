from pathlib import Path
import wave,json,csv,hashlib
import numpy as np
path=Path('inputs/recordings/3-Audio 0013 [2026-10-07 205444].wav')
csvpath=Path('outputs/stock-hardware-measurements/stock-click-120-20261007-205913.csv')
with wave.open(str(path),'rb') as w:
 rate=w.getframerate();channels=w.getnchannels();width=w.getsampwidth();count=w.getnframes();raw=w.readframes(count)
assert (rate,channels,width)==(48000,2,3)
packed=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.int32)
pcm=packed[:,0]|(packed[:,1]<<8)|(packed[:,2]<<16);pcm=(pcm^0x800000)-0x800000;pcm=pcm.reshape(-1,channels)
x=pcm.astype(np.float64)/8388608
bin_n=48;usable=len(x)//bin_n;env=np.max(np.abs(x[:usable*bin_n].reshape(usable,bin_n,channels)),axis=(1,2))
threshold=float(np.percentile(env,99.9)*0.12)
indices=np.flatnonzero(env>threshold);groups=[]
if len(indices):
 splits=np.flatnonzero(np.diff(indices)>50)+1
 for row in np.split(indices,splits):groups.append((int(row[0]),int(row[-1]),float(env[row].max())))
onsets=np.array([g[0]*bin_n for g in groups],dtype=np.int64)
diff=np.diff(onsets)/rate
with csvpath.open(newline='') as f:log=list(csv.DictReader(f))
r={'WAV':str(path),'WAV_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sample_rate':rate,'bits':width*8,'channels':channels,'duration_seconds':len(x)/rate,'peak_dBFS':float(20*np.log10(max(float(np.max(np.abs(x))),1e-15))),'clipped_samples':int((np.abs(pcm)>=8388607).sum()),'channel_rms_dBFS':[float(20*np.log10(max(float(np.sqrt(np.mean(x[:,i]**2))),1e-15))) for i in range(channels)],'MIDI_rows':len(log),'MIDI_clock_count':sum(e['kind']=='clock' for e in log),'detection_threshold':threshold,'coarse_clicks':[{'seconds':a/1000,'duration_ms':b-a+1,'peak':peak} for a,b,peak in groups],'coarse_interval_seconds':diff.tolist(),'failure':None,'limits':['Stock hardware analog output captured through Rubix; sample clock and analog path are part of the measurement.','Empty MIDI CSV cannot establish clock jitter or audio-to-clock alignment.','This does not validate modified E04 cache behaviour or internal render/DMA deadlines.']}
try:
 assert len(onsets)>30,'Insufficient click candidates'
 print('candidate clicks',len(onsets),'interval percentiles',np.percentile(diff,[0,10,50,90,100]),'peak',r['peak_dBFS'],flush=True)
 # Work only on the longest uninterrupted sequence of approximately 0.5-s clicks.
 breaks=np.flatnonzero((diff<0.45)|(diff>0.55))+1;parts=np.split(np.arange(len(onsets)),breaks);chosen=max(parts,key=len)
 assert len(chosen)>30
 active=onsets[chosen];mono=x[:,int(np.argmax(np.mean(x*x,axis=0)))];matched=[];quality=[]
 templates={};half_search=200;length=2048
 for phase in range(4):
  k=phase+8;start=int(active[k])-48;templates[phase]=mono[start:start+length].copy()
 for k,onset in enumerate(active):
  template=templates[k%4];start=int(onset)-48-half_search;segment=mono[start:start+length+2*half_search]
  assert len(segment)==length+2*half_search
  # Full correlation, with a moving energy term for normalized quality.
  nfft=1<<((len(segment)+len(template)-2).bit_length())
  corr=np.fft.irfft(np.fft.rfft(segment,nfft)*np.fft.rfft(template[::-1],nfft),nfft)[length-1:length-1+2*half_search+1]
  window_energy=np.convolve(segment*segment,np.ones(length),mode='valid');den=np.sqrt(window_energy*np.dot(template,template));normalized=corr/np.maximum(den,1e-30)
  best=int(np.argmax(normalized));matched.append(start+best);quality.append(float(normalized[best]))
 matched=np.array(matched,dtype=np.float64);beats=np.arange(len(matched))
 # Independent phase templates have different onset references. Fit each
 # phase's fixed offset rather than interpreting it as per-beat jitter.
 design=np.column_stack([beats]+[(beats%4==phase).astype(float) for phase in range(4)])
 fitted=np.linalg.lstsq(design,matched,rcond=None)[0];slope=fitted[0];residual=matched-design@fitted
 interval=np.diff(matched);same_phase=(matched[4:]-matched[:-4])/4
 r['timing']={'clicks_used':len(matched),'start_seconds':float(matched[0]/rate),'end_seconds':float(matched[-1]/rate),'samples_per_beat_fit':float(slope),'measured_BPM_relative_to_Rubix_sample_clock':float(60*rate/slope),'beat_period_ms_fit':float(1000*slope/rate),'phase_reference_interval_ms_min':float(interval.min()*1000/rate),'phase_reference_interval_ms_max':float(interval.max()*1000/rate),'same_phase_four_beat_span_ms_min':float(same_phase.min()*4000/rate),'same_phase_four_beat_span_ms_max':float(same_phase.max()*4000/rate),'fit_residual_peak_to_peak_samples':float(np.ptp(residual)),'fit_residual_std_samples':float(residual.std()),'deviation_from_120BPM_ppm':float((slope/(rate/2)-1)*1e6),'matched_click_samples':matched.astype(int).tolist(),'template_correlation_min':min(quality),'template_correlation_median':float(np.median(quality)),'coarse_gaps_outside_half_second_tolerance':int(((diff<0.45)|(diff>0.55)).sum())}
 r['limits'].append('Each four-beat phase uses a separate waveform template and fixed reference offset. Adjacent template-reference intervals are not a direct jitter measurement. Fit residuals describe alignment repeatability at the 48 kHz sample grid, not internal CPU jitter.')
 assert min(quality)>0.85,'Click templates do not reliably match; inspect audio'
 r['passed_audio_analysis']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc();r['passed_audio_analysis']=False;print(r['failure'],flush=True)
Path('outputs/Digitone-stock-physical-click-analysis.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:r.get(k) for k in ['duration_seconds','peak_dBFS','clipped_samples','MIDI_rows','timing','failure']},indent=2))
