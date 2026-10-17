exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for start,end in [(0x400388e4,0x400389b4),(0x400dc8c4,0x400dc9b0),(0x400dc2f6,0x400dc3e2)]:
 out.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
out.append('EVENT-DISPATCH CANDIDATE STORES: discovery only')
for i in md.disasm(b[0x4009cb98-base:0x4009e39e-base],0x4009cb98):
 if i.mnemonic.startswith(('move','clr','add','sub','or','and')) and (i.op_str.endswith(', (a3)') or i.op_str=='(a3)' or '$38(a3)' in i.op_str):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
out.append('SETTINGS DISPLACEMENT CANDIDATES: discovery only')
for i in md.disasm(b[:0x170000],base):
 if any(s in i.op_str for s in ['$12a(', '$12e(']):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/cached-replay-eligibility.txt').write_text('\n'.join(out))
for v in [0x401feafc,0x401feaf8,0x401feb00,0x4002f08a,0x4002f13a]:
 hits=[];p=0
 while True:
  p=b.find(struct.pack('>I',v),p)
  if p<0:break
  hits.append(base+p);p+=1
 out.append(f'EXACT {v:08x}: {[hex(a) for a in hits]}')
 for a in hits:
  if v==0x401feafc:
   out.append(f'CONTEXT literal {a:08x}')
   for i in md.disasm(b[a-base-2:a-base+18],a-2):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
out.append(f'GLOBAL STEP INITIAL BYTES {b[0x401feaf8-base:0x401feb04-base].hex()}')
for target in [0x400dcaf6,0x400dcb0e,0x400ab0ac,0x400aa892]:
 refs=[]
 for off in range(0,len(b)-6,2):
  op=struct.unpack_from('>H',b,off)[0]
  if op in (0x4eb9,0x4ef9) and struct.unpack_from('>I',b,off+2)[0]==target:refs.append(base+off)
  if op>>8 in (0x60,0x61):
   disp=op&255
   if disp==0:disp=struct.unpack_from('>h',b,off+2)[0]
   elif disp==255:disp=struct.unpack_from('>i',b,off+2)[0]
   elif disp>=128:disp-=256
   if base+off+2+disp==target:refs.append(base+off)
 out.append(f'DIRECT {target:08x}: {[hex(a) for a in refs]}')
pathlib.Path('work/cached-replay-eligibility.txt').write_text('\n'.join(out))
print('\n'.join(out[:130]+out[-7:]))
