from pathlib import Path
import json,hashlib
cases={mode:json.loads(Path('outputs/Digitone-OS1.44-fallback-continuous-'+mode+'.json').read_text()) for mode in ['valid','bad_magic','bad_pointer']}
comparison=json.loads(Path('outputs/Digitone-OS1.44-fallback-stock-playback-comparison.json').read_text())
assert comparison['passed'] and all(r['passed'] for r in cases.values())
allowed_memset={0x400fbb3c,0x400fbb3e,0x400fbb40,0x400fbb42}
for mode,r in cases.items():
 for pc,row in r['reservation_writers'].items():
  pc=int(pc,16)
  assert 0x4029c4b0<=pc<0x4029c50e or 0x47be0000<=pc<0x47be08a4 or 0x47f40000<=pc<0x47f40118 or (mode=='valid' and pc in allowed_memset)
  assert 0x47be0000<=int(row['min'],16)<int(row['max'],16)<=0x47be1b74
r=cases['valid'];dma={};scatter=0
for key,item in r['dma_descriptors'].items():
 row=dma.setdefault(item['channel'],{'descriptors':0,'DDR_start':None,'DDR_end':None});row['descriptors']+=1
 for e in item['envelopes']:
  assert not e['overlaps_reservation']
  lo=int(e['canonical_start'],16);hi=lo+int(e['end'],16)-int(e['start'],16)
  if 0x40000000<=lo<0x48000000:
   row['DDR_start']=hex(min(lo,int(row['DDR_start'],16) if row['DDR_start'] else lo));row['DDR_end']=hex(max(hi,int(row['DDR_end'],16) if row['DDR_end'] else hi))
 if int(key.split(':',1)[1].split(',')[-1],16)&16:scatter+=1
additional=[{'site':'0x4008cc4a','stack_base':'0x40320ebc','bytes':0x4000,'end':'0x40324ebc'}, {'site':'0x400eb884','stack_base':'0x4199ffb8','bytes':0x8000,'end':'0x419a7fb8'}, {'site':'0x400f8e1a','stack_base':'0x419cade4','bytes':0x4000,'end':'0x419cede4'}]
for t in additional:assert int(t['end'],16)<0x47be0000
out={'PC_only':True,'passed':True,'startup_from':'Direct MAIN reset with an initialized PC +Drive copy, not a fresh factory initialization or loader prefix','fallback_modes':{k:{f:v[f] for f in ['passed','startup_entries','pointer_at_UI','pointer_after_playback','helper_hits','audio_bytes','top_stack_min_write']} for k,v in cases.items()},'stock_pitch_comparison':comparison,'runtime_tasks':r['tasks'],'additional_literal_stack_ranges':additional,'dma_channels':dma,'scatter_gather_descriptors_observed':scatter,'reservation_writers_all_accounted_for':True,'heap_boundary_cases':json.loads(Path('outputs/Digitone-OS1.44-heap-bounds-checks.json').read_text()),'preserved_files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx'),Path('work/os144/packed-context-overlay.bin')]},'limits':['Scratch fallback code at 47f40000 is not integrated into the existing copier/helper image.','Snapshot handoffs preserve machine state but are emulator stages, not a physical uninterrupted power-on run. Hooks/timers use the existing instruction-timed engine and host accelerations; physical timing/cache coherence untested.','CPU write hooks account for executed guest stores, not arbitrary host/device DMA writes; DMA evidence is descriptor/range analysis of observed configurations and software starts. No scatter-gather descriptor was observed.','Static stack inventory plus constructed task ranges and observed high-stack stores is not worst-case interrupt nesting or stack overflow proof. Unexercised modes/project loads/new DMA configurations are outside the measured workload.','Captured-state heap cases use intact initial allocator metadata; they do not prove every corrupted metadata/overflow path.','Fallback and stock-site replays have identical pitches but differing PCM hashes; no audio equivalence or physical deadline claim.']}
Path('outputs/Digitone-OS1.44-fallback-and-RAM-completion-checks.json').write_text(json.dumps(out,indent=2));print('PASS: 3 continuous cases, 2 stock-pitch controls, 7 heap cases;',len(r['tasks']),'runtime stacks;',len(r['dma_descriptors']),'DMA descriptors')
