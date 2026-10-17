import json,hashlib,struct,sys
from pathlib import Path
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.cfisa import decode
mapping={0x4009719e:0x40097a94,0x4009ddac:0x4009e694,0x41345ef8:0x41392fbc,0x4009de50:0x4009e738,0x41344530:0x413915f4,0x41345f08:0x41392fcc,0x41345620:0x413926e4,0x40093efc:0x400947f4,0x4009dfa2:0x4009e88a,0x400f062c:0x400ffff8,0x400ec284:0x400fbb20,0x4199dad8:0x419ebe70,0x400f050e:0x400ffeda,0x4199da94:0x419ebe2c,0x419a304c:0x419f182c,0x400ec23c:0x400fbad8,0x40093454:0x40093d4c}
stock=Path('work/os144/section-3.bin').read_bytes();oldstock=Path('work/section-3.bin').read_bytes();base=0x40000400
assert stock[0x40094c38-base:0x40094c38-base+4]==struct.pack('>I',mapping[0x419a304c])
assert oldstock[0x40094340-base:0x40094340-base+4]==struct.pack('>I',0x419a304c)
info=json.loads(Path('work/packed-context-build.json').read_text());ports=[]
for name,ranges in [('packed-context-overlay',[(0,info['code_bytes'])]),('cache-context-overlay',[(0,1892),(2368,2564)])]:
 original=Path('work/'+name+'.bin').read_bytes();blob=bytearray(original);changes=[]
 for start,end in ranges:
  p=start
  while p<end:
   ins=decode(lambda r:struct.unpack_from('>H',original,p+r)[0],0x47be0000+p)
   for k in range(2,ins.length-3,2):
    value=int.from_bytes(original[p+k:p+k+4],'big')
    if value in mapping:
     blob[p+k:p+k+4]=mapping[value].to_bytes(4,'big');changes.append({'offset':p+k,'old':hex(value),'new':hex(mapping[value]),'instruction':hex(0x47be0000+p)})
   p+=ins.length
  assert p==end,(name,p,end)
 path=Path('work/os144/'+name+'.bin');path.write_bytes(blob)
 assert len(blob)==len(original)
 ports.append({'name':name,'path':str(path),'size':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'changes':changes})
hooks=[]
for old,new,length,name in [(0x40093ef4,0x400947ec,8,'producer_capture'),(0x400f0626,0x400ffff2,6,'allocate_clear'),(0x4009dda6,0x4009e68e,6,'before'),(0x4009de46,0x4009e72e,10,'caller_commit'),(0x4009df9a,0x4009e882,8,'pitch_hook'),(0x4009344e,0x40093d46,6,'first_copy'),(0x40093892,0x4009418a,6,'copy')]:
 hooks.append({'name':name,'old_site':hex(old),'site':hex(new),'length':length,'stock_bytes':stock[new-base:new-base+length].hex(),'helper':info['layout'][name]['address']})
result={'firmware_modified':False,'startup_hook_installed':False,'PC_only_helper_images':ports,'mapping':{hex(k):hex(v) for k,v in mapping.items()},'layout':info['layout'],'code_bytes':info['code_bytes'],'hooks':hooks,'cache_base_evidence':{'old_operand_at':'0x40094340','new_operand_at':'0x40094c38','new_cache_base':'0x419f182c'},'limits':['Operand port only; stock cancellation stays upstream of insertion points.','No assertion that direct pitch helper detects cancellation by itself.','No startup installation or full playback integration performed.']}
Path('work/os144/helper-port.json').write_text(json.dumps(result,indent=2));print('Ported',[(r['name'],len(r['changes'])) for r in ports])
