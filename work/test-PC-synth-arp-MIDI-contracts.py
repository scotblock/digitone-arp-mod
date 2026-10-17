from pathlib import Path
exec(Path('work/test-E06-degree-contracts.py').read_text().split('count=0;examples=[]')[0])
mid=json.loads(Path('work/os144/PC_ONLY-synth-arp-MIDI-layout.json').read_text());blob=Path('work/os144/PC_ONLY-synth-arp-MIDI-code.bin').read_bytes();tail=Path('work/os144/PC_ONLY-synth-arp-MIDI-tail.bin').read_bytes();S=mid['state'];R=mid['records'];M=mid['markers'];B=mid['base'];checks=[];packets=[]
for address in [B,S,0x405285a4,0x419c5df4,0x41368d30,0xfc045000,0x4bc09000]:m.ensure(address)
u.mem_write(B,blob)
for r in mid['regions']+[mid['tail']]:
 code=tail if r['base']==0x47be0c00 else blob[r['base']-B:r['base']-B+r['bytes']];p=0
 while p<len(code):
  i=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),r['base']+p);assert i.length>0 and p+i.length<=len(code) and not i.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big')),(r,hex(r['base']+p),i);p+=i.length
 m.install_isa_patches_scoped(code,r['base'])
def stub(uc,pc,n,d):
 sp=uc.reg_read(UC_M68K_REG_A7);assert int.from_bytes(uc.mem_read(sp+4,4),'big')==3;ptr=int.from_bytes(uc.mem_read(sp+8,4),'big');packets.append(list(uc.mem_read(ptr,3)));uc.reg_write(UC_M68K_REG_PC,int.from_bytes(uc.mem_read(sp,4),'big'));uc.reg_write(UC_M68K_REG_A7,sp+4)
u.hook_add(UC_HOOK_CODE,stub,begin=0x40002a3a,end=0x40002a3a)
def put(a,v):u.mem_write(a,u32(v))
def get(a):return int.from_bytes(u.mem_read(a,4),'big')
def reset():
 packets.clear();u.mem_write(S,bytes(160));put(S,0x53414d31);put(S+4,1);put(0x419c5df4,1);put(0x405285a4,0x4bc09000)
 for a in [0x405285b0,0x405285bc,0x405285b8]:put(a,0)
 u.mem_write(0xfc0454b4,bytes(2));u.mem_write(0xfc0454bc,bytes(2))
 for t in range(4):put(M+t*4,0x419e0000+t*72);put(0x41368d30+t*4,t)
def invoke(addr,args=[]):return call(m,addr,args,stack_top=STACK,limit=20000)
ON=B+0x300;OFF=B+0x200;PUMP=B+0x500
for t in range(4):
 reset();invoke(ON,[t,t,0x419e0000+t*72,60+t,100]);invoke(OFF,[t]);assert packets==[[0x90+t,60+t,100],[0x80+t,60+t,0]];assert get(R+t*16)==0;checks.append('configured channel '+str(t+1))
reset()
for v in range(3):invoke(ON,[v,0,0x419e0000,60,90])
assert packets==[[0x90,60,90]]
invoke(OFF,[0]);invoke(OFF,[1]);assert len(packets)==1;invoke(OFF,[2]);assert packets[-1]==[0x80,60,0] and len(packets)==2;checks.append('shared/unison ownership sends one pair')
reset();invoke(ON,[0,0,0x419e0000,60,100]);invoke(ON,[0,0,0x419e0004,62,100]);assert packets==[[0x90,60,100],[0x80,60,0]];checks.append('ordinary replacement releases mirrored owner without mirroring ordinary note')
reset();invoke(ON,[0,0,0x419e0000,60,100]);put(0x41368d30,9);invoke(OFF,[0]);invoke(ON,[0,0,0x419e0000,62,100]);invoke(OFF,[0]);assert packets==[[144,60,100],[128,60,0],[153,62,100],[137,62,0]];checks.append('channel change releases original stored destination')
for field,value in [(S+4,0),(0x419c5df4,0),(0x41368d30,0xffffffff),(S,0)]:
 reset();put(field,value);before=bytes(u.mem_read(R,128));invoke(ON,[0,0,0x419e0000,60,100]);assert not packets and before==bytes(u.mem_read(R,128));checks.append('disabled/invalid gate '+hex(field))
reset();put(0x405285b8,4094);invoke(ON,[0,0,0x419e0000,60,100]);assert not packets and get(R)==0 and get(S+8)==1;checks.append('full ring drops note-on without claiming ownership')
reset();invoke(ON,[0,0,0x419e0000,60,100]);put(0x405285b8,4094);invoke(OFF,[0]);assert len(packets)==1 and get(R)==1 and get(R+8)==1;put(0x405285b8,0);invoke(PUMP);assert packets[-1]==[128,60,0] and get(R)==0;checks.append('blocked note-off retained and drained later')
reset();invoke(ON,[0,0,0x419e0000,60,100]);put(0x419c5df4,0);invoke(OFF,[0]);assert packets[-1]==[128,60,0];checks.append('output selection change does not strand existing note')
for v in [-1,8,127]:
 reset();invoke(ON,[v,0,0x419e0000,60,100]);invoke(OFF,[v]);assert not packets;checks.append('invalid voice '+str(v))
assert hashlib.sha256(Path('outputs/Digitone_OS1.44E06_SCALE_DEGREE_ARP_PC_ONLY.syx').read_bytes()).hexdigest()=='9677c2434429016b1861ebcbb5cfbefcaa0a863c076e123acd84abf120a068d3'
out={'passed':True,'PC_only':True,'checks':checks,'strict_ColdFire_regions_passed':True,'E06_preserved':True,'limits':['Stock DIN writer is replaced by a packet-recording stub in these isolated ownership controls. Integrated playback must use the real writer.','Private code/state are host installed; native startup integration remains unimplemented.']};Path('outputs/Digitone-synth-arp-MIDI-contracts.json').write_text(json.dumps(out,indent=2));print('PASS',len(checks),'MIDI ownership/control groups')
