from pathlib import Path
import json
cfg=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text())
names=set(json.loads(Path('work/os144/PC_ONLY-synth-arp-MIDI-layout.json').read_text())['regions'][i]['name'] for i in range(11))
mid={'base':0x47be0000,'state':cfg['MIDI_state'],'records':cfg['MIDI_records'],'markers':cfg['MIDI_markers'],'regions':[r for r in cfg['regions'] if r['name'] in names],'tail':{'base':0x47be0c00,'bytes':146}}
Path('work/os144/E07-MIDI-adapter.json').write_text(json.dumps(mid,indent=2))
s=Path('work/test-PC-synth-arp-MIDI-contracts.py').read_text().replace("Path('work/test-E06-degree-contracts.py').read_text()", "Path('work/test-E06-degree-contracts.py').read_text().replace('E06','E07')")
s=s.replace('PC_ONLY-synth-arp-MIDI-layout.json','E07-MIDI-adapter.json').replace('PC_ONLY-synth-arp-MIDI-code.bin','E07-PC-payload.bin').replace("Path('work/os144/PC_ONLY-synth-arp-MIDI-tail.bin').read_bytes()", "Path('work/os144/E07-PC-payload.bin').read_bytes()[0xc00:0xc00+146]")
s=s.replace('ON=B+0x300;OFF=B+0x200;PUMP=B+0x500', "ON=cfg['MIDI_entries']['ON'];OFF=cfg['MIDI_entries']['OFF'];PUMP=cfg['MIDI_entries']['PUMP']")
s=s.replace('Digitone-synth-arp-MIDI-contracts.json','Digitone-E07-MIDI-contracts.json').replace("'Private code/state are host installed; native startup integration remains unimplemented.'", "'Relocated packaged helper contracts use isolated native frames; native copying is checked separately.'")
Path('work/test-E07-MIDI-contracts.py').write_text(s)
for old in ['package-E06-PC-candidate.py','verify-E06-PC-container.py','test-E06-PC-startup.py','test-E06-PC-diagnostic-reset.py']:
 Path('work/'+old.replace('E06','E07')).write_text(Path('work/'+old).read_text().replace('E06','E07'))
