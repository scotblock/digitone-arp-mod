from pathlib import Path
p=Path('work/trace-synth-arp-MIDI-output.py').read_text()
p=p.replace('E06-PC-candidate.syx','E07-PC-candidate.syx').replace('Digitone-E06-PC-startup-comparison.json','Digitone-E07-PC-startup-comparison.json').replace("=='E06_restored'","=='E07_restored'").replace('Digitone-E06-PC-candidate-layout.json','Digitone-E07-PC-candidate-layout.json').replace('E06-PC-payload.bin','E07-PC-payload.bin')
p=p.replace("'failure':None}","'failure':None,'counts':{}}")
p=p.replace("out['events'].append(event)","key=hex(pc);out['counts'][key]=out['counts'].get(key,0)+1\n  if out['counts'][key]<=24:out['events'].append(event)")
p=p.replace('[0x40002a3a,0x40002b6e,0x40002c08]','[0x40002a3a,0x40002b6e,0x40002c08,0x400eabb4,0x400eaab0,0x400edbc2,0x400f3c1a,0x400f0578,0x4009755e,0x40098116]')
p=p.replace("after_ms=1000);mark('MIDI-track playback')","after_ms=5000);mark('MIDI-track playback')")
p=p.replace('Digitone-synth-arp-MIDI-output-discovery.json','Digitone-E08-MIDI-track-stock-path.json')
Path('work/trace-E08-MIDI-track-stock-path.py').write_text(p)
