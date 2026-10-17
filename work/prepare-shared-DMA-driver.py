import pathlib
p=pathlib.Path('work/shared_dma_arbiter.py');s=p.read_text();a=s.index('    def walk(');s=s[:a]+'\n'.join(line[3:] if line.startswith('   ') else line for line in s[a:].splitlines())+'\n';p.write_text(s)
# Driver, same workload with the new shared module.
s=pathlib.Path('work/compare-timestamped-DMA-runs.py').read_text().replace('from timestamped_dma import TimestampedMemory as MemoryTiming','from shared_dma_arbiter import SharedDmaMemory as MemoryTiming');pathlib.Path('work/compare-shared-DMA-arbiter.py').write_text(s)
