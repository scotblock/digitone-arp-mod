from pathlib import Path
s=Path('work/test-PC-pattern-retained-provenance.py').read_text()
needle="source=source.replace('  for entry,label in',insert+'  for entry,label in')"
add="""insert+='''  report['owner_field_writes']=[];report['owner_setter_entries']=[];report['owner_field_reads']=[];report['owner_frees']=[]
  def fieldwrite(u,access,a,n,v,d):
   canonical=0x40000000+(a-0x40000000)%0x08000000
   if canonical<0x41a720f4 and canonical+n>0x41a720f0:report['owner_field_writes'].append({'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(a),'bytes':n,'value':hex(v),'before':hex(rd(u,0x41a720f0)),'ms':s.now_ms()})
  for alias in range(8):u.hook_add(UC_HOOK_MEM_WRITE,fieldwrite,begin=0x41a720ef+alias*0x08000000,end=0x41a720f4+alias*0x08000000)
  def setter(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);args=struct.unpack('>IIII',u.mem_read(sp,16))
   if args[1]==0x41a720d0:report['owner_setter_entries'].append({'pc':hex(pc),'caller':hex(args[0]),'object':hex(args[1]),'arg2':hex(args[2]),'arg3':hex(args[3]),'prior_field':hex(rd(u,args[1]+32)),'ms':s.now_ms()})
  for pc in [0x40152ffe,0x40153060,0x40153078]:s.at(pc,setter)
  def readfield(u,pc,n,d):
   obj=u.reg_read(UC_M68K_REG_A2)
   if obj==0x41a720d0:report['owner_field_reads'].append({'pc':hex(pc),'value':hex(rd(u,obj+32)),'ms':s.now_ms()})
  s.at(0x401533bc,readfield)
  def freed(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);ptr=rd(u,sp+4)
   if ptr in [0x41a720d0,0x407ef9f4]:report['owner_frees'].append({'pc':hex(pc),'pointer':hex(ptr),'caller':hex(rd(u,sp)),'ms':s.now_ms()})
  s.at(0x400e96cc,freed)
'''
source=source.replace('  for entry,label in',insert+'  for entry,label in')"""
assert needle in s;s=s.replace(needle,add).replace('Digitone-E04-PC-pattern-retained-provenance-runtime.json','Digitone-E04-PC-pattern-field-lifetime-runtime.json')
exec(compile(s,'pattern-field-lifetime','exec'))
