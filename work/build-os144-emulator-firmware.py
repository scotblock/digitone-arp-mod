from pathlib import Path
import sys,struct,hashlib,json,math
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections,decode_syx
from dt2.elz import depack_section
SOURCE=Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx')
OUT=Path('outputs/Digitone_OS1.44E01_SCALE_ARP_DIGIEMU_ONLY.syx')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(SOURCE.read_bytes())=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
stock=Path('work/os144/section-3.bin').read_bytes();blob=Path('work/os144/packed-context-overlay.bin').read_bytes()
assert sha(blob)=='0c5d58bf72828102b6f1fe19277e633ef97503fdcb727fd2a5f728ded2a8e299'
port=json.loads(Path('work/os144/helper-port.json').read_text());layout=port['layout']
BASE,RAM,PTR,BSS=0x40000400,0x47be0000,0x47be1000,0x47be1004
STAGE=BASE+len(stock);u32=lambda v:struct.pack('>I',v&0xffffffff)
a=bytearray();emit=lambda h:a.extend(bytes.fromhex(h))
emit('41f9'+u32(STAGE+256).hex()+'43f9'+u32(RAM).hex()+'203c'+u32(len(blob)//4).hex())
emit('22d853806600fffa43f9'+u32(PTR).hex()+'203c'+u32(0xb74//4).hex()+'720022c153806600fffa')
emit('23fc'+u32(BSS-0x14100).hex()+u32(PTR).hex())
for address,value in [(BSS,0x534c4332),(BSS+4,2),(BSS+8,0xb70)]:emit('23fc'+u32(value).hex()+u32(address).hex())
emit('4ef940001df4');assert len(a)<256
main=bytearray(stock);changes=[]
def patch(pc,expected,target,op):
 n=len(bytes.fromhex(expected));offset=pc-BASE
 assert main[offset:offset+n]==bytes.fromhex(expected),(hex(pc),main[offset:offset+n].hex())
 new=bytes.fromhex(op)+u32(target)+bytes.fromhex('4e71')*((n-6)//2)
 main[offset:offset+n]=new;changes.append({'site':hex(pc),'original':expected,'patched':new.hex()})
patch(0x40000538,'4eb940001df4',STAGE,'4eb9')
patch(0x400ffed0,'2f032f0241f9419ebe70',layout['reset']['address'],'4ef9')
for h in port['hooks']:patch(int(h['site'],16),h['stock_bytes'],h['helper'],'4eb9' if h['name'] in ['before','copy'] else '4ef9')
main.extend(a+bytes(256-len(a))+blob);main=bytes(main)
class Bits:
 def __init__(self):self.data=bytearray(8);self.left=0
 def bit(self,v):
  if not self.left:self.tag=len(self.data);self.data.append(0);self.left=8
  self.left-=1;self.data[self.tag]|=(v&1)<<self.left
 def byte(self,v):self.data.append(v)
 def gamma(self,v):
  for j in range(v.bit_length()-2,-1,-1):self.bit(v>>j&1);self.bit(j==0)
b=Bits()
for v in main:b.bit(1);b.byte(v)
b.bit(0);b.gamma(0x1000002);b.byte(255)
b.data[:8]=struct.pack('>II',len(b.data)-8,sum(b.data[8:])&0xffffffff)
assert depack_section(bytes(b.data))==main
c,entries=sections(SOURCE);c=c[:struct.unpack_from('>I',decode_syx(SOURCE))[0]]
container=bytearray(c[:min(o for _,o,_,_ in entries)])
container[12:24]=b'1.44E01'.rjust(12,b' ')
newentries=[]
for sid,off,n,dest in entries:
 container.extend(bytes((-len(container))%16));start=len(container)
 data=bytes(b.data) if sid==3 else c[off:off+n]
 container.extend(data);newentries.append((sid,start,len(data),dest))
for i,entry in enumerate(newentries):struct.pack_into('>IIII',container,32+i*16,*entry)
container.extend(bytes((-len(container))%16))
checksum=sum((i+1)^w[0] for i,w in enumerate(struct.iter_unpack('>I',container)))&0xffffffff
stream=struct.pack('>II',len(container),checksum)+container
count=math.ceil(len(stream)/101);stream+=bytes(count*101-len(stream))
first=bytearray(SOURCE.read_bytes()[1:15]);base=first[7];start=(first[8]<<7)|first[9];seq=first[10]
first[11:14]=bytes([(count>>14)&127,(count>>7)&127,count&127]);result=bytearray(b'\xf0'+first+b'\xf7')
for i in range(count):
 block=start+((seq+i)>>7);body=bytearray(b'\x00\x20\x3c\x0d\x00\x7e'+bytes([(block>>7)&127,block&127,(seq+i)&127]))
 chunk=stream[i*101:(i+1)*101]
 for k in range(0,101,7):
  group=chunk[k:k+7];body.append(sum(((v>>7)&1)<<(6-n) for n,v in enumerate(group)));body.extend(v&127 for v in group)
 assert len(body)==125
 body.append((base+sum(v^(base+j) for j,v in enumerate(body[6:])))&127)
 result.extend(b'\xf0'+body+b'\xf7')
first[6]=2;result.extend(b'\xf0'+first+b'\xf7');OUT.write_bytes(result)
decoded=decode_syx(OUT);size,storedsum=struct.unpack_from('>II',decoded)
assert size==len(container) and storedsum==checksum and decoded[8:8+size]==container and not any(decoded[8+size:])
cc,es=sections(OUT);assert depack_section(cc[next(e[1] for e in es if e[0]==3):next(e[1]+e[2] for e in es if e[0]==3)])==main
for old,new in zip(entries,es):
 if old[0]!=3:assert c[old[1]:old[1]+old[2]]==cc[new[1]:new[1]+new[2]]
Path('work/os144/emulator-build-main.bin').write_bytes(main)
report={'output':str(OUT.resolve()),'version':'1.44E01','emulator_only':True,'source_sha256':sha(SOURCE.read_bytes()),'output_sha256':sha(result),'main_sha256':sha(main),'main_bytes':len(main),'container_bytes':len(container),'data_packets':count,'copier_address':hex(STAGE),'copier_bytes':len(a),'helper_bytes':len(blob),'code_bytes':port['code_bytes'],'changes':changes,'checks':{'independent_decompression':True,'all_non_main_sections_unchanged':True,'container_checksum':True,'source_unchanged':True},'limits':['Experimental Digiemu build. Hardware flash and physical cache/timing behavior are unvalidated.','Startup copy/reset are newly connected in this image; emulator boot validation is recorded separately.','All-literal compression makes this image larger than stock.']}
Path('outputs/Digitone-OS1.44E01-build.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['output','output_sha256','main_bytes','container_bytes']},indent=2))
