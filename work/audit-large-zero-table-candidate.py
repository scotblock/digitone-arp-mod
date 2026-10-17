"""Execute unchanged stock table-reader slices, never modify firmware."""
exec(open('work/test-actual-capture-and-pitch.py').read().split('# Capture across')[0])
import hashlib
RANGES.extend([(0x400984fc,0x4009852c),(0x40098a5c,0x40098aba),(0x40098fe0,0x40099022),(0x4009882c,0x40098850),(0x40098d44,0x40098d5c)])
lo,hi,tbase=0x401fd47c,0x401fdc8c,0x401fcc8c
assert b[lo-base:hi-base]==bytes(2064)
cases=[];coverage={}
for reader in ('dual_filter_8e_90','filter_8_0a','filter_8_0a_second'):
 reached=set()
 for idx in range(508,1024):
  total=idx*64;x=min(32767,total);y=total-x
  assert 0<=x<=32767 and 0<=y<=32767
  m=create();param=0x29000000;m.map(param,0x200);m.map(0x8000e990,0x100);m.map(0x8000d500,0x300)
  reads=[];original_read=m.read
  def observed_read(addr,size):
   if size==4 and tbase<=addr<hi:reads.append(addr)
   return original_read(addr,size)
  m.read=observed_read
  if reader=='dual_filter_8e_90':
   m.reg['a0']=param;m.write(param+0x8e,2,x);m.write(param+0x90,2,y);m.write(m.reg['a7']+0x30,4,param)
   m.route(0x400984fc,0x4009852c)
   first=m.read(m.reg['a7']+0x48,4);second=m.read(m.reg['a7']+0x4c,4)
  elif reader=='filter_8_0a':
   m.reg['a6']=param;m.write(param+8,2,x);m.write(param+10,2,y)
   m.route(0x40098a5c,0x40098aba)
   first=m.read(0x8000e9b0,4);second=m.read(0x8000e9b4,4)
  else:
   m.reg['a0']=param;m.write(param+8,2,x);m.write(param+10,2,y);m.write(param+4,1,0);m.write(param+6,2,0)
   m.route(0x40098fe0,0x40099022)
   first=m.read(0x8000d5d0,4);second=m.read(0x8000d5d4,4)
  want=[tbase+4*(x>>6),tbase+4*idx]
  assert reads==want,(reader,idx,reads,want)
  assert first==int.from_bytes(b[want[0]-base:want[0]-base+4],'big') and second==0
  reached.update(addr for addr in reads if lo<=addr<hi)
  cases.append({'reader':reader,'index':idx,'parameter_1':x,'parameter_2':y,'summed_read':hex(want[1])})
 assert reached==set(range(lo,hi,4))
 coverage[reader]={'distinct_candidate_words':len(reached),'bytes':len(reached)*4}
# Execute both existing endpoint initialization slices as well.
for start,end,dest in [(0x4009882c,0x40098850,0x8000e9b4),(0x40098d44,0x40098d5c,0x8000d5d4)]:
 m=create();m.map(0x8000e990,0x100);m.map(0x8000d500,0x300);m.route(start,end);assert m.read(dest,4)==0
image_hash=hashlib.sha256(b).hexdigest();assert image_hash=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
stock=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
assert hashlib.sha256(stock.read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
result={'candidate':{'start':hex(lo),'end_exclusive':hex(hi),'bytes':2064},'table_base':hex(tbase),'candidate_indices':[508,1023],'executed_index_cases':len(cases),'executed_endpoint_initializers':2,'coverage_by_reader':coverage,'usable_bytes_certified':0,'limitations':'Parameter pairs are supplied nonnegative signed-word inputs. Full producer eligibility and complete function/DSP execution are not claimed. Excluding these table reads would require upstream constraints. All candidate words are reachable by each of three unchanged reader slices.','firmware_hashes_unchanged':True,'cases':cases}
pathlib.Path('outputs/Digitone-large-zero-table-candidate-audit.json').write_text(json.dumps(result,indent=2))
lines=[]
for start,end in [(0x400984fc,0x4009852c),(0x40098a5c,0x40098aba),(0x40098fe0,0x40099022),(0x4009882c,0x40098850),(0x40098d44,0x40098d5c)]:
 lines.append('\nWINDOW '+hex(start))
 for ins in md.disasm(b[start-base:end-base],start):lines.append(f'{ins.address:08x} {ins.bytes.hex():20} {ins.mnemonic:10} {ins.op_str}')
pathlib.Path('outputs/Digitone-large-zero-table-reader-instructions.txt').write_text('\n'.join(lines))
print('PASS:',len(cases),'stock reader cases; entire 2064-byte candidate reached by each of three readers; two endpoint initializers; firmware unchanged')
