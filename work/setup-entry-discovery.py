exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json
strings=[]
for m in re.finditer(rb'[\x20-\x7e]{5,}',b):
 s=m.group().decode()
 if re.search(r'alloc|memory|fatal|assert|panic|out of|failed|failure',s,re.I):strings.append((hex(base+m.start()),s[:200]))
print('STRINGS',json.dumps(strings))
targets=[0x400f0504,0x4009bcb8,0x4009bcc6,0x4009bde8,0x4009c7f0,0x4009c802,0x400ae45e]
refs={hex(t):[] for t in targets};alloc=[];interior=[]
for off in range(0,len(b)-6,2):
 a=base+off;op=struct.unpack_from('>H',b,off)[0];dst=None
 if op in (0x4eb9,0x4ef9):dst=struct.unpack_from('>I',b,off+2)[0]
 elif op in (0x4eba,0x4efa):dst=a+2+struct.unpack_from('>h',b,off+2)[0]
 elif op&0xf000==0x6000:
  v=op&255;d=struct.unpack_from('>i' if v==255 else '>h',b,off+2)[0] if v in (0,255) else (v-256 if v>=128 else v);dst=a+2+d
 if dst in targets:refs[hex(dst)].append(hex(a))
 if dst==0x400dab8c:alloc.append(a)
 if dst and 0x400f0504<dst<0x400f05d6 and not 0x400f0504<=a<0x400f05d6:interior.append((hex(a),hex(dst)))
print('REFS',json.dumps(refs));print('INTERIOR_CANDIDATES',json.dumps(interior));print('ALLOC_CALL_COUNT',len(alloc))
out=[]
for a in alloc:
 out.append('\nALLOC WINDOW '+hex(a))
 for i in md.disasm(b[a-base:a-base+36],a):out.append(f'{i.address:08x} {i.mnemonic} {i.op_str}')
pathlib.Path('work/setup-allocation-candidates.txt').write_text('\n'.join(out))
pathlib.Path('work/setup-entry-discovery.json').write_text(json.dumps({'strings':strings,'refs':refs,'interior_candidates':interior,'allocations':[hex(x) for x in alloc]},indent=2))
print('\n'.join(out[:55]))

