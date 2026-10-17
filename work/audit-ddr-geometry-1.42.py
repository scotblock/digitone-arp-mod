"""Decode only the stock straight-line DDR setup; no firmware edits."""
import pathlib,json,hashlib
x=pathlib.Path('work/section-2.bin').read_bytes();pc=0x32c;end=0x4ee
d0=0;writes=[]
while pc<end:
 raw=x[pc:pc+6];op=raw[:2]
 if op==bytes.fromhex('203c'):d0=int.from_bytes(raw[2:6],'big');size=6
 elif raw[0]==0x70:d0=int.from_bytes(raw[1:2],'big',signed=True)&0xffffffff;size=2
 elif op in [bytes.fromhex('4200'),bytes.fromhex('4240'),bytes.fromhex('4280')]:
  bits={bytes.fromhex('4200'):8,bytes.fromhex('4240'):16,bytes.fromhex('4280'):32}[op];d0&=~((1<<bits)-1);size=2
 elif op==bytes.fromhex('303c'):d0=(d0&0xffff0000)|int.from_bytes(raw[2:4],'big');size=4
 elif op in [bytes.fromhex('23c0'),bytes.fromhex('42b9')]:
  writes.append({'pc':hex(0x02000800+pc),'address':hex(int.from_bytes(raw[2:6],'big')),'value':hex(d0 if op==bytes.fromhex('23c0') else 0)});size=6
 else:raise AssertionError((hex(pc),raw.hex()))
 pc+=size
assert pc==end
regs={int(a['address'],16):int(a['value'],16) for a in writes}
assert [regs[a] for a in [0xfc0b8010,0xfc0b803c,0xfc0b8040]]==[0x10101,0x2000103,0x2000407]
rows=16-((regs[0xfc0b803c]>>24)&7);cols=12-((regs[0xfc0b8040]>>24)&7);banks=8 if regs[0xfc0b8010]&256 else 4
size=(1<<(rows+cols))*banks
assert size==128*1024*1024
r={'firmware_modified':False,'bootstrap_sha256':hashlib.sha256(x).hexdigest(),'setup_file_interval':[hex(0x32c),hex(end)],'writes':writes,'geometry':{'rows':rows,'columns':cols,'banks':banks,'bytes':size},'canonicalization':'0x40000000 + ((address - 0x40000000) % 0x08000000), for SDRAM 0x40000000..0x80000000','reserved_aliases':[hex(0x47be0000+i*size) for i in range(8)],'sources':['https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf','https://github.com/irpina/digiemu/blob/24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2/tools/ddr_geometry.py'],'limits':['Static controller configuration decode; not a measurement of the physical board.','No cache or DMA timing model.']}
pathlib.Path('outputs/Digitone-OS1.42-DDR-geometry.json').write_text(json.dumps(r,indent=2));print('PASS: stock geometry',rows,cols,banks,size//(1024*1024),'MiB;',len(writes),'decoded writes')
