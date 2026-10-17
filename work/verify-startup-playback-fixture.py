import pathlib
ns={};s=pathlib.Path('work/test-copied-table-read-witness.py').read_text()
exec(s[:s.index('exec(compile(body')],ns)
body=ns['body']
for call in ['uc.mem_write(RAM,blob)','uc.mem_write(PTR,bytes(0xb74))','uc.mem_write(PTR,u32(BSS-0x14100))','uc.mem_write(BSS,struct.pack','uc.mem_write(pc,bytes.fromhex(op)']:
 assert call not in body,call
print('Verified: playback contains no code/table/header/hook reinjection.')
