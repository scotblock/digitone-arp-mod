# Apply the already tested current copy guard to a disposable isolated machine.
# Existing initializer/layout is identical; do not clear any live metadata here.
base_prepared=prepared
def prepared():
 m=base_prepared();atomic=Path('work/os144/PC_ONLY-atomic-live-copy.bin').read_bytes();m.load(atomic,0x47be3600);m.install_isa_patches_scoped(atomic,0x47be3600)
 for site,opcode in [(0x400ff5f6,'4eb9'),(0x400ff5a6,'4bf9')]:
  assert bytes(m.uc.mem_read(site,6))==bytes.fromhex(opcode)+u32(LIVE['layout']['live_copy']['address']);m.uc.mem_write(site,bytes.fromhex(opcode)+u32(0x47be3600))
 return m
