from pathlib import Path
original=Path('work/test-PC-restored-arp-DSP.py').read_text().split("exec(compile(s,'restored-live-arp-DSP','exec'))")[0]
exec(compile(original,'build-restored-workload','exec'))
s=s.replace('Digitone-E04-PC-restored-arp-DSP.json','Digitone-E04-PC-restored-sequencer-arp-DSP.json')
s=s.replace('Digitone-E04-PC-restored-','Digitone-E04-PC-restored-sequence-')
s=s.replace('Digitone-E04-PC-restored-sequence-sequencer-arp-DSP.json','Digitone-E04-PC-restored-sequencer-arp-DSP.json')
start=s.index('   mi=midi.MidiIn();');end=s.index("   r['DSP_after']=",start)
s=s[:start]+"   s.run_ms(4000)\n   s.tap(s.code('STOP'),hold_ms=100,after_ms=300)\n"+s[end:]
s=s.replace("   r['MIDI_delivery']={'received':mi.received,'delivered':mi.delivered,'interrupts':mi.raised}","   r['MIDI_delivery']={'received':0,'delivered':0,'interrupts':0}")
s=s.replace('   assert mi.received==mi.delivered','   assert not r[\'pending_returns\']')
s=s.replace("   if scenario=='scale':assert any(x['note']!=x['actual'] for x in r['quantize'])","   if scenario=='scale':assert any(x['note']!=x['actual'] for x in r['quantize']) and all(int(x['word'],16)>>31 for x in r['quantize'])")
exec(compile(s,'restored-sequencer-arp-DSP','exec'))
