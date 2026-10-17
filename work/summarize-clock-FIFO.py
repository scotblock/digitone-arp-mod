import json,pathlib,hashlib
root=pathlib.Path('.')
r=json.loads((root/'outputs/Digitone-FIFO-audio-comparison.json').read_text())
assert r['failure'] is None,r['failure']
rows=[]
for x in r['runs']:
 f=x['memory_model']['FIFO'];d=x['render_deadline'];c=x['DMA_summary']
 assert c['final_clock_timer_gap_cycles']==147
 assert not any(f['counts'].get(k,0) for k in ('TX_underflow','RX_overflow','TX_overflow','RX_empty_read'))
 rows.append(dict(mode=x['mode'],total_ms=x['ms'],FIFO=f,render=d,DMA=c,pitch=x['pitch'],oracle=x['quantizer_calls'],clock=x['clock']))
native=json.loads((root/'outputs/Digitone-native-clock-FIFO-check.json').read_text())
assert native['failure'] is None,native['failure']
for x in native['runs']:
 assert x['input_clock_checks']==[0,0,0,0]
 assert x['DMA_summary']['final_clock_timer_gap_cycles']==0
 assert not any(x['memory_model']['FIFO']['counts'].get(k,0) for k in ('TX_underflow','RX_overflow','TX_overflow','RX_empty_read'))
s=dict(native_final_revision=native,longer_comparison_revision='before final input epoch correction; residual 147 cycles retained transparently',firmware_modified=False,core_hz_assumed=r['fsys_assumption_hz'],bus_hz_assumed=r['fsys_assumption_hz']//2,checks={'clock':12,'FIFO':34,'previous_audio':15},runs=rows,firmware_sha256=r['firmware_after'],code_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'work/fifo_audio_dma.py',root/'work/precise_audio_dma.py',root/'work/upstream/digiemu/emu/longrun.py',root/'work/upstream/digiemu/emu/session.py',root/'work/upstream/digiemu/emu/pit.py',root/'work/upstream/digiemu/emu/dtim.py']})
(root/'outputs/Digitone-clock-FIFO-summary.json').write_text(json.dumps(s,indent=2))
print(json.dumps([dict(mode=x['mode'],ms=x['total_ms'],fifo=x['FIFO'],render=x['render'],DMA=x['DMA']) for x in rows],indent=2))
