import pathlib
s=pathlib.Path('work/test-DMA-completion-native.py').read_text().replace('from shared_memory_timing import MemoryTiming','from timestamped_dma import TimestampedMemory as MemoryTiming').replace("ev={'edma_sw_bank':bank}","ev={'edma_sw_bank':bank},sources=()")
s=s.replace('Digitone-DMA-completion-native-check.json','Digitone-timestamped-DMA-native-check.json')
pathlib.Path('work/test-timestamped-DMA-native.py').write_text(s)
s=pathlib.Path('work/compare-shared-memory-runs.py').read_text().replace('from shared_memory_timing import MemoryTiming','from timestamped_dma import TimestampedMemory as MemoryTiming').replace('instant DMA payload copy with delayed DONE','timestamped DMA payload beats and completion').replace('Existing SSI bulk-capture model; not physical sample-by-sample bus timing','Frame-level SSI capture; software DMA payload at modeled beat boundaries')
pathlib.Path('work/compare-timestamped-DMA-runs.py').write_text(s)
