"""Execute recovered SRAM descriptor and copied SPI reader, simulated MMIO only."""
exec(open('work/try-full-early-allocator.py').read().split('m=AllocMachine();')[0])
import json,hashlib
boot=pathlib.Path('work/section-2.bin').read_bytes();linked=0x800003fc
spi_blob=boot[0x80007300-linked:0x80007300-linked+0x158]
RANGES.extend([(0x80005a50,0x80005b4e),(0x8000f010,0x8000f100),(0x800005d8,0x80000654)])
def mapped_fetch(pc):
 if 0x8000f000<=pc<0x8000f158:return spi_blob[pc-0x8000f000:pc-0x8000f000+16]
 if linked<=pc<linked+len(boot):return boot[pc-linked:pc-linked+16]
 return b[pc-base:pc-base+16]
class ReadComplete(Exception):pass
run_source=source.replace('b[pc-base:pc-base+16]','mapped_fetch(pc)').replace('range(100000)','range(500000)')
run_source=run_source.replace('   self.steps.append(pc)',"   self.steps.append(pc)\n   if pc==0x8000f010:self.start_read()\n   if pc==getattr(self,'stop',None):raise ReadComplete()")
run_source=run_source.replace("   elif m=='swap':","   elif m=='movec':self.controls.append((pc,int.from_bytes(i.bytes[2:4],'big')&4095,self.get(ops[0],4)))\n   elif m=='nop':pass\n   elif m=='swap':")
exec('if True:\n'+run_source);Machine.run=run
inspection=json.loads(pathlib.Path('work/inspection.json').read_text())
sections=inspection['sections'];header=bytes.fromhex(inspection['header_hex'])
def table(length=None,offset=None,dest=None):
 data=bytearray(header)
 for sec in sections:
  values=[sec['id'],int(sec['offset'],16),sec['stored_bytes'],int(sec['destination'],16)]
  if sec['id']==3:
   if length is not None:values[2]=length
   if offset is not None:values[1]=offset
   if dest is not None:values[3]=dest
  for v in values:data.extend(v.to_bytes(4,'big'))
 return bytes(data)
class StorageMachine(Machine):
 def __init__(self,flashdata):
  super().__init__();self.map(0x30000000,0x4000);self.map(0x80007a30,0x40);self.map(0x29000000,64);self.flash={0x80000+j:v for j,v in enumerate(flashdata)};self.reads=[];self.commands=[];self.controls=[];self.spi_cursor=0
 def start_read(self):
  sp=self.reg['a7'];raw=self.read(sp+4,4);length=self.read(sp+8,4);dest=self.read(sp+12,4)
  self.reads.append({'address':hex(raw),'wire_address':hex(raw&0xffffff),'bytes':length,'destination':hex(dest)});self.spi_base=raw&0xffffff;self.spi_cursor=-4
  if getattr(self,'stop_on_main',False) and dest==0x40200000:raise ReadComplete()
 def read(self,a,n):
  if a==0xfc05c02c:return 0x10000010 # ready/completed, one receive word available
  if a==0xfc05c000:return 0
  if a==0xfc05c038:
   cursor=self.spi_cursor;self.spi_cursor+=1
   return 0 if cursor<0 else self.flash.get(self.spi_base+cursor,((self.spi_base+cursor)*73+19)&255)
  if linked<=a and a+n<=linked+len(boot) and all(a+j not in self.mem for j in range(n)):return int.from_bytes(boot[a-linked:a-linked+n],'big')
  return super().read(a,n)
 def write(self,a,n,v):
  if 0xfc05c000<=a<0xfc05c040:
   if a==0xfc05c034:self.commands.append(v&0xffffffff)
   return
  return super().write(a,n,v)
checks=[];cases=[]
def check(name,ok):assert ok,name;checks.append(name)
stock=next(sec for sec in sections if sec['id']==3)
for length in [stock['stored_bytes'],stock['stored_bytes']+4096,0x200000,0x7fffffff,0x80000000]:
 m=StorageMachine(table(length=length));result=m.run(0x80005a88,(3,0x29000010))
 record=[m.read(0x29000010+j*4,4) for j in range(4)]
 check(f'descriptor {length:x}: matching record accepted',result==1 and record==[3,int(stock['offset'],16),length,int(stock['destination'],16)])
 check(f'descriptor {length:x}: reads are bounded by scanned records',[r['bytes'] for r in m.reads]==[32,16,16,16])
 cases.append({'kind':'descriptor','stored_length':length,'record':record,'instructions':len(m.steps),'reads':m.reads})
m=StorageMachine(table());m.write(0x29000010,4,0xa5a5a5a5);result=m.run(0x80005a88,(99,0x29000010))
check('missing ID stops after header count and returns zero',result==0 and len(m.reads)==7)
check('missing ID leaves output unchanged',m.read(0x29000010,4)==0xa5a5a5a5)
for length in [stock['stored_bytes'],stock['stored_bytes']+4096]:
 m=StorageMachine(table(length=length));m.stop_on_main=True
 try:m.run(0x800005d8)
 except ReadComplete:pass
 else:raise AssertionError('main read boundary not reached')
 last=m.reads[-1]
 check(f'main read {length}: descriptor location plus container base',last['address']==hex(0x80000+int(stock['offset'],16)))
 check(f'main read {length}: full stored length forwarded',last['bytes']==length and last['destination']=='0x40200000')
 cases.append({'kind':'main caller to storage boundary','stored_length':length,'instructions':len(m.steps),'reads':m.reads,'limit':'stopped before large payload transfer; not depacking actual image'})
for address,length in [(0x880000,0),(0x880000,1),(0x880000,17),(0x01880000,17),(0x880000,4096),(0x880000,0x80000000)]:
 effective=length if length<0x80000000 else 0
 m=StorageMachine(table());m.map(0x29100000,effective+32)
 for j in range(effective+32):m.write(0x29100000+j,1,0xa5)
 m.run(0x8000f010,(address,length,0x29100010))
 expected=bytes(((address&0xffffff)+j)*73+19&255 for j in range(effective))
 check(f'SPI {address:x}/{length}: exact simulated read bytes',bytes(m.read(0x29100010+j,1) for j in range(effective))==expected)
 check(f'SPI {address:x}/{length}: destination guards unchanged',m.read(0x2910000f,1)==0xa5 and m.read(0x29100010+effective,1)==0xa5)
 check(f'SPI {address:x}/{length}: command emits 24-bit address',[v&255 for v in m.commands[:4]]==[3,(address>>16)&255,(address>>8)&255,address&255])
 cases.append({'kind':'actual SPI reader with simulated hardware','address':hex(address),'length':length,'instructions':len(m.steps),'first_commands':[hex(v) for v in m.commands[:4]],'data_receive_count':m.spi_cursor})
for mode in ['offset_wrap','missing_main']:
 data=bytearray(table(offset=0xfff90000 if mode=='offset_wrap' else None))
 if mode=='missing_main':data[32+2*16:36+2*16]=(99).to_bytes(4,'big')
 m=StorageMachine(data);m.stop_on_main=True
 try:m.run(0x800005d8)
 except ReadComplete:pass
 else:raise AssertionError(mode)
 last=m.reads[-1]
 if mode=='offset_wrap':check('main offset addition wraps without local rejection',last['address']=='0x10000' and last['bytes']==stock['stored_bytes'])
 else:check('missing descriptor return is unchecked by main caller',last['address']=='0x80000' and last['bytes']==0)
 cases.append({'kind':mode,'instructions':len(m.steps),'main_read_boundary':last,'limitation':'missing-main descriptor slots begin zero in this fixture; device stack contents may differ'})
# Preserve provenance anchors for the copied code and matching entries.
anchors={0x80005a88:'4fefffdc48d7043c',0x80000602:'4eb980005a88',0x80000efc:'41f98000730043f98000f000',0x80000f08:'22d8b1fc8000745665f6'}
for addr,h in anchors.items():check(f'mapping anchor {addr:x}',boot[addr-linked:addr-linked+len(bytes.fromhex(h))].hex()==h)
check('copied storage entry is same provided bytes',spi_blob[16:22].hex()=='2039fc05c000')
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
check('original SysEx unchanged',hashlib.sha256(syx.read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
check('main image unchanged',hashlib.sha256(b).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
result={'checks':checks,'cases':cases,'firmware_modified':False,'mapping':{'decoded_prefix_bytes':4,'linked_image_start':'0x80000400','section2_offset0_mapping':'0x800003fc','storage_source':'0x80007300..0x80007456','storage_copy_destination':'0x8000f000','copied_bytes':0x158,'evidence':'descriptor, copy helper, storage caller, and blob-copy anchors agree under this mapping; original load/copy into SRAM still not executed'},'limits':{'descriptor_record_bytes':16,'descriptor_scan_count':'cached header word at +0x1c; no independent local maximum','wire_address_bits':24,'read_length':'signed positive comparison; high-bit lengths skip data loop','destination_bounds_check':False,'poll_timeout':False,'hardware_model':'always ready, completes, supplies flash-table bytes or deterministic payload bytes'},'remaining':['device flash capacity/partition and updater write limits','actual SRAM installation/handoff entry','actual modified compressed-stream overlap and full boot sequence','storage hardware errors/timeouts and alternate boot paths']}
pathlib.Path('outputs/Digitone-section-descriptor-storage-results.json').write_text(json.dumps(result,indent=2))
lines=[]
for start,end in [(0x80005a50,0x80005b08),(0x800005d8,0x80000654),(0x80000efc,0x80000f12),(0x8000f010,0x8000f100)]:
 data=spi_blob[start-0x8000f000:end-0x8000f000] if start>=0x8000f000 else boot[start-linked:end-linked]
 for ins in md.disasm(data,start):lines.append(f'{ins.address:08x} {ins.bytes.hex():18} {ins.mnemonic:10} {ins.op_str}')
pathlib.Path('outputs/Digitone-section-descriptor-storage-instructions.txt').write_text('\n'.join(lines))
print('PASS',len(checks),'checks;',len(cases),'cases; descriptor and copied storage reader recovered; firmware unchanged')
