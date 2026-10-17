"""Actual metadata helper instructions, synthetic addresses only; image unchanged."""
exec(open('work/execute-identity-and-accepted-commit.py').read().split('for initial,want')[0])
class Asm:
 def __init__(self):self.code=bytearray();self.labels={};self.fix=[]
 def emit(self,h):self.code.extend(bytes.fromhex(h))
 def label(self,n):self.labels[n]=len(self.code)
 def branch(self,op,n):p=len(self.code);self.emit(op+'0000');self.fix.append((p,n))
 def done(self):
  for p,n in self.fix:self.code[p+2:p+4]=(self.labels[n]-p-2).to_bytes(2,'big',signed=True)
  return bytes(self.code)
def pro(a):a.emit('206f000440c146fc2700') # record, save SR, mask interrupts
def end(a):a.emit('46c14e75')
fixtures={};names={}
def install(name,a):addr=0x50001000+len(fixtures)*0x200;fixtures[addr]=a.done();names[name]=addr
# begin(record): non-wrapping depth; overflow stays unavailable.
a=Asm();pro(a);a.emit('202800080c80ffffffff');a.branch('6700','overflow');a.emit('5280214000087001');a.branch('6000','end');a.label('overflow');a.emit('42a8000c4280');a.label('end');end(a);install('begin',a)
# cancel(record): close one gate without replacing accepted data; underflow fails closed.
a=Asm();pro(a);a.emit('20280008');a.branch('6700','bad');a.emit('5380214000087001');a.branch('6000','end');a.label('bad');a.emit('42a8000c4280');a.label('end');end(a);install('cancel',a)
# commit(record,id,snapshot,binding). Only the outermost gate may commit.
a=Asm();pro(a);a.emit('202800080c8000000001');a.branch('6600','busy');a.emit('202f0008');a.branch('6700','bad');a.emit('202f00100c8000000004');a.branch('6400','bad');a.emit('202f000c');a.branch('6700','store');a.branch('6a00','bad');a.emit('02807fff8000');a.branch('6600','bad');a.emit('202f000cee8802800000003f0c8000000024');a.branch('6400','bad');a.label('store');a.emit('202f00082080202f000c2140000442a8000c42a80008');a.emit('202f000c');a.branch('6700','success');a.emit('202f00100080800000002140000c');a.label('success');a.emit('7001');a.branch('6000','end');a.label('bad');a.emit('42a80008');a.label('busy');a.emit('42a8000c4280');a.label('end');end(a);install('commit',a)
# read(record,expected id,binding): return only complete bound record.
a=Asm();pro(a);a.emit('20280008');a.branch('6600','none');a.emit('202f0008');a.branch('6700','none');a.emit('b090');a.branch('6600','none');a.emit('202f000c0c8000000004');a.branch('6400','none');a.emit('008080000000b0a8000c');a.branch('6600','none');a.emit('20280004');a.branch('6000','end');a.label('none');a.emit('4280');a.label('end');end(a);install('read',a)
# candidate-copy(dst,src), invalidate(dst): callers supply validated aligned entries.
a=Asm();pro(a);a.emit('226f000820112080');end(a);install('copy',a)
a=Asm();pro(a);a.emit('42904280');end(a);install('invalidate',a)
for addr,code in fixtures.items():
 items=list(md.disasm(code,addr));assert sum(i.size for i in items)==len(code) and all(i.id for i in items),(hex(addr),[(i.mnemonic,i.op_str) for i in items])
def fixture_fetch(pc):
 for addr,code in fixtures.items():
  if addr<=pc<addr+len(code):return code[pc-addr:pc-addr+16]
 return b[pc-base:pc-base+16]
RANGES.extend((addr,addr+len(code)) for addr,code in fixtures.items())
src=source.replace('b[pc-base:pc-base+16]','fixture_fetch(pc)');exec('if True:\n'+src);Machine.run=run
checks=[];total=0;record=0x27000010
m=create();m.map(record-16,96)
for k in range(96):m.write(record-16+k,1,0xa5)
for t in range(4):
 for off in range(0,16,4):m.write(record+t*16+off,4,0)
def call(name,*args):
 global total
 m.sr=0x251b;before=m.reg.copy();start=len(m.steps);ret=m.run(names[name],args);total+=len(m.steps)-start
 assert m.sr==0x251b and m.reg['a7']==before['a7'] and all(m.reg[r]==before[r] for r in [f'd{i}' for i in range(2,8)]+[f'a{i}' for i in range(2,7)])
 return ret
for t in range(4):
 r=record+16*t
 for scale in range(36):
  for root in [0,60,127]:
   word=0x80000000|root|(scale<<7)|(t<<13)
   check('begin/commit/read encoding',call('begin',r)==1 and call('commit',r,19,word,t)==1 and call('read',r,19,t)==word)
   check('identity and binding reject',call('read',r,20,t)==0 and call('read',r,19,(t+1)%4)==0)
 check('gate hides prior record',call('begin',r)==1 and call('read',r,19,t)==0)
 check('nested commit fails closed',call('begin',r)==1 and call('commit',r,20,word,t)==0 and m.read(r+8,4)==2 and call('read',r,19,t)==0)
 check('nested cancels balance',call('cancel',r)==1 and call('cancel',r)==1 and m.read(r+8,4)==0)
 check('cancel underflow stays invalid',call('cancel',r)==0 and call('read',r,19,t)==0)
for badword in [1,0x80008000,0x80001200,0xffffffff]:
 call('begin',record);check('malformed snapshot fails closed',call('commit',record,21,badword,0)==0 and m.read(record+8,4)==0 and call('read',record,19,0)==0)
for ident,track in [(0,0),(21,4),(21,0xffffffff)]:
 call('begin',record);check('invalid identity/binding fails closed',call('commit',record,ident,0x80000080,track)==0 and call('read',record,19,0)==0)
call('begin',record);check('missing snapshot commits fallback',call('commit',record,22,0,0)==1 and m.read(record,4)==22 and call('read',record,22,0)==0)
m.write(record+8,4,0xffffffff);check('depth overflow does not wrap',call('begin',record)==0 and m.read(record+8,4)==0xffffffff)
# Inspect every store boundary, including validity publication: no exposed partial tuple.
m.write(record+8,4,0);call('begin',record);m.write(record+12,4,0x80000000)
visible=[]
def observe(pc):
 if names['commit']<=pc<names['commit']+len(fixtures[names['commit']]):
  if m.read(record+8,4)==0 and m.read(record+12,4)==0x80000000:visible.append((m.read(record,4),m.read(record+4,4)))
m.observe=observe;call('commit',record,42,0x80000080,0);del m.observe
check('only complete tuple is published',visible and all(v==(42,0x80000080) for v in visible))
srcptr=record+64;dstptr=record+68;m.write(srcptr,4,0x80006080)
check('candidate copy and self-copy',call('copy',dstptr,srcptr)==0x80006080 and call('copy',dstptr,dstptr)==0x80006080 and m.read(dstptr,4)==0x80006080)
check('candidate invalidation',call('invalidate',dstptr)==0 and m.read(dstptr,4)==0)
check('record guards preserved',all(m.mem[record-16+k]==0xa5 for k in range(16)) and all(m.mem[record+72+k]==0xa5 for k in range(8)))
# Ordinary additive/zero-return path preserves the prior accepted snapshot.
m.write(record+8,4,0);call('begin',record);call('commit',record,43,0x80000080,0)
check('balanced zero-result cancellation preserves prior context',call('begin',record)==1 and call('cancel',record)==1 and call('read',record,43,0)==0x80000080)
for prior_sr in [0x2000,0x240f,0x2715]:
 m.sr=prior_sr;m.run(names['begin'],(record,));m.run(names['cancel'],(record,))
 check('exact SR restoration across masks',m.sr==prior_sr)
check('source candidate unchanged',m.read(srcptr,4)==0x80006080)
total=len(m.steps)
result={'passed':len(checks),'executed_instructions':total,'checks':checks,'helpers':{name:{'address':hex(addr),'bytes':len(fixtures[addr]),'disassembly':[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(fixtures[addr],addr)]} for name,addr in names.items()},'firmware_modified':False,'limits':['Synthetic executable addresses only','Explicit validated record/entry pointers supplied; owner resolver and pool-address classifier not implemented','Supervisor context required; masks interrupts but does not stop DMA or multiple CPUs','Reader validates record publication, identity and binding; callers still require header readiness, active arp and retained identity checks','Bounded custom interpreter, not independent hardware validation','No startup wrapper, code installation, allocator or cache maintenance executed']}
pathlib.Path('outputs/Digitone-metadata-helper-instruction-tests.json').write_text(json.dumps(result,indent=2));print('PASS',len(checks),'checks;',total,'helper instructions')

