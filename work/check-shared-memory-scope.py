import pathlib
p=pathlib.Path('work/shared_memory_timing.py')
print('model bytes',p.stat().st_size)
print('Known limitation: DMA payload is copied at launch; only completion status and DDR resource ownership are delayed.')
