from pathlib import Path
import csv, hashlib, json, statistics, wave
import numpy as np

root = Path(__file__).resolve().parents[1]
audio = Path('inputs/recordings/3-Audio 0016 [2026-10-08 193839].wav')
csvpath = root / 'outputs/stock-hardware-measurements/stock-click-120-20261008-194030.csv'
metapath = csvpath.with_suffix('.json')
rows = list(csv.DictReader(csvpath.open(newline='')))
meta = json.loads(metapath.read_text())
starts = [i for i, r in enumerate(rows) if r['kind'] == 'start']
stops = [i for i, r in enumerate(rows) if r['kind'] == 'stop']
assert len(starts) == len(stops) == 1 and starts[0] < stops[0]
clock = [r for r in rows[starts[0]+1:stops[0]] if r['kind'] == 'clock']
midi = {'all_messages': len(rows), 'all_clock_messages': sum(r['kind']=='clock' for r in rows), 'playback_clock_messages': len(clock), 'logger_stats': meta['stats']}
for field, factor in [('callback_elapsed_ns', 1e-6), ('driver_elapsed_ms', 1.0)]:
    t = np.array([int(r[field])*factor for r in clock])
    dt = np.diff(t)
    indices = np.arange(len(t), dtype=float)
    slope = float(np.dot(indices-indices.mean(), t-t.mean()) / np.dot(indices-indices.mean(), indices-indices.mean()))
    midi[field] = {'start_ms': int(rows[starts[0]][field])*factor, 'stop_ms': int(rows[stops[0]][field])*factor,
                   'transport_duration_seconds': (int(rows[stops[0]][field])-int(rows[starts[0]][field]))*factor/1000,
                   'first_to_last_clock_seconds': float((t[-1]-t[0])/1000),
                   'mean_clock_interval_ms': float(dt.mean()), 'regression_bpm': 60000/(24*slope),
                   'interval_percentiles_ms': dict(zip(['min','p01','median','p99','max'], np.percentile(dt,[0,1,50,99,100]).tolist())),
                   'intervals_over_31_25_ms': int(np.sum(dt>31.25)), 'intervals_under_10_4167_ms': int(np.sum(dt<10.4167)),
                   'nonpositive_intervals': int(np.sum(dt<=0))}
with wave.open(str(audio), 'rb') as w:
    rate, channels, width, frames = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
    raw = w.readframes(frames)
assert width == 3 and channels == 2
b = np.frombuffer(raw, np.uint8).reshape(-1,3).astype(np.int32)
p = (b[:,0] | (b[:,1]<<8) | (b[:,2]<<16))
p = ((p ^ 8388608)-8388608).reshape(-1,channels)
x = p.astype(np.float64)/8388608
def db(v): return float(20*np.log10(max(float(v),1e-15)))
block = rate//100
z = x[:len(x)//block*block].reshape(-1,block,channels)
peak = np.max(np.abs(z), axis=(1,2))
rms = np.sqrt(np.mean(z*z,axis=(1,2)))
active = np.flatnonzero(peak>0.001)
def runs(mask, minimum):
    edges = np.diff(np.r_[False,mask,False].astype(np.int8))
    return [(int(a),int(b)) for a,b in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)) if b-a>=minimum]
quiet = runs(rms<10**(-60/20),10)
zeros = runs(np.all(p==0,axis=1),rate//1000)
delta = np.max(np.abs(np.diff(x,axis=0)),axis=1)
top = np.argsort(delta)[-10:][::-1]
a = {'path': str(audio), 'sha256': hashlib.sha256(audio.read_bytes()).hexdigest(),
     'sample_rate':rate,'channels':channels,'bits':width*8,'duration_seconds':frames/rate,
     'peak_dbfs':db(np.max(np.abs(x))), 'channel_rms_dbfs':[db(np.sqrt(np.mean(x[:,i]**2))) for i in range(channels)],
     'clipped_samples':int(np.sum(np.abs(p)>=8388607)),
     'first_last_above_minus60_peak_seconds':[float(active[0]/100),float((active[-1]+1)/100)] if len(active) else None,
     'quiet_runs_below_minus60_rms_at_least_100ms':[{'start_seconds':s/100,'end_seconds':e/100} for s,e in quiet],
     'exact_zero_runs_at_least_1ms':[{'start_seconds':s/rate,'end_seconds':e/rate} for s,e in zeros],
     'largest_adjacent_sample_changes':[{'seconds':float(i/rate),'change_full_scale':float(delta[i])} for i in top],
     'continuity_limit':'Quiet intervals and large sample changes can be intentional music. These tests do not classify all clicks or prove deadline compliance.'}
result = {'audio':a,'midi':midi,'sources':{'csv':str(csvpath),'json':str(metapath)},
          'alignment':'User supplied this as the repeat paired take. Audio and MIDI have separate time origins; absolute alignment is not established by filenames or transport events alone.',
          'firmware':'User-reported physical stock 1.44; no modified firmware or cache measurements.'}
dest=root/'outputs/Digitone-stock-paired-take-20261008-analysis.json'
dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
