"""Ephemeral extended MAIN through stock loader, then same-machine early copier."""
import pathlib,sys,json,hashlib,struct,time,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom,longrun
from dt2.container import sections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
stock=pathlib.Path('work/section-3.bin').read_bytes();bootstrap=pathlib.Path('work/section-2.bin').read_bytes()
blob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text());init=json.loads(pathlib.Path('work/native-overlay-startup.json').read_text())['initializer']
BASE,RAM,PTR,BSS=0x40000400,0x47be0000,0x47be1000,0x47be1004
STAGE=BASE+len(stock);u32=lambda x:struct.pack('>I',x)
a=bytearray();emit=lambda h:a.extend(bytes.fromhex(h))
emit('41f9'+u32(STAGE+0x100).hex()+'43f9'+u32(RAM).hex()+'203c'+u32(len(blob)//4).hex())
emit('22d853806600fffa43f9'+u32(PTR).hex()+'203c'+u32(0xb74//4).hex()+'720022c153806600fffa')
emit('23fc'+u32(BSS-0x14100).hex()+u32(PTR).hex())
for address,value in [(BSS,0x534c4332),(BSS+4,2),(BSS+8,0xb70)]:emit('23fc'+u32(value).hex()+u32(address).hex())
emit('4ef940001df4');copier=bytes(a);assert len(copier)<=256 and len(blob)%4==0
main=bytearray(stock)
for pc,name,op,length in [(0x40000538,None,'4eb9',6),(0x400f0504,None,'4ef9',10),(0x40093ef4,'producer_capture','4ef9',8),(0x400f0626,'allocate_clear','4ef9',6),(0x4009dda6,'before','4eb9',6),(0x4009de46,'caller_commit','4ef9',10),(0x4009df9a,'pitch_hook','4ef9',8)]:
 target=STAGE if pc==0x40000538 else init if pc==0x400f0504 else layout[name]['address']
 main[pc-BASE:pc-BASE+length]=bytes.fromhex(op)+u32(target)+bytes.fromhex('4e71')*((length-6)//2)
main.extend(copier+bytes(256-len(copier))+blob);main=bytes(main)
class Bits:
 def __init__(self):self.data=bytearray(8);self.remaining=0
 def bit(self,v):
  if not self.remaining:self.tag=len(self.data);self.data.append(0);self.remaining=8
  self.remaining-=1;self.data[self.tag]|=(v&1)<<self.remaining
 def byte(self,v):self.data.append(v)
 def gamma(self,v):
  for j in range(v.bit_length()-2,-1,-1):self.bit(v>>j&1);self.bit(j==0)
b=Bits()
for v in main:b.bit(1);b.byte(v)
b.bit(0);b.gamma(0x1000002);b.byte(255)
b.data[:4]=u32(len(b.data)-8);b.data[4:8]=u32(sum(b.data[8:])&0xffffffff)
c,secs=sections(syx);container=bytearray(c[:0x90]);entries=[]
for sid,off,n,dest in secs:
 container.extend(bytes((-len(container))%16));offnew=len(container)
 data=bytes(b.data) if sid==3 else c[off:off+n]
 container.extend(data);entries.append((sid,offnew,len(data),dest))
for i,entry in enumerate(entries):struct.pack_into('>IIII',container,0x20+i*16,*entry)
assert bootrom.CONTAINER_AT+len(container)<bootrom.FLASH_SIZE
flash=bytearray(b'\xff'*bootrom.FLASH_SIZE);flash[bootrom.CONTAINER_AT:bootrom.CONTAINER_AT+len(container)]=container
bootrom.flash_image=lambda *args,**kwargs:bytes(flash)
originalspin=longrun.spin
def fastspin(*args,**kwargs):kwargs['fast']=True;return originalspin(*args,**kwargs)
longrun.spin=fastspin
out={'firmware_modified':False,'ephemeral_image_only':True,'compression':'all literals plus NRV end marker; different compression from stock','main_bytes':len(main),'container_bytes':len(container),'blob_sha256':hashlib.sha256(blob).hexdigest(),'before':hashlib.sha256(syx.read_bytes()).hexdigest(),'events':[],'cache_writes':[],'copy_stores':0,'source_writers':{},'synchronizing_nop':[],'failure':None};start=time.monotonic()
def state(m):return {hex(k):hex(v) for k,v in m.ctlregs.items()}
def install(m,flash,dspi):
 uc=m.uc;m.install_isa_patches_scoped(main,BASE);m.install_isa_patches_scoped(blob[:1892],RAM)
 seen=set()
 def cache(uc,pc,n,d):
  raw=bytes(uc.mem_read(pc,4));word=int.from_bytes(raw[2:],'big')
  if raw[:2]!=b'\x4e\x7b' or word&4095 not in [2,4,5,6,7,12,13,14,15]:return
  reg=(UC_M68K_REG_A0 if word&0x8000 else UC_M68K_REG_D0)+((word>>12)&7)
  out['cache_writes'].append({'pc':hex(pc),'selector':hex(word&4095),'value':hex(uc.reg_read(reg))})
 for image,base in [(bootstrap[4:],0x80000400),(bootrom.container_section(syx,4)[8:],0x80000408),(main,BASE)]:
  for i in range(0,len(image)-3,2):
   pc=base+i
   if image[i:i+2]==b'\x4e\x7b' and int.from_bytes(image[i+2:i+4],'big')&4095 in [2,4,5,6,7,12,13,14,15] and pc not in seen:
    uc.hook_add(UC_HOOK_CODE,cache,begin=pc,end=pc);seen.add(pc)
 def hit(uc,pc,n,d):
  item={'pc':hex(pc),'controls':state(m),'SR':hex(uc.reg_read(UC_M68K_REG_SR)),'source_intact':bytes(uc.mem_read(STAGE+256,len(blob)))==blob};out['events'].append(item)
  if pc!=0x40000568:assert item['source_intact']
  if pc==0x4000053e:
   item['copied_exact']=bytes(uc.mem_read(RAM,len(blob)))==blob;assert item['copied_exact']
   item['header']=list(struct.unpack('>IIII',uc.mem_read(BSS,16)));assert item['header']==[0x534c4332,2,0xb70,0]
  if pc==0x40000568:
   item['copied_exact']=bytes(uc.mem_read(RAM,len(blob)))==blob;assert item['copied_exact']
   m.halt_vec=-2;uc.emu_stop()
 for pc in [STAGE,0x4000053e,0x40000568]:uc.hook_add(UC_HOOK_CODE,hit,begin=pc,end=pc)
 def sync(uc,pc,n,d):
  assert bytes(uc.mem_read(pc,2))==b'\x4e\x71'
  out['synchronizing_nop'].append({'pc':hex(pc),'controls':state(m)})
 uc.hook_add(UC_HOOK_CODE,sync,begin=0x80000632,end=0x80000632)
 def sourcewrite(uc,access,address,n,value,d):
  pc=hex(uc.reg_read(UC_M68K_REG_PC));out['source_writers'][pc]=out['source_writers'].get(pc,0)+1
 uc.hook_add(UC_HOOK_MEM_WRITE,sourcewrite,begin=STAGE,end=STAGE+256+len(blob)-1)
 def store(uc,access,address,n,value,d):
  pc=uc.reg_read(UC_M68K_REG_PC)
  assert STAGE<=pc<STAGE+len(copier),(hex(pc),hex(address))
  assert not m.ctlregs[2]&0xa0000000,'cache or store buffer enabled during copy'
  out['copy_stores']+=1
 uc.hook_add(UC_HOOK_MEM_WRITE,store,begin=RAM,end=RAM+len(blob)-1)
def trace(m,done,pc):print('loader',done,hex(pc),flush=True)
try:
 r=bootrom.boot(syx,bootstrap,main,limit=300000000,chunk=10000000,on_machine=install,trace=trace,ui_card=8,straps={0xec09401b:8},groups=7)
 out['loader']={'stop':r.stop,'reached':hex(r.reached) if r.reached else None,'main_matches':r.main_os_matches,'controls':state(r.m),'flags':hex(r.boot_flags) if r.boot_flags is not None else None,'flash_writes':r.flash_writes}
 assert r.reached==0x400004e8 and r.main_os_matches and not r.flash_writes
 r.m.halt_vec=None
 pc,done,stop=longrun.spin(r.m,r.reached,100000000,chunk=10000000,on_chunk=lambda *args:print('copier progress',flush=True))
 out['continuation']={'pc':hex(pc),'stop':stop,'controls':state(r.m),'source_intact':bytes(r.m.uc.mem_read(STAGE+256,len(blob)))==blob,'copied_exact':bytes(r.m.uc.mem_read(RAM,len(blob)))==blob}
 assert pc==0x40000568 and out['copy_stores']==len(blob)//4 and out['continuation']['copied_exact']
 out['passed']=True
except BaseException as e:
 out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
out['after']=hashlib.sha256(syx.read_bytes()).hexdigest();assert out['before']==out['after']
out['seconds']=time.monotonic()-start
pathlib.Path('outputs/Digitone-continuous-loader-copier.json').write_text(json.dumps(out,indent=2));print('RESULT',out['passed'],out['seconds'],flush=True)
