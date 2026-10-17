from pathlib import Path
import sys,json,struct,hashlib,subprocess
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections
from dt2.elz import depack_section
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
sha=lambda x:hashlib.sha256(x).hexdigest()
ROOT=Path('work/os144');MB=0x40000400;PB=0x47be0000;OLD=0x47fa0000;NEW=0x47be3800
main=bytearray((ROOT/'PC_ONLY-atomic-storage-main.bin').read_bytes());payload=bytearray((ROOT/'PC_ONLY-atomic-storage-payload.bin').read_bytes());payload.extend(bytes(0x4804-len(payload)))
components=[];relocations=[];hooks=[]
def mapped(a):return NEW+a-OLD if OLD<=a<OLD+0x1000 else a
def relocate(code,origin):
 code=bytearray(code)
 for p in range(0,len(code)-3,2):
  a=int.from_bytes(code[p:p+4],'big')
  if OLD<=a<OLD+0x1000:
   relocations.append({'operand':hex(mapped(origin)+p),'old':hex(a),'new':hex(mapped(a))});code[p:p+4]=struct.pack('>I',mapped(a))
 return bytes(code)
for name in ['persistent-admission','cold-admission-overlay','input-live-overlay','release-reset-overlay','resident-deferred-release-overlay']:
 spec=json.loads((ROOT/('PC_ONLY-'+name+'.json')).read_text());code=(ROOT/('PC_ONLY-'+name+'.bin')).read_bytes();assert sha(code)==spec['sha256']
 base=mapped(spec['base']);code=relocate(code,spec['base']);payload[base-PB:base-PB+len(code)]=code
 components.append({'name':name,'base':base,'bytes':len(code),'sha256_before_completion_patch':sha(code),'layout':{k:{**v,'address':mapped(v['address'])} for k,v in spec['layout'].items()}})
 for h in spec['hooks']:
  site=mapped(h['site']);prev=bytes.fromhex(h.get('previous',h.get('stock')));prev=relocate(prev,h['site']);replacement=relocate(bytes.fromhex(h['replacement']),h['site'])
  buf=payload if site>=PB else main;off=site-(PB if site>=PB else MB)
  assert bytes(buf[off:off+h['length']])==prev,(name,hex(site),bytes(buf[off:off+h['length']]).hex(),prev.hex())
  buf[off:off+h['length']]=replacement;hooks.append({'name':name+':'+h['name'],'site':site,'previous':prev.hex(),'replacement':replacement.hex(),'length':h['length']})
diag=0x47be4800;payload[diag-PB:diag-PB+2]=bytes.fromhex('4e75');site=0x4009c6d0;previous=bytes(main[site-MB:site-MB+8]);assert previous.hex()=='2f0b2f0a4ebafeca'
main[site-MB:site-MB+8]=bytes.fromhex('4ef9')+struct.pack('>I',diag)+bytes.fromhex('4e71');hooks.append({'name':'diagnostic_outer_refuse','site':site,'length':8,'previous':previous.hex(),'replacement':bytes(main[site-MB:site-MB+8]).hex()})
components.append({'name':'diagnostic_outer_refuse','base':diag,'bytes':2,'layout':{'refuse':{'address':diag,'size':2}}})
main[0x4029c4be-MB:0x4029c4c2-MB]=struct.pack('>I',len(payload)//4);main[0x4029c5b0-MB:]=payload
assert bytes(payload[0x2860:0x29f0])==bytes(400) and bytes(payload[0x2840:0x2844])==bytes(4)
port=json.loads((ROOT/'helper-port.json').read_text())
regions=[{'name':'copier','base':0x4029c4b0,'bytes':110}]+[{'name':n,'base':v['address'],'bytes':v['size']} for n,v in port['layout'].items()]+[{'name':'live_capture','base':0x47be3000,'bytes':474},{'name':'storage_reset','base':0x47be3400,'bytes':304},{'name':'atomic_live_copy','base':0x47be3600,'bytes':182}]+[{'name':x['name'],'base':x['base'],'bytes':x['bytes']} for x in components]
checks=[]
for r in regions:
 buf=payload if r['base']>=PB else main;offset=r['base']-(PB if r['base']>=PB else MB);code=bytes(buf[offset:offset+r['bytes']]);p=0;count=0
 while p<len(code):
  ins=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),r['base']+p);assert ins.length>0 and p+ins.length<=len(code),(r,hex(r['base']+p),ins)
  assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big')),(r,hex(r['base']+p),ins)
  p+=ins.length;count+=1
 checks.append({'name':r['name'],'instructions':count,'passed':True})
for p in range(0,len(payload)-3,2):assert not OLD<=int.from_bytes(payload[p:p+4],'big')<OLD+0x1000,hex(PB+p)
(ROOT/'E05-PC-main.bin').write_bytes(main);(ROOT/'E05-PC-payload.bin').write_bytes(payload)
proc=subprocess.run(['work/c-verification/pack-review.exe',str(ROOT/'E05-PC-main.bin'),str(ROOT/'E05-PC-main-packed.bin')],capture_output=True,text=True);assert proc.returncode==0,proc.stdout+proc.stderr
# Reuse the independently round-tripped stock writer, with local stock recovery source.
source=Path('work/build-os144-E03-pc.py').read_text().split('unchanged,_=container()')[0]
source=source.replace("inputs/Digitone_and_Digitone_Keys_OS1.44.syx","outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx").replace('E03-main-packed.bin','E05-PC-main-packed.bin').replace('emulator-E02-main.bin','E05-PC-main.bin')
env={};exec(compile(source,'E05-stock-writer','exec'),env);original,_=env['container']();assert original==env['stock_c'] and env['syx'](original)==env['raw']
c,entries=env['container'](env['packed'],512);assert len(c)<0x1e0000-8 and 0x80000+((len(c)+0x3ffff)//0x40000)*0x40000<=0x380000
syx=env['syx'](c);candidate=ROOT/'E05-PC-candidate.syx';candidate.write_bytes(syx);(ROOT/'E05-PC-container.bin').write_bytes(c)
parsed,es=sections(candidate)
for sid,off,n,dest in es:
 if sid==3:assert depack_section(parsed[off:off+n])==bytes(main)
out={'PC_only':True,'hardware_ready':False,'candidate':str(candidate.resolve()),'candidate_sha256':sha(syx),'main_sha256':sha(main),'payload_sha256':sha(payload),'payload_bytes':len(payload),'copy_longwords':len(payload)//4,'sections':entries,'container_bytes':len(c),'syx_bytes':len(syx),'components':components,'regions':regions,'hooks':hooks,'relocations':relocations,'strict_ISA':checks,'codec_roundtrip':proc.stdout.strip(),'stock_writer_byte_exact':True,'candidate_decompression_exact':True,'policy':'Consolidated corrected startup/live-capture/admission/reset/UI/deferred-release helpers are delivered by the native payload copier. Unsupported diagnostic queue entry returns before mutation. Global shared-owner release is unchanged.','limits':['RAM extension through 47be4804 has not been physically certified.','Existing masked failure stop remains; this is not a guarantee of graceful hardware fallback.','Application-wide shutdown/worker quiescence and unknown reset callers remain unresolved.','PC loader/device/cache/IRQ/timing shortcuts cannot certify physical behavior.']}
Path('outputs/Digitone-E05-PC-candidate-layout.json').write_text(json.dumps(out,indent=2));print('Consolidated PC candidate:',len(payload),'copied bytes;',len(relocations),'address relocations;',len(hooks),'guard hooks; strict ISA and codec checks passed')
