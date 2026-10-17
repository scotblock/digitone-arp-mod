import pathlib
s=pathlib.Path('work/test-cache-maintenance-native.py').read_text().replace('from shared_memory_timing import MemoryTiming','from timestamped_dma import TimestampedMemory as MemoryTiming').replace("ev={'edma_sw_bank':SimpleNamespace(_native=None,channels={})}","ev={'edma_sw_bank':SimpleNamespace(_native=None,channels={})},sources=()")
s=s.replace('Digitone-cache-maintenance-native-check.json','Digitone-timestamped-cache-maintenance-native-check.json')
pathlib.Path('work/test-timestamped-cache-maintenance-native.py').write_text(s)
