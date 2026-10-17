import sys,json,hashlib,struct,collections,difflib,re
from pathlib import Path
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections
from dt2.elz import depack_section
from emu.cfisa import decode,F_BCC,F_BRA,F_BSR
BASE=0x40000400
oldpath=Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
newpath=Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx')
old=Path('work/section-3.bin').read_bytes();new=Path('work/os144/section-3.bin').read_bytes()
report={'firmware_modified':False,'independent_decoder':[],'section_comparison':[],'candidates':[]}
containers={}
for version,path in [('1.42',oldpath),('1.44',newpath)]:
 c,entries=sections(path);containers[version]={sid:bytes(c[off:off+length]) for sid,off,length,dest in entries}
 for sid in ([2,3] if version=='1.42' else [2,3,8]):
  raw=depack_section(containers[version][sid])
  reference=Path(f'work/section-{sid}.bin' if version=='1.42' else f'work/os144/section-{sid}.bin').read_bytes()
  assert raw==reference,(version,sid)
  report['independent_decoder'].append({'version':version,'section':sid,'bytes':len(raw),'match':True})
for sid in sorted(set(containers['1.42'])|set(containers['1.44'])):
 a=containers['1.42'].get(sid);b=containers['1.44'].get(sid)
 report['section_comparison'].append({'id':sid,'old_bytes':None if a is None else len(a),'new_bytes':len(b),'identical':a==b})
targets={
 'early_startup':0x40000538,'producer_capture':0x40093ef4,
 'cache_copy_first':0x4009344e,'cache_copy_wrapper':0x40093892,
 'selector':0x4009719e,'later_pitch':0x4009755e,'acceptance_entry':0x4009dd80,
 'before_selector':0x4009dda6,'caller_commit':0x4009de46,'pitch_hook':0x4009df9a,
 'pool_initializer':0x400f0504,'allocate_clear':0x400f0626,
 'memcpy':0x400ec23c,'memset':0x400ec284,'allocator':0x400dab8c,
 'render_body':0x4009c838,'audio_irq_body':0x4009ba1c}
for name,address in targets.items():
 offset=address-BASE;votes=collections.Counter();anchors=collections.defaultdict(list)
 for relative in range(-64,128,2):
  p=offset+relative;token=old[p:p+8]
  if len(token)!=8:continue
  pos=new.find(token);hits=[]
  while pos>=0 and len(hits)<9:
   if pos%2==0:hits.append(pos)
   pos=new.find(token,pos+1)
  if len(hits)==1:
   delta=hits[0]-p;votes[delta]+=1;anchors[delta].append(relative)
 best=votes.most_common(3)
 record={'name':name,'old':hex(address),'status':'static_candidate_only','matches':[]}
 for delta,count in best:
  newaddr=address+delta;n=newaddr-BASE
  record['matches'].append({'new':hex(newaddr),'delta':delta,'unique_8byte_anchors':count,'anchor_offsets':anchors[delta],'old_at_site':old[offset:offset+16].hex(),'new_at_site':new[n:n+16].hex()})
 report['candidates'].append(record)
for record in report['candidates']:
 if not record['matches']:continue
 a=int(record['old'],16);b=int(record['matches'][0]['new'],16)
 changes=[];same=0;shape=True;ram=[];calls=[];consumed=0
 while consumed<128:
  def insn(data,addr):
   return decode(lambda relative:struct.unpack_from('>H',data,addr-BASE+relative)[0],addr)
  ia=insn(old,a+consumed);ib=insn(new,b+consumed)
  if (ia.length,ia.op,ia.flow)!=(ib.length,ib.op,ib.flow):
   shape=False;changes.append({'offset':consumed,'old_instruction':str(ia),'new_instruction':str(ib),'kind':'instruction_shape_changed'});break
  aa=old[a-BASE+consumed:a-BASE+consumed+ia.length];bb=new[b-BASE+consumed:b-BASE+consumed+ib.length]
  if aa==bb:same+=1
  else:
   changes.append({'offset':consumed,'old':aa.hex(),'new':bb.hex(),'op':ia.op})
   for k in range(2,ia.length-3,2):
    av=int.from_bytes(aa[k:k+4],'big');bv=int.from_bytes(bb[k:k+4],'big')
    if 0x40000000<=av<0x50000000 and 0x40000000<=bv<0x50000000:ram.append({'offset':consumed+k,'old':hex(av),'new':hex(bv)})
  if ia.flow and isinstance(ia.target,int):calls.append({'offset':consumed,'flow':ia.flow,'old':hex(ia.target),'new':hex(ib.target) if isinstance(ib.target,int) else str(ib.target)})
  consumed+=ia.length
 record['instruction_window']={'bytes_checked':consumed,'same_instruction_lengths_operations_control_classes':shape,'identical_instructions':same,'changes':changes,'address_pairs':ram,'static_transfers':calls}
core=json.loads(Path('work/upstream/elekloader/mods/core-dn1/mod.json').read_text())
report['elekloader_144_stock_sites']=[]
for site in core['ports']['1.44']['sites']:
 at=int(site['addr'],16)-BASE;expected=bytes.fromhex(site['stock']);actual=new[at:at+len(expected)]
 assert actual==expected,site
 report['elekloader_144_stock_sites'].append({'address':site['addr'],'target':site['target'],'stock_bytes_match':True})
report['startup_operands']={'old_prefix':old[:224].hex(),'new_prefix':new[:224].hex()}
def normalized_instructions(data,start,end):
 result=[];addr=start
 while addr<end:
  ins=decode(lambda relative:struct.unpack_from('>H',data,addr-BASE+relative)[0],addr)
  raw=data[addr-BASE:addr-BASE+ins.length];masked=bytearray(raw)
  if ins.flow in (F_BCC,F_BRA,F_BSR):
   masked[1:]=bytes(len(masked)-1)
  else:
   for k in range(2,len(raw)-3,2):
    value=int.from_bytes(raw[k:k+4],'big')
    if 0x40000000<=value<0x50000000:masked[k:k+4]=bytes(4)
  result.append({'address':hex(addr),'raw':raw.hex(),'op':ins.op,'key':(ins.op,ins.length,ins.flow,masked.hex())})
  addr+=ins.length
 assert addr==end,(hex(addr),hex(end))
 return result
oa=normalized_instructions(old,0x4009719e,0x4009755e)
nb=normalized_instructions(new,0x40097a94,0x40097e46)
sm=difflib.SequenceMatcher(None,[x['key'] for x in oa],[x['key'] for x in nb],autojunk=False)
report['selector_full_interval']={'old_start':'0x4009719e','old_end':'0x4009755e','new_start':'0x40097a94','new_end':'0x40097e46','old_instructions':len(oa),'new_instructions':len(nb),'method':'Sequence alignment; static transfer displacements and instruction-contained 0x40000000..0x4fffffff address candidates masked. Heuristic, not behavioral equivalence.','differences':[]}
for tag,i,j,k,l in sm.get_opcodes():
 if tag!='equal':report['selector_full_interval']['differences'].append({'tag':tag,'old':[{p:v for p,v in x.items() if p!='key'} for x in oa[i:j]],'new':[{p:v for p,v in x.items() if p!='key'} for x in nb[k:l]]})
section8=Path('work/os144/section-8.bin').read_bytes()
report['section8_observations']={'raw_bytes':len(section8),'ff_bytes':section8.count(255),'zero_bytes':section8.count(0),'first_non_ff':next(i for i,b in enumerate(section8) if b!=255),'printable_runs':[x.decode('ascii') for x in re.findall(rb'[ -~]{12,}',section8)][:30],'purpose':'Unclassified; no execution/load purpose established in this audit.'}
report['confirmed_startup_constants']={}
for address,opcode,value in [(0x4000045e,'45f9',0x4028f000),(0x40000470,'b5fc',0x402948f0),(0x40000486,'45f9',0x402948f0),(0x40000498,'b5fc',0x4029c4b0),(0x400004ba,'207c',0x4028f000),(0x400004c0,'223c',0x4322ae60)]:
 raw=new[address-BASE:address-BASE+6];assert raw==bytes.fromhex(opcode)+value.to_bytes(4,'big')
 report['confirmed_startup_constants'][hex(address)]=hex(value)
report['firmware_hashes_after_analysis']={'1.42':hashlib.sha256(oldpath.read_bytes()).hexdigest(),'1.44':hashlib.sha256(newpath.read_bytes()).hexdigest(),'baseline_main':hashlib.sha256(old).hexdigest()}
assert report['firmware_hashes_after_analysis']['1.42']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
assert report['firmware_hashes_after_analysis']['1.44']=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
assert report['firmware_hashes_after_analysis']['baseline_main']=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
Path('outputs/Digitone-OS1.44-migration-comparison.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
