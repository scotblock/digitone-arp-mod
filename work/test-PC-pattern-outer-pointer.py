from pathlib import Path
s=Path('work/test-PC-pattern-retained-provenance.py').read_text()
s=s.replace("source=source.replace('  for entry,label in',insert+'  for entry,label in')", """insert+='''  def dispatched(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);args=struct.unpack('>III',u.mem_read(sp,12));report.setdefault('outer_dispatch',[]).append({'caller':hex(args[0]),'object':hex(args[1]),'destination':hex(args[2]),'sp':hex(sp),'a6':hex(u.reg_read(UC_M68K_REG_A6))})
  s.at(0x401533aa,dispatched)
'''
source=source.replace('  for entry,label in',insert+'  for entry,label in')""")
s=s.replace('Digitone-E04-PC-pattern-retained-provenance-runtime.json','Digitone-E04-PC-pattern-outer-pointer-runtime.json')
exec(compile(s,'outer-pattern-provenance','exec'))
