from pathlib import Path
import struct,sys,hashlib,json,math
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import decode_syx,sections
from dt2.elz import depack_section
SOURCE=Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx');OUT=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx')
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=SOURCE.read_bytes();decoded=decode_syx(SOURCE);stock_n=struct.unpack_from('>I',decoded)[0];stock_c=decoded[8:8+stock_n];_,entries=sections(SOURCE)
packed=Path('work/os144/E03-main-packed.bin').read_bytes();main=Path('work/os144/emulator-E02-main.bin').read_bytes();assert depack_section(packed)==main
assert struct.unpack_from('>II',packed)==(len(packed)-8,sum(packed[8:])&0xffffffff)
def container(replacement=None,align=16):
 c=bytearray(stock_c[:min(e[1] for e in entries)]);es=[]
 for sid,off,n,dest in entries:
  c.extend(bytes((-len(c))%16));at=len(c);data=replacement if sid==3 and replacement is not None else stock_c[off:off+n]
  c.extend(data);es.append((sid,at,len(data),dest))
 for i,e in enumerate(es):struct.pack_into('>IIII',c,32+i*16,*e)
 c.extend(bytes((-len(c))%align));return bytes(c),es

def syx(c):
 checksum=sum((i+1)^w[0] for i,w in enumerate(struct.iter_unpack('>I',c)))&0xffffffff
 stream=struct.pack('>II',len(c),checksum)+c;count=math.ceil(len(stream)/101);stream+=bytes(count*101-len(stream))
 first=bytearray(raw[1:15]);base=first[7];start=(first[8]<<7)|first[9];seq=first[10];first[11:14]=bytes([(count>>14)&127,(count>>7)&127,count&127]);out=bytearray(b'\xf0'+first+b'\xf7')
 for i in range(count):
  block=start+((seq+i)>>7);body=bytearray(b'\x00\x20\x3c\x0d\x00\x7e'+bytes([(block>>7)&127,block&127,(seq+i)&127]));chunk=stream[i*101:(i+1)*101]
  for k in range(0,101,7):
   group=chunk[k:k+7];body.append(sum(((v>>7)&1)<<(6-j) for j,v in enumerate(group)));body.extend(v&127 for v in group)
  assert len(body)==125;body.append((base+sum(v^(base+j) for j,v in enumerate(body[6:])))&127);out.extend(b'\xf0'+body+b'\xf7')
 first[6]=2;out.extend(b'\xf0'+first+b'\xf7');return bytes(out)
unchanged,_=container();assert unchanged==stock_c,'unchanged container reconstruction mismatch';assert syx(unchanged)==raw,'unchanged writer not byte exact'
c,es=container(packed,512);assert len(c)<0x1e0000-8 and 0x80000+math.ceil(len(c)/0x40000)*0x40000<=0x380000
OUT.write_bytes(syx(c));Path('work/os144/E03-container.bin').write_bytes(c)
last_end=max(o+n for sid,o,n,dest in es);canonical=math.ceil(last_end/16)*16
r={'PC_only':True,'source_sha256':sha(raw),'output':str(OUT.resolve()),'output_sha256':sha(OUT.read_bytes()),'main_sha256':sha(main),'main_identical_to_E02':True,'unchanged_writer_byte_exact':True,'packed_main_bytes':len(packed),'container_bytes':len(c),'canonical_16_aligned_length':canonical,'additional_zero_tail_bytes':len(c)-canonical,'padding_policy':'Logical ELE3 container extended with zero tail to 512-byte alignment; checksum and advertised length cover all tail bytes. No extra unadvertised transport packets.','syx_bytes':OUT.stat().st_size,'compressor_sha256':sha(Path('work/elektron-firmware-tool/aplib.c').read_bytes()),'compression_level':2,'sections':es,'independent_Python_decompression':True,'C_codec_roundtrip':True,'hardware_ready':False,'remaining':['Stock loader acceptance of the extra zero tail not yet checked.','Complete receiver/update session and error paths unverified.','Startup fail-stop, global RAM ownership and physical cache/audio timing remain unverified.']}
Path('outputs/Digitone-OS1.44E03-packaging.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in ['output_sha256','packed_main_bytes','container_bytes','additional_zero_tail_bytes','syx_bytes','unchanged_writer_byte_exact']},indent=2))
