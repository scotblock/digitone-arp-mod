from pathlib import Path
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from capstone import Cs,CS_ARCH_M68K,CS_MODE_M68K_040,CS_MODE_BIG_ENDIAN
b=Path('work/os144/PC_ONLY-E04-ISA-corrected-payload.bin').read_bytes()
l=json.loads(Path('work/packed-context-build.json').read_text())['layout']
md=Cs(CS_ARCH_M68K,CS_MODE_M68K_040|CS_MODE_BIG_ENDIAN)
lines=[]
for name in ['snapshot','slot','copy','first_copy','allocate_clear','begin','cancel','commit','read','resolve','candidate_store','pitch','before','after','caller_commit']:
 p=l[name]['address'];end=p+l[name]['size'];lines.append('\n'+name)
 while p<end:
  ins=cfisa.decode(lambda off:int.from_bytes(b[p-0x47be0000+off:p-0x47be0000+off+2],'big'),p)
  raw=b[p-0x47be0000:p-0x47be0000+ins.length];decoded=list(md.disasm(raw,p));pretty=' '.join(x.mnemonic+' '+x.op_str for x in decoded)
  lines.append(f'{p:08x} {raw.hex():16} {ins.op:8} {pretty}');p+=ins.length
Path('work/PC-context-helper-disassembly.txt').write_text('\n'.join(lines))
print('\n'.join(lines))
