import json,pathlib
j=json.loads(pathlib.Path('outputs/Digitone-timestamped-DMA-pilot.json').read_text());r=j['runs'][0]
print('elapsed',j['elapsed_seconds'],'payload',r['memory_model']['timestamped_payload']['counts'],'coherence',r['memory_model']['coherence_observations'],'DMA',r['memory_model']['DMA_channel_bytes'])
