from pathlib import Path
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from emu.harness import Machine,call
cfg=json.loads(Path('work/os144/PC_ONLY-live-capture-layout.json').read_text());code=Path('work/os144/PC_ONLY-live-capture-code.bin').read_bytes();old=Path('work/os144/PC_ONLY-E04-ISA-corrected-payload.bin').read_bytes()
checks=[];cases=[]
m=Machine();m.load(Path('work/os144/section-3.bin').read_bytes(),0x40000400);m.load(old,0x47be0000);m.load(code,cfg['base']);m.install_isa_patches_scoped(old[:1784],0x47be0000);m.install_isa_patches_scoped(code,cfg['base']);uc=m.uc
for a in [0x47be0000,0x43220000,0x419ebe2c,0x407fd414,0x47fe0000]:m.ensure(a)
uc.mem_write(0x47be1000,struct.pack('>IIIII',0x47be1004-0x14100,0x534c4332,2,0xb70,1));uc.mem_write(cfg['state'],bytes(cfg['state_bytes']))
for item in cfg['layout'].values():
 p=item['address'];end=p+item['size']
 while p<end:
  i=cfisa.decode(lambda off:int.from_bytes(uc.mem_read(p+off,2),'big'),p)
  assert not i.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(uc.mem_read(p,2),'big')),(hex(p),i.op)
  p+=i.length
 assert p==end
checks.append('All added instructions pass ColdFire decoder and combined MOVE restrictions')
for t in range(4):
 for n in range(128):
  uc.reg_write(UC_M68K_REG_D0,0x43220348+t*0x2a18+n*72)
  assert call(m,cfg['layout']['descriptor_slot']['address'],[],stack_top=0x47feff00,limit=1000)==(t*128+n)*4
checks.append('All 512 descriptor addresses map to distinct bounded sidecar slots')
for e in [0,0xffffffff,0x43220347,0x43220349,0x43220348+0x2400,0x43220348+4*0x2a18]:
 uc.reg_write(UC_M68K_REG_D0,e);assert call(m,cfg['layout']['descriptor_slot']['address'],[],stack_top=0x47feff00,limit=1000)==0xffffffff
checks.append('Invalid, unaligned, inter-track gap and fifth-track sources rejected')
# Enter the actual displaced-instruction hook with a stock input-handler frame.
REGS=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(7)]
for t,n,root,raw,ready in [(0,64,62,0,1),(3,127,65,5,1),(0,64,60,-1,1),(0,64,128,0,1),(0,64,62,35,1),(4,64,62,0,1),(0,128,62,0,1),(0,64,62,0,0)]:
 uc.mem_write(cfg['state'],bytes(cfg['state_bytes']));uc.mem_write(0x47be1010,struct.pack('>I',ready))
 pattern=0x407fd414;uc.mem_write(pattern+t*0x3d0+0x3cb,bytes([root]));uc.mem_write(pattern+t*0x3d0+0x3ce,bytes([raw&255]))
 for j,r in enumerate(REGS):uc.reg_write(r,0x12340000+j)
 uc.reg_write(UC_M68K_REG_A2,pattern);uc.reg_write(UC_M68K_REG_A6,0x47fe8000);uc.reg_write(UC_M68K_REG_D2,t);uc.reg_write(UC_M68K_REG_D3,n);uc.reg_write(UC_M68K_REG_SR,0x231f);uc.reg_write(UC_M68K_REG_A7,0x47feff00)
 before=[uc.reg_read(r) for r in REGS];uc.emu_start(cfg['layout']['noteon_capture']['address'],0x400eaf50,count=3000)
 assert uc.reg_read(UC_M68K_REG_PC)==0x400eaf50 and before==[uc.reg_read(r) for r in REGS] and uc.reg_read(UC_M68K_REG_A7)==0x47feff00
 assert bytes(uc.mem_read(0x47fe8000-0x30,8))==struct.pack('>II',t,n)
 expected=0x80000000|root|((raw+1)<<7)|(t<<13) if t<4 and n<128 and root<128 and -1<=raw<35 and ready else 0
 actual=int.from_bytes(uc.mem_read(cfg['pending']+t*8+4,4),'big') if t<4 and n<128 else 0
 assert actual==expected,(t,n,hex(actual),hex(expected))
 # Stock second displaced MOVE sets NZ, clears VC and preserves X.
 assert uc.reg_read(UC_M68K_REG_SR)==(0x2310|(4 if n==0 else 0))
 cases.append({'track':t,'note':n,'root':root,'raw':raw,'ready':ready,'word':hex(actual),'registers_stack_SR_preserved_before_displaced_moves':True})
checks.append('Capture validates track, note, root, scale and readiness; displaced writes and full register/stack/condition contract match stock')
uc.mem_write(0x47be1010,struct.pack('>I',1))
for state,key_matches,ready in [(1,True,1),(1,False,1),(2,True,1),(1,True,0)]:
 t=3;n=127;src=0x43220348+t*0x2a18+n*72;inp=0x47fe8000;slot=cfg['state']+(t*128+n)*4;pending=cfg['pending']+t*8
 m.ensure(src);uc.mem_write(inp,struct.pack('>IIII',t,n,100,state));uc.mem_write(slot,struct.pack('>I',0x800060be));uc.mem_write(pending,struct.pack('>II',inp if key_matches else inp+4,0x800060c1));uc.mem_write(0x47be1010,struct.pack('>I',ready))
 for j,r in enumerate(REGS):uc.reg_write(r,0x12340000+j)
 uc.reg_write(UC_M68K_REG_A2,inp);uc.reg_write(UC_M68K_REG_A4,src);uc.reg_write(UC_M68K_REG_D0,5);uc.reg_write(UC_M68K_REG_SR,0x231f);uc.reg_write(UC_M68K_REG_A7,0x47feff00);before=[uc.reg_read(r) for r in REGS]
 uc.emu_start(cfg['layout']['descriptor_bind']['address'],0x400ff484,count=3000)
 actual=int.from_bytes(uc.mem_read(slot,4),'big');expected=(0x800060c1 if key_matches else 0) if ready and state==1 else 0x800060be
 assert actual==expected and before==[uc.reg_read(r) for r in REGS] and uc.reg_read(UC_M68K_REG_A7)==0x47feff00 and uc.reg_read(UC_M68K_REG_SR)==0x2314,(hex(actual),hex(expected))
 assert bytes(uc.mem_read(src+0x34,4))==struct.pack('>I',5) and bytes(uc.mem_read(src+0x44,4))==bytes(4)
 if ready and state==1 and key_matches:assert bytes(uc.mem_read(pending,8))==bytes(8)
checks.append('Descriptor binding consumes matching input once, rejects mismatched pending input, preserves note-off context and refuses unready state')
uc.mem_write(0x47be1010,struct.pack('>I',1))
for t,n in [(0,0),(0,64),(3,127)]:
 src=0x43220348+t*0x2a18+n*72;dest=0x419ebe2c;word=0x800000be|(t<<13)
 m.ensure(src);uc.mem_write(src,bytes(range(72)));uc.mem_write(cfg['state']+(t*128+n)*4,struct.pack('>I',word))
 call(m,cfg['layout']['live_copy']['address'],[dest,src,72],stack_top=0x47feff00,limit=3000)
 assert bytes(uc.mem_read(dest,72))==bytes(range(72)) and int.from_bytes(uc.mem_read(0x47be1024,4),'big')==word
checks.append('Actual stock 72-byte memcpy transfers descriptors and machine-code wrapper transfers original captured context')
for mode in ['known','unknown_source','unready','short','unknown_destination']:
 src=0x43220348+64*72 if mode!='unknown_source' else 0x43227000;dest=0x419ebe2c if mode!='unknown_destination' else 0x419ef000;length=68 if mode=='short' else 72
 m.ensure(src);m.ensure(dest);uc.mem_write(src,bytes(range(72)));uc.mem_write(cfg['state']+64*4,struct.pack('>I',0x800000be));uc.mem_write(0x47be1010,struct.pack('>I',0 if mode=='unready' else 1))
 states=[]
 for address in [0x400fbad8,cfg['layout']['live_copy']['address']]:
  uc.mem_write(dest,bytes([0xa5])*72);uc.mem_write(0x47be1024,struct.pack('>I',0x12345678))
  for j,reg in enumerate(REGS):uc.reg_write(reg,0x22340000+j)
  call(m,address,[dest,src,length],stack_top=0x47feff00,limit=3000)
  states.append({'registers':[uc.reg_read(reg) for reg in REGS],'sr':uc.reg_read(UC_M68K_REG_SR),'sp':uc.reg_read(UC_M68K_REG_A7),'bytes':bytes(uc.mem_read(dest,72)).hex(),'metadata':int.from_bytes(uc.mem_read(0x47be1024,4),'big')})
 assert {k:v for k,v in states[0].items() if k!='metadata'}=={k:v for k,v in states[1].items() if k!='metadata'},mode
 expected={'known':0x800000be,'unknown_source':0,'unready':0x12345678,'short':0x12345678,'unknown_destination':0x12345678}[mode]
 assert states[1]['metadata']==expected,(mode,states)
checks.append('Full memcpy result registers, stack, SR and copied bytes equal stock across valid, unknown-source, unready, short-copy and unknown-destination controls')
Path('outputs/Digitone-E04-PC-live-capture-contracts.json').write_text(json.dumps({'PC_only':True,'checks':checks,'cases':cases,'passed':True},indent=2));print('PASS',len(checks),'contract groups',len(cases),'capture cases')
