from pathlib import Path
import json,hashlib,shutil
def load(scenario,mode):
 p=Path('outputs/Digitone-E02-audio-control-'+scenario+'-'+mode+'.json')
 if scenario=='simple' and not p.exists():p=Path('outputs/Digitone-E02-audio-control-'+mode+'.json')
 r=json.loads(p.read_text());assert r['failure'] is None and r['halted'] is None;return r
summary={'source_firmware_modified':False,'installed_Digiemu_modified':False,'cases':{},'findings':[],'limits':['Emulator functional/host-thread tests do not certify physical timing, cache coherence or hardware firmware installation.','Stock user session differs in pattern/sound from the modified user session; direct stock-vs-modified WAV comparison is not an exact matched workload.','Same-snapshot hook-restoration and threaded/synchronous comparisons control that difference. Restoring startup sites after boot does not undo startup history.','The barrier is a test harness host wait at the voice-DMA start; it has not been installed in the user application or packaged as an emulator fix.']}
for scenario in ['simple','arp']:
 cases=[load(scenario,m) for m in ['stock','custom','custom-no-arp','stock-with-arp']]
 assert len({r['audio']['sha256'] for r in cases})==1
 assert len({r['marks'][1]['pattern_hash'] for r in cases})==1
 summary['cases'][scenario]=[{k:r[k] for k in ['mode','audio','helper_hits']} for r in cases]
summary['cases']['nonchromatic']=[{k:load('arp-scale',m)[k] for k in ['mode','audio','helper_hits']} for m in ['stock','custom']]
for scenario,modes in [('user',['stock','stock-with-arp','custom','custom-no-arp']),('user-threaded',['stock','custom','custom-no-arp','custom-all-stock']),('user-threaded-barrier',['custom','stock'])]:
 summary['cases'][scenario]=[]
 for mode in modes:
  r=load(scenario,mode);summary['cases'][scenario].append({k:r[k] for k in ['mode','audio','helper_hits','pitch']})
  if 'barrier' in scenario:summary['cases'][scenario][-1].update(barrier_calls=r.get('DSP_read_barrier_calls'),busy_at_read=r.get('DSP_busy_at_voice_read'))
inline=load('user','custom');threaded=load('user-threaded','custom');barrier=load('user-threaded-barrier','custom');disabled=load('user-threaded','custom-all-stock')
assert inline['audio']['jumps_over_0_02']==0 and threaded['audio']['jumps_over_0_02_on_32_boundary']>100 and disabled['audio']['jumps_over_0_02_on_32_boundary']>100
assert disabled['all_nine_hook_sites_restored_in_RAM'] and not disabled['helper_hits']
assert inline['audio']['sha256']==barrier['audio']['sha256'] and barrier['audio']['jumps_over_0_02']==0
assert load('user','stock')['audio']['sha256']==load('user','stock-with-arp')['audio']['sha256']
assert load('user-threaded-barrier','stock')['audio']['jumps_over_0_02']==0
assert [p['fixed_pitch'] for p in load('user','stock')['pitch']]==[p['fixed_pitch'] for p in load('user-threaded-barrier','stock')['pitch']]
summary['stock_barrier_PCM_matches_synchronous']=False
notes=lambda r:[p['fixed_pitch']>>16 for p in r['pitch']]
assert notes(inline)==[60,60,64,65,60] and notes(load('user','custom-no-arp'))==[60,61,64,66,60]
summary['findings']=['Simple and factory-arp matched workloads are byte-identical in stock/E02 and startup/runtime isolation controls.','The actual modified user session is clean synchronously and exhibits the uploaded block-boundary symptom with background DSP rendering.','The symptom persists with seven arp hooks disabled and with all nine startup/runtime sites restored to stock in RAM.','An emulator-only wait for DSP completion immediately before voice DMA yields audio byte-identical to the clean synchronous E02 run. Stock retains its pitch sequence and has no large jumps, but its PCM differs from synchronous stock.','The actual user arp sequence is scale-constrained correctly: C/Csharp/E/Fsharp becomes C/C/E/F.']
summary['next_step']='Implement and validate the DSP voice-buffer ownership barrier in a separate emulator build or launcher, retaining the same firmware and source sessions.'
for mode,name in [('custom','Digitone-user-scale-locked-clean.wav'),('custom-no-arp','Digitone-user-same-pattern-stock-pitch-clean.wav')]:
 shutil.copyfile('outputs/Digitone-E02-audio-control-user-'+mode+'.wav','outputs/'+name)
for path,digest in [('outputs/Digitone_OS1.44E02_SCALE_ARP_DIGIEMU_ONLY.syx','8e1d9c4e384d30314255801d0e1ef70736a1f76ac1279a31f8e02d3285fe43ef'),('inputs/Digitone_and_Digitone_Keys_OS1.44.syx','d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659')]:assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
Path('outputs/Digitone-E02-audio-isolation-summary.json').write_text(json.dumps(summary,indent=2))
Path('outputs/Digitone-E02-audio-isolation.md').write_text('''# E02 audio isolation using the saved user session

The uploaded crackling symptom was reproduced using background DSP rendering, the mode used by Digiemu's live GUI. The same saved modified session, notes and sound are clean with synchronous DSP rendering. Neither source firmware nor the user's installed app/session files were modified by these tests; their files were copied into the workspace.

Matched simple track-1 and factory arp workloads produce byte-identical stock/E02 audio, including controls that restore the seven runtime hooks after E02 startup and install those hooks after stock startup. A nonchromatic factory arp test changes pitches as intended without the dense boundary discontinuities.

## Actual saved modified session

| Execution | Large sample jumps | At strongest 32-frame boundary |
| --- | ---: | ---: |
| E02, synchronous DSP | 0 | 0 |
| E02, background DSP | 256 | 256 |
| Seven arp hooks disabled, background DSP | 250 | 250 |
| All nine modified sites restored to stock, background DSP | 249 | 249 |
| E02, background DSP plus voice-read barrier | 0 | 0 |

Counts use the same 0.02 full-scale jump threshold as the initial WAV analysis. The workload is 2.8 emulated seconds including STOP/PLAY controls. Host-thread scheduling makes the unsynchronized counts nondeterministic.

The main render starts DMA channel 47 at 0x4009d1ac to read the DSP voice buffer at 0x100003a0. A test-only host wait at that instruction ensures the background DSP render completes before copying its output. This restores **byte-identical PCM** to the clean synchronous E02 run, not merely fewer detected jumps. Stock retains the same pitches and has no large discontinuities with the barrier, but its PCM differs from the synchronous stock control. That remaining scheduling difference needs validation before packaging an emulator fix.

This localizes the observed discontinuity to threaded DSP handoff behavior in this engine/workload. Disabling the nine sites after loading does not erase earlier startup history, so it is not a universal startup proof. The user stock session has different note/effect settings from the modified session; its direct WAV comparison is not a matched control. The same-snapshot thread/barrier and hook-restoration tests establish the stronger result.

## Scale-locking confirmation

From the user's saved pattern, actual arp pitch outputs with the seven hooks disabled are MIDI notes 60,61,64,66,60. E02 produces 60,60,64,65,60: C,Csharp,E,Fsharp,C becomes C,C,E,F,C. The clean audio exports keep the same pattern and sound and differ in hook configuration, making them suitable for the intended Ableton pitch comparison.

Clean files: `Digitone-user-scale-locked-clean.wav` and `Digitone-user-same-pattern-stock-pitch-clean.wav`. The second is a same-session stock-pitch control with the seven runtime hooks restored, not a fresh stock firmware boot.

## Remaining work

The voice-read barrier is currently a PC test harness change only. A separately packaged emulator/launcher fix still needs implementation and validation for live use. This result does not change E02 firmware, certify hardware timing or authorize physical flashing. Detailed cases and hashes are in `Digitone-E02-audio-isolation-summary.json`.
''')
print('Audio isolation and scale-lock checks pass; source firmware hashes unchanged')
