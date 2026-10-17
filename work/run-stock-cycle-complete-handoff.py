"""Matched stock-instruction control for complete timed native handoff."""
import pathlib
outer=pathlib.Path('work/run-cold-cycle-complete-handoff.py').read_text().split("exec(compile(source,'cold-cycle-complete-handoff','exec'))")[0]
exec(compile(outer,'stock-handoff-source','exec'))
source=source.replace("MODE='all'","MODE='stock'")
source=source.replace("OUT=pathlib.Path('outputs/Digitone-cycle-complete-handoff'","OUT=pathlib.Path('outputs/Digitone-stock-cycle-complete-handoff'")
# The prepared checkpoint is unique to this process and keeps stock hooks;
# the full-hook process uses its own untouched native preparation checkpoint.
source=source.replace('work/cache-native-prepared-handoff.snap','work/cache-native-prepared-stock-handoff.snap')
source=source.replace(" result['PC_runtime_extension_installed']=False", """ if MODE=='stock':
  for site in [0x4009344e,0x40093892]:uc.mem_write(site,stock[site-base:site-base+6])
 result['PC_runtime_extension_installed']=False""")
# In the restored stock checkpoint those two sites are already stock. Accept
# that explicitly rather than asserting that a discarded hook remains.
source=source.replace("  assert bytes(uc.mem_read(site,6))==bytes.fromhex(opcode)+u32(target)","  assert bytes(uc.mem_read(site,6)) in (bytes.fromhex(opcode)+u32(target),stock[site-base:site-base+6])")
exec(compile(source,'stock-cycle-complete-handoff','exec'))
