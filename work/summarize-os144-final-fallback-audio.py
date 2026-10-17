from pathlib import Path
import json,hashlib
import sys
sys.path.insert(0,'work/emulator-deps')
import numpy as np
read=lambda name:json.loads(Path('outputs/'+name+'.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
boot={mode:read('Digitone-OS1.44-fallback-final-'+mode) for mode in ['valid','bad_magic','bad_pointer']}
for mode,r in boot.items():
 assert r['passed'] and r['copier_stores']==623 and r['placement']['entry']=='0x47be08a4'
 assert r['audio_sha256']==read('Digitone-OS1.44-fallback-continuous-'+mode)['audio_sha256']
 # Correct a report label inherited before the relocated address was assigned.
 r['entry']=r['placement']['entry'];Path('outputs/Digitone-OS1.44-fallback-final-'+mode+'.json').write_text(json.dumps(r,indent=2))
contracts=read('Digitone-OS1.44-final-fallback-contract-checks');loader=read('Digitone-OS1.44-final-fallback-loader-cache-check')
assert contracts['passed'] and len(contracts['cases'])==33 and loader['passed'] and loader['copier_stores']==623
modes=['stock','fallback','no-pitch','only-pitch','timing-only','timing-allocation','replay-stock']
audio={m:read('Digitone-OS1.44-fallback-audio-'+m) for m in modes};stock=audio['stock'];fallback=audio['fallback']
assert all(r['passed'] for r in audio.values())
values=lambda r:[x['value'] for x in r['pitch']]
packets=lambda r:[x['packet'] for x in r['transfers']]
render_packets=lambda r:[x['packet'] for x in r['DSP']]
voices=lambda r:[x['voices_sha256'] for x in r['DSP']]
assert values(stock)==values(fallback) and packets(stock)==packets(fallback)
assert render_packets(stock)==render_packets(audio['replay-stock']) and voices(stock)==voices(audio['replay-stock'])
assert stock['audio_sha256']==audio['replay-stock']['audio_sha256']!=fallback['audio_sha256']
first=next(i for i,(a,b) in enumerate(zip(stock['DSP'],fallback['DSP'])) if a['packet']!=b['packet'])
assert first==49 and stock['DSP'][49]['packet']==stock['transfers'][48]['packet'] and fallback['DSP'][49]['packet']==fallback['transfers'][49]['packet']
def events_near(r,index):
 i=next(i for i,e in enumerate(r['events']) if e['kind']=='render' and e['index']==index);return r['events'][i-4:i+5]
summary={}
for m,r in audio.items():
 summary[m]={'audio_sha256':r['audio_sha256'],'audio_matches_stock':r['audio_sha256']==stock['audio_sha256'],'pitches_match_stock':values(r)==values(stock),'generated_packets_match_stock':packets(r)==packets(stock),'consumed_packets_match_stock':render_packets(r)==render_packets(stock),'voice_blocks_match_stock':voices(r)==voices(stock)}
assert all(r['pitches_match_stock'] for r in summary.values())
assert not summary['timing-allocation']['audio_matches_stock']
x,y=[np.frombuffer(Path('work/os144/fallback-audio-'+m+'.pcm').read_bytes(),dtype='<i2').reshape(-1,2) for m in ['stock','fallback']]
different=np.any(x!=y,axis=1)
first_voice=next(i for i,(a,b) in enumerate(zip(stock['DSP'],fallback['DSP'])) if a['voices_sha256']!=b['voices_sha256'])
out={'PC_only':True,'passed':True,'placement':boot['valid']['placement'],'continuous_cases':{m:{k:r[k] for k in ['passed','copy_events','copier_stores','pointer_at_UI','pointer_after_playback','startup_entries']} for m,r in boot.items()},'isolated_contract_cases':len(contracts['cases']),'loader_derived_copy_events':loader['events'],'loader_scope':'Unchanged E03 loads first; source extension, copier count and jump are then overlaid before application prefix. No new packed-container load was tested.','audio_controls':summary,'first_packet_difference':{'render_index':first,'stock_render_ms':stock['DSP'][first]['ms'],'fallback_render_ms':fallback['DSP'][first]['ms'],'stock_consumes_transfer_index':48,'fallback_consumes_transfer_index':49,'stock_word290':'267d1800','fallback_word290':'26aa1800','stock_order':events_near(stock,first),'fallback_order':events_near(fallback,first)},'first_voice_difference_render':first_voice,'PCM_metrics':{'frames':len(x),'first_different_frame':int(np.flatnonzero(different)[0]),'different_frame_fraction':float(different.mean()),'maximum_16bit_sample_difference':int(np.abs(x.astype(np.int32)-y).max())},'preserved_files':{p:sha(p) for p in ['outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx','work/os144/packed-context-overlay.bin']},'limits':['PC overlays only; no firmware image rebuilt or device accessed.','Cache-control order and byte preservation are modeled; physical cache coherence not simulated.','Copied extension has not been repackaged or passed through the loader as part of a new container.','Audio trace and replay use existing instruction-timed, accelerated, deterministic DSP model; no physical timing/deadline guarantee.','Replay explicitly forces each stock input packet by render ordinal; it is a causal diagnostic, not a proposed synchronization change.','Timing-only allocation shim adds 32 NOPs and a jump/trampoline; its cost is not exactly matched to the full helpers.','No-pitch and pitch-only controls match stock PCM here, while the combined fallback differs. This result is specific to this state and workload.']}
assert out['preserved_files']['outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx']=='8775320f161cb02efa8f51b2671034baf73eeec95f4bb66ffc20a29e9b0a2a3d'
Path('outputs/Digitone-OS1.44-final-fallback-audio-summary.json').write_text(json.dumps(out,indent=2))
print('PASS final placement/copy/contracts and causal packet replay; E03 unchanged')
