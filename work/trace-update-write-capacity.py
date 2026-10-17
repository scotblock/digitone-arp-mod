"""PC-only update loop and receiving-size branch probes. No flash writes."""
exec(open('work/trace-section-descriptor-storage.py').read().split('checks=[];cases=[]')[0])
RANGES.extend([(0x80003f6a,0x80003fda),(0x80002ba8,0x80002cc4),(0x400d9fca,0x400d9fd8),(0x400da032,0x400da034),(0x80002af8,0x80002afa),(0x80002edc,0x80002f4a)])
class ProbeStop(Exception):pass
probe_source=run_source.replace('   self.steps.append(pc)', '''   self.steps.append(pc)
   if pc in getattr(self,'endpoints',[]):self.endpoint=pc;raise ProbeStop()
   if pc==0x400059c0:pc=self.get('(a7)+',4);continue
   if pc in (0x80002f48,0x80002edc,0x400edbbe,0x400edb42):
    sp=self.reg['a7'];argc=1 if pc in (0x80002f48,0x400edbbe) else 3
    self.calls.append((pc,[self.read(sp+4+j*4,4) for j in range(argc)]));pc=self.get('(a7)+',4);continue
   if pc==0x80002af8:
    sp=self.reg['a7'];dst=self.read(sp+4,4);count=self.read(sp+8,4);assert count==5
    for j,v in enumerate(self.jedec):self.write(dst+j,1,v)
    pc=self.get('(a7)+',4);continue''')
exec('if True:\n'+probe_source);Machine.run=run
class ProbeMachine(StorageMachine):
 def write(self,a,n,v):
  if a==0xfc04c01c:return
  return super().write(a,n,v)
checks=[];cases=[]
def check(name,condition):assert condition,name;checks.append(name)
def stoprun(m,pc):
 try:m.run(pc)
 except ProbeStop:return
 raise AssertionError('expected boundary')
stock_size=inspection['container_bytes'] if 'container_bytes' in inspection else 1102032
for length in [0,1,511,512,513,stock_size,stock_size+4096,0x1dfff8,0x300000,0x300001]:
 m=ProbeMachine(table());m.calls=[];m.endpoints=[0x80003fd8];m.reg['d4']=length;stoprun(m,0x80003f6a)
 erase=[v[0] for pc,v in m.calls if pc==0x80002f48];program=[v for pc,v in m.calls if pc==0x80002edc]
 check(f'{length}: erase count',len(erase)==(length+0x3ffff)//0x40000)
 check(f'{length}: program count',len(program)==(length+511)//512)
 check(f'{length}: erase addresses',erase==list(range(0x80000,0x80000+len(erase)*0x40000,0x40000)))
 check(f'{length}: program addresses/source',all(v==[0x80000+j*512,512,0x40000008+j*512] for j,v in enumerate(program)))
 cases.append({'kind':'actual bootstrap update loops to simulated erase/program boundaries','container_length':length,'erase_count':len(erase),'erase_end_exclusive':hex(0x80000+len(erase)*0x40000),'program_count':len(program),'program_end_exclusive':hex(0x80000+len(program)*512),'instructions':len(m.steps)})
for manufacturer,device,extra,page,erase in [(1,0x2018,0,512,0x40000),(1,0x2018,1,256,0x10000),(0xef,0x4017,0,256,0x10000),(0xef,0x4018,0,256,0x10000),(0xc2,0x2017,0,256,0x10000),(0xc2,0x2018,0,256,0x10000),(0x9d,0x6017,0,256,0x10000)]:
 m=ProbeMachine(table());m.map(0x800070d4,20);m.map(0x80007708,4);m.calls=[];m.jedec=bytes([manufacturer,device>>8,device&255,0,extra]);m.endpoints=[]
 m.write(0x800070dc,4,0xffffffff);m.write(0x800070e0,4,0xffffffff)
 result=m.run(0x80002ba8)
 check(f'JEDEC {manufacturer:x}/{device:x}/{extra}: recognized geometry',result==0 and m.read(0x800070e0,4)==page and m.read(0x800070dc,4)==erase)
 check(f'JEDEC {manufacturer:x}/{device:x}/{extra}: manufacturer field',m.read(0x800070d8,4)==manufacturer)
 cases.append({'kind':'actual identification branches; supplied JEDEC bytes at hardware-query boundary','jedec':m.jedec.hex(),'page_bytes':page,'erase_bytes':erase,'manufacturer_field':m.read(0x800070d8,4),'instructions':len(m.steps)})
for length in [stock_size,stock_size+4096,0x1dfff8,0x1dfff9,0x1e0000]:
 m=ProbeMachine(table());m.map(0x41924418,4);m.write(0x41924418,4,0x1e0000);m.reg['d0']=length;m.calls=[];m.endpoints=[0x400d9fd6,0x400da032];stoprun(m,0x400d9fca)
 accepted=m.endpoint==0x400d9fd6
 check(f'{length}: actual receiving-size decision',accepted==(length+7<0x1e0000))
 cases.append({'kind':'actual main receiving-size comparison branch; positive lengths','length':length,'configured_capacity':0x1e0000,'accepted':accepted,'endpoint':hex(m.endpoint)})
RANGES.extend([(0x4008ad76,0x4008ad9c),(0x4008ae3c,0x4008aec4),(0x400edbbe,0x400edbc0),(0x400edb42,0x400edb44),(0x400059c0,0x400059c2)])
for length in [stock_size,stock_size+4096,0x1dfff8]:
 m=ProbeMachine(table());m.map(0x4bc47084,4);m.map(0x401fa938,8);m.write(0x4bc47084,4,length);m.reg['a6']=0x30003000;m.calls=[];m.endpoints=[0x4008aec2];stoprun(m,0x4008ad76)
 erase=[v[0] for pc,v in m.calls if pc==0x400edbbe];program=[v for pc,v in m.calls if pc==0x400edb42]
 check(f'main {length}: erase count and addresses',erase==list(range(0x80000,0x80000+((length+0x3ffff)//0x40000)*0x40000,0x40000)))
 check(f'main {length}: program count and source',len(program)==(length+511)//512 and all(v==[0x80000+j*512,512,0x4bc47088+j*512] for j,v in enumerate(program)))
 cases.append({'kind':'actual main update loops to simulated erase/program boundaries; display calls skipped','length':length,'erase_count':len(erase),'erase_end_exclusive':hex(0x80000+len(erase)*0x40000),'program_count':len(program),'instructions':len(m.steps)})
check('small extension keeps stock erase count',cases[5]['erase_count']==cases[6]['erase_count']==5)
check('stock erase ends before occupied 380000',int(cases[5]['erase_end_exclusive'],16)<0x380000)
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
check('original SysEx unchanged',hashlib.sha256(syx.read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
pathlib.Path('outputs/Digitone-update-write-capacity-results.json').write_text(json.dumps({'check_count':len(checks),'checks':checks,'cases':cases,'limits':['Hardware queries and erase/program operations are simulated boundaries.','No complete receive/session or update execution.','No physical device capacity identified.','No firmware modification or flashable output.']},indent=2))
print(json.dumps({'checks':len(checks),'cases':len(cases),'stock_container_bytes':stock_size}))


