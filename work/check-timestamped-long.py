import json,pathlib
j=json.loads(pathlib.Path('outputs/Digitone-timestamped-DMA-long-comparison.json').read_text());r=j['runs'][0]
print('elapsed',j['elapsed_seconds']);print('counts',r['memory_model']['timestamped_payload']['counts']);print('queued',r['memory_model']['timestamped_payload']['active_channels'],r['memory_model']['timestamped_payload']['queued_events']);print('coherence',r['memory_model']['coherence_observations']);print('bytes',r['memory_model']['DMA_channel_bytes'])
