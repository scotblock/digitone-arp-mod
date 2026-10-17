"""Read-only execution of recovered stock indexed-reader slices."""
exec(open('work/test-actual-capture-and-pitch.py').read().split('# Capture across')[0])
import hashlib
RANGES.extend([(0x40098fe4,0x40098ffa),(0x40099022,0x40099038),(0x4009907a,0x4009909e)])
lo,hi=0x401fbf8c,0x401fc38c
assert b[lo-base:hi-base]==bytes(1024)
rows=[]
for reader in ('parameter_plus_4','parameter_plus_2'):
 for raw in range(256):
  m=create();m.map(0x29000000,32);m.reg['a0']=0x29000000
  m.write(0x29000000+(4 if reader=='parameter_plus_4' else 2),1,raw)
  m.write(0x29000006,2,0);m.reg['d0']=0;m.reg['d2']=0
  reads=[];original_read=m.read
  def observed_read(addr,size):
   if size==4 and 0x401fbf8c<=addr<0x401fc68c:reads.append(addr)
   return original_read(addr,size)
  m.read=observed_read
  signed=raw if raw<128 else raw-256
  if reader=='parameter_plus_4':
   m.route(0x40098fe4,0x40098ffa)
   want=0x401fc48c+4*signed;result=m.reg['d0']
  else:
   m.route(0x40099022,0x40099038)
   assert m.read(m.reg['a7']+0x30,4)==signed&0xffffffff
   m.route(0x4009907a,0x4009909e)
   want=0x401fc38c+4*signed if signed<=63 else None;result=m.reg['d5']
  assert reads==([] if want is None else [want]),(reader,raw,reads,want)
  if want is not None:
   assert result==int.from_bytes(b[want-base:want-base+4],'big')
  else:assert result==0x5b851eb8
  rows.append({'reader':reader,'raw':raw,'signed':signed,'address':None if want is None else hex(want),'candidate_overlap':want is not None and lo<=want<hi})
overlap=sorted({int(r['address'],16) for r in rows if r['candidate_overlap']})
assert overlap==list(range(0x401fc18c,hi,4))
source_path=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
assert hashlib.sha256(b).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
assert hashlib.sha256(source_path.read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
report={'candidate':{'start':hex(lo),'end_exclusive':hex(hi),'bytes':1024},'executed_cases':len(rows),'overlap':{'start':'0x401fc18c','end_exclusive':hex(hi),'bytes':512},'potential_remainder':{'start':hex(lo),'end_exclusive':'0x401fc18c','bytes':512,'ownership':'unverified','remaining_shortfall_if_all_512_available':302},'limitation':'Recovered reader slices execute unchanged instructions with supplied parameter bytes. Full upstream writers and normal-device negative-parameter eligibility are not established. This is a potential stock read overlap, not proof of a specific normal-device event. No code placement is certified.','firmware_hashes_unchanged':True,'cases':rows}
pathlib.Path('outputs/Digitone-zero-table-candidate-audit.json').write_text(json.dumps(report,indent=2))
windows=[(0x40098fd4,0x40099038),(0x4009907a,0x4009909e),(0x40096a30,0x40096a46)]
lines=[]
for start,end in windows:
 for ins in md.disasm(b[start-base:end-base],start):lines.append(f'{ins.address:08x} {ins.bytes.hex():20} {ins.mnemonic:10} {ins.op_str}')
pathlib.Path('outputs/Digitone-zero-table-reader-instructions.txt').write_text('\n'.join(lines))
print('PASS: 512 unchanged-stock reader cases; 512-byte candidate overlap; both firmware hashes unchanged')
