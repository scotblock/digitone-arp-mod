from pathlib import Path
import sys,json,struct,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import sections,decode_syx
from dt2.elz import depack_section
path=Path('work/os144/E05-PC-candidate.syx');raw=path.read_bytes();messages=[];p=0
while p<len(raw):
 assert raw[p]==0xf0;j=raw.index(0xf7,p+1);body=raw[p+1:j];assert all(x<128 for x in body);messages.append(body);p=j+1
first,last=messages[0],messages[-1];count=(first[11]<<14)|(first[12]<<7)|first[13];assert len(first)==len(last)==14 and len(messages)==count+2 and first[:6]==last[:6] and last[6]==2
base=first[7];start=(first[8]<<7)|first[9];seq=first[10]
for i,body in enumerate(messages[1:-1]):
 assert len(body)==126 and body[:6]==bytes.fromhex('00203c0d007e') and body[6:9]==bytes([(start+((seq+i)>>7))>>7,(start+((seq+i)>>7))&127,(seq+i)&127])
 assert body[-1]==(base+sum(v^(base+j) for j,v in enumerate(body[6:-1])))&127
decoded=decode_syx(path);size,checksum=struct.unpack_from('>II',decoded);c=decoded[8:8+size];assert len(c)==size and size%512==0 and decoded[8+size:]==bytes(len(decoded)-8-size)
actual=sum((i+1)^w[0] for i,w in enumerate(struct.iter_unpack('>I',c)))&0xffffffff;assert actual==checksum
_,entries=sections(path);stock,se=sections(Path('outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx'));stock_by={sid:stock[off:off+n] for sid,off,n,dest in se};unchanged=[]
for sid,off,n,dest in entries:
 assert off%16==0 and off+n<=size
 if sid==3:
  packed=c[off:off+n];length,check=struct.unpack_from('>II',packed);assert length==len(packed)-8 and check==sum(packed[8:])&0xffffffff;assert depack_section(packed)==Path('work/os144/E05-PC-main.bin').read_bytes()
 else:assert c[off:off+n]==stock_by[sid];unchanged.append(sid)
old=json.loads(Path('outputs/Digitone-E04-PC-input-live-summary.json').read_text())
for name,h in old['hashes'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h
manifest=json.loads(Path('outputs/Digitone-E05-PC-candidate-layout.json').read_text());assert hashlib.sha256(raw).hexdigest()==manifest['candidate_sha256']
result={'PC_only':True,'passed':True,'transport_messages':count,'packet_checksum_and_sequence_verified':True,'container_length_checksum_and_padding_verified':True,'main_compressed_header_checksum_verified':True,'main_decompression_exact':True,'unchanged_sections':unchanged,'old_firmware_and_overlay_hashes_unchanged':True,'sha256':manifest['candidate_sha256'],'limits':['Independent framing/codec verification does not execute a physical updater or certify the new source/RAM ranges.']}
Path('outputs/Digitone-E05-PC-container-verification.json').write_text(json.dumps(result,indent=2));print('PASS transport',count,'packets; container and compressed checksums; exact MAIN decode; stock/E04 preserved')
