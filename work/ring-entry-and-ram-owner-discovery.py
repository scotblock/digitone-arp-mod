exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json
target=0x400f021c
raw=[];transfers=[];pc=[]
for section in [2,3]:
 data=pathlib.Path(f'work/section-{section}.bin').read_bytes()
 raw.append(dict(section=section,exact_function_pointer_offsets=[m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),data)],exact_index_pointer_offsets=[m.start() for m in re.finditer(re.escape(struct.pack('>I',0x4199d4f4)),data)]))
# Inspect direct branch, call and jump encodings, including 32-bit relative
# branches omitted by the earlier word/byte candidate search.
for off in range(0,len(b)-8,2):
 a=base+off;op=int.from_bytes(b[off:off+2],'big');dest=None;form=None
 if op in (0x4eb9,0x4ef9):dest=int.from_bytes(b[off+2:off+6],'big');form='absolute'
 elif op in (0x4eba,0x4efa):dest=a+2+int.from_bytes(b[off+2:off+4],'big',signed=True);form='pc_word'
 elif op&0xf000==0x6000:
  low=op&255
  if low==0:disp=int.from_bytes(b[off+2:off+4],'big',signed=True);form='branch_word'
  elif low==255:disp=int.from_bytes(b[off+2:off+6],'big',signed=True);form='branch_long'
  else:disp=int.from_bytes(b[off+1:off+2],'big',signed=True);form='branch_byte'
  dest=a+2+disp
 if dest is not None and 0x400f021c<=dest<0x400f0296:
  transfers.append(dict(site=f'{a:08x}',target=f'{dest:08x}',form=form,entry=dest==target,source_inside_routine=0x400f021c<=a<0x400f0296))
 # Candidate PC-relative code/data operand at a confirmed two-byte opcode.
 # Full extension-word indexed forms remain a separate provenance gap.
 for start in [a]:
  i=next(md.disasm(b[off:off+16],start,count=1),None)
  if i and '(pc)' in i.op_str and ('$400f021c' in i.op_str or '$4199d4f4' in i.op_str):
   pc.append(dict(site=f'{start:08x}',instruction=f'{i.mnemonic} {i.op_str}'))
result=dict(raw=raw,encoded_transfers_into_routine=transfers,pc_relative_candidates=pc,limitation='Opcode discovery may include data; no complete proof against computed or relocated entry addresses')
pathlib.Path('work/ring-entry-discovery.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
out=[]
for s,e in [(0x400f05ba,0x400f0626),(0x400eea88,0x400eeb3e),(0x400eec70,0x400eed18),(0x400dab8c,0x400dac50),(0x400f066c,0x400f06dc)]:
 out.append('WINDOW '+hex(s));out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/ram-owner-followup-windows.txt').write_text('\n'.join(out))
