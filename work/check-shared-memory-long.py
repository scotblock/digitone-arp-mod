import json,pathlib
j=json.loads(pathlib.Path('outputs/Digitone-shared-memory-long-comparison.json').read_text());r=j['runs'][0]
print('stock completed',r['ms'],'maintenance',r['memory_model']['maintenance'],'counts',r['memory_model']['counts'],'DMA',r['memory_model']['DMA_channel_bytes'],'coherence',r['memory_model']['coherence_observations'],'flags',r['decoder_flags'][:3])
