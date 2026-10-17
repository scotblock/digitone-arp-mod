import pathlib
s=pathlib.Path('work/compare-shared-DMA-arbiter.py').read_text().replace('from shared_dma_arbiter import SharedDmaMemory as MemoryTiming','from precise_audio_dma import PreciseAudioMemory as MemoryTiming');pathlib.Path('work/compare-precise-audio-DMA.py').write_text(s)
