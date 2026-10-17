exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json
conds={'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs'}
def graph(start,end):
 todo=[start];seen={};calls=[]
 while todo:
  a=todo.pop()
  if a in seen:continue
  assert start<=a<end,hex(a)
  i=next(md.disasm(b[a-base:a-base+16],a,count=1));m=i.mnemonic.split('.')[0]
  assert i.id or i.bytes.hex() in [f'4a8{x:x}' for x in range(8,16)],(hex(a),i.mnemonic)
  seen[a]={'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str}
  if m in ('rts','rte'):continue
  if m=='jmp':raise RuntimeError((hex(a),i.op_str))
  if m in ('jsr','bsr'):calls.append({'site':hex(a),'instruction':i.mnemonic+' '+i.op_str})
  if m in conds|{'bra'}:
   todo.append(int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16))
   if m!='bra':todo.append(a+i.size)
  else:todo.append(a+i.size)
 return {'entry':hex(start),'instructions':{hex(a):v for a,v in sorted(seen.items())},'calls':calls}
graphs=[]
for start,end in [(0x400d924e,0x400d94de),(0x4008dce0,0x4008dfd2),(0x400d6db6,0x400d6e16),(0x400ae9fa,0x400aeb1a),(0x400d95cc,0x400d95ee),(0x4008dfd2,0x4008e032)]:graphs.append(graph(start,end))
refs=[]
for off in range(0,len(b)-6,2):
 if b[off+2:off+6]==struct.pack('>I',0x40253e80):refs.append(hex(base+off))
pathlib.Path('outputs/Digitone-shutdown-barrier-graphs.json').write_text(json.dumps({'graphs':graphs,'test_mode_flag_literal_candidates':refs,'scope':'Confirmed local graphs; calls do not certify transitive effects.'},indent=2))
print(json.dumps({'graphs':[(g['entry'],len(g['instructions']),g['calls']) for g in graphs],'test_mode_flag_candidates':refs},indent=2))
