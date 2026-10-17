from pathlib import Path
import json,re,sys,collections
sys.path.insert(0,'work/emulator-deps')
from capstone import *
image=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;end=base+len(image);md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
roots=[0x400004e8,0x4008d300,0x4009d120,0x400025c8,0x40002342,0x400e9b7e,0x400e842c,0x400e9076,0x400eabb4,0x400eae5c,0x400edbc2,0x400e6352,0x400e47e6,0x400f049a,0x400f0580,0x400947ec]
old=json.loads(Path('outputs/Digitone-OS1.44-fallback-and-RAM-completion-checks.json').read_text())
for t in old['runtime_tasks']:
 if 'entry' in t:roots.append(int(t['entry'],16))
queue=collections.deque(roots);seen=set();unknown=[];indirect=[];computed_stores=[];hits=[]
while queue and len(seen)<200000:
 pc=queue.popleft()
 if pc in seen or pc<base or pc>=end or pc&1:continue
 seen.add(pc);raw=image[pc-base:pc-base+16];items=list(md.disasm(raw,pc,count=1))
 if not items:
  # ColdFire TST An is unsupported by this 68040 decoder, length is known.
  if len(raw)>=2 and 0x4a88<=int.from_bytes(raw[:2],'big')<=0x4a8f:queue.append(pc+2);continue
  unknown.append(hex(pc));continue
 i=items[0];op=i.mnemonic.split('.')[0];operands=i.op_str
 for v in re.findall(r'\$([0-9a-f]+)',operands):
  address=int(v,16)
  if 0x40000000<=address<0x80000000 and 0x47be2860<=0x40000000+(address-0x40000000)%0x08000000<0x47be29f0:hits.append({'pc':hex(pc),'instruction':i.mnemonic+' '+operands})
 dest=operands.rsplit(', ',1)[-1]
 if op in ['move','movem','clr','add','sub','and','or','eor','bset','bclr','bchg','addq','subq'] and '(' in dest:computed_stores.append({'pc':hex(pc),'instruction':i.mnemonic+' '+operands})
 if op in ['rts','rte','rtr','stop','illegal']:continue
 control=op in ['jsr','jmp','bsr','bra'] or (op.startswith('b') and op not in ['btst','bset','bclr','bchg','bitrev','byterev'])
 if control:
  match=re.fullmatch(r'\$([0-9a-f]+)(?:\(pc\)|\.l|\.w)?',operands)
  if match:queue.append(int(match[1],16))
  elif op in ['jsr','jmp']:indirect.append({'pc':hex(pc),'instruction':i.mnemonic+' '+operands})
  if op in ['bra','jmp']:continue
 queue.append(pc+i.size)
r={'PC_only':True,'stock_OS':'1.44','root_count':len(set(roots)),'reached_instruction_count':len(seen),'truncated_at_budget':bool(queue),'literal_interval_hits':hits,'unknown_boundaries':unknown,'indirect_control_edges':indirect,'computed_destination_candidates':computed_stores,'limits':['Rooted 68040 disassembly screen with one recognized ColdFire fallback; undecoded instructions and indirect edges terminate coverage.','Computed store candidates are not data-flow-resolved destinations; absence of literal hits is not exclusive ownership proof.']}
Path('outputs/Digitone-E04-PC-resident-computed-write-screen.json').write_text(json.dumps(r,indent=2));print('Rooted screen:',len(seen),'instructions;',len(computed_stores),'computed-store candidates;',len(indirect),'indirect edges;',len(unknown),'unknown boundaries')
