import pathlib,json
s=pathlib.Path('work/summarize-shared-memory-long.py').read_text().replace('Digitone-shared-memory-long-comparison.json','Digitone-timestamped-DMA-long-comparison.json').replace('Digitone-shared-memory-long-summary.json','Digitone-timestamped-DMA-long-summary.json')
s=s.replace("'model_checks':json.loads((out/'Digitone-shared-memory-model-checks.json').read_text())", "'model_checks':json.loads((out/'Digitone-timestamped-DMA-visibility-checks.json').read_text())")
pathlib.Path('work/summarize-timestamped-DMA-long.py').write_text(s)
s=pathlib.Path('work/verify-shared-memory-pitches.py').read_text().replace('Digitone-shared-memory-long-summary.json','Digitone-timestamped-DMA-long-summary.json').replace('Digitone-shared-memory-long-comparison.json','Digitone-timestamped-DMA-long-comparison.json')
pathlib.Path('work/verify-timestamped-DMA-pitches.py').write_text(s)
print('Summary and pitch comparison prepared for the completed runs.')
