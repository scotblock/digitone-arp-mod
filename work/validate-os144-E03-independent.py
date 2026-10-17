from pathlib import Path
import sys,json,hashlib,struct,math,runpy,subprocess
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import decode_syx,sections
from dt2.elz import depack_section
asset=runpy.run_path('work/validate-startup-decompression.py')['decode_asset']
p=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx');raw=p.read_bytes();dec=decode_syx(p);n,stored=struct.unpack_from('>II',dec);container=dec[8:8+n]
assert len(container)==n and n%512==0 and not any(dec[8+n:]);assert sum((i+1)^v[0] for i,v in enumerate(struct.iter_unpack('>I',container)))&0xffffffff==stored
_,es=sections(p);stock=Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx');original,oes=sections(stock);osids={sid:(o,l,d) for sid,o,l,d in oes}
for sid,o,l,d in es:
 if sid!=3:
  oo,ll,dd=osids[sid];assert (l,d)==(ll,dd) and container[o:o+l]==original[oo:oo+ll]
o,l,d=next(x[1:] for x in es if x[0]==3);packed=container[o:o+l];image,info,tokens=asset(packed)
assert image==Path('work/os144/emulator-E02-main.bin').read_bytes() and depack_section(packed)==image
assert info['header_checksum_matches'] and info['consumed']==len(packed)-8
source,dest=0x40200000,0x40000400;gaps=[source+t[3]-(dest+t[2]-1) for t in tokens];assert min(gaps)>0
r={'passed':True,'sha256':hashlib.sha256(raw).hexdigest(),'packet_checks':{},'all_other_sections_unchanged':True,'exact_E02_executable':True,'decompression':info,'in_place':{'source':hex(source),'destination':hex(dest),'minimum_first_unread_byte_to_last_output_write_gap':min(gaps),'all_literal_and_match_writes_before_unread_input':True,'tokens_checked':len(tokens)},'content_checksum':True,'512_byte_logical_container_alignment':True,'negative_checks':[]}
def transport(b):
 bodies=[];i=0
 while i<len(b):
  assert b[i]==240;j=b.index(247,i+1);bodies.append(b[i+1:j]);i=j+1
 assert len(bodies[0])==14 and len(bodies[-1])==14
 first,last=bodies[0],bodies[-1];assert first[6]==1 and last[6]==2
 assert first[:6]+first[7:]==last[:6]+last[7:]
 base=first[7];start=(first[8]<<7)|first[9];seq=first[10];count=(first[11]<<14)|(first[12]<<7)|first[13]
 assert len(bodies)-2==count
 for i,body in enumerate(bodies[1:-1]):
  assert len(body)==126 and not any(v>127 for v in body)
  assert body[:6]==bytes.fromhex('00203c0d007e')
  assert ((body[6]<<7)|body[7])==start+((seq+i)>>7) and body[8]==((seq+i)&127)
  assert body[125]==((base+sum(v^(base+j) for j,v in enumerate(body[6:125])))&127)
 return count
r['packet_checks']={'data_packets':transport(raw),'framing_and_checksums':True,'sequence_contiguous':True}
result=subprocess.run(['work/c-verification/verify-E03.exe',str(p)],capture_output=True,text=True);assert result.returncode==0;r['independent_C_verifier']=result.stdout
for name,mutation in [('packet_checksum',lambda b:b.__setitem__(16+126,b[16+126]^1)),('truncated_end_marker',lambda b:b.__delitem__(slice(-16,None)) )]:
 b=bytearray(raw);mutation(b)
 try:transport(b)
 except (AssertionError,ValueError):r['negative_checks'].append({'case':name,'rejected':True})
 else:raise AssertionError(name+' not rejected')
# Corrupted content also exercises the independent C verifier.
b=bytearray(raw);b[26]^=1;bad=Path('work/os144/E03-corrupt-packet-test.syx');bad.write_bytes(b)
x=subprocess.run(['work/c-verification/verify-E03.exe',str(bad)],capture_output=True,text=True);assert x.returncode!=0;r['negative_checks'].append({'case':'corrupted transport content','C_rejected':True,'result':x.stdout})
Path('outputs/Digitone-OS1.44E03-independent-checks.json').write_text(json.dumps(r,indent=2));print(json.dumps({'passed':True,'minimum_in_place_gap':min(gaps),'data_packets':r['packet_checks']['data_packets'],'negative_checks':len(r['negative_checks'])},indent=2))
