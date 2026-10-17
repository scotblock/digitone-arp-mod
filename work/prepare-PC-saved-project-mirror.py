from pathlib import Path
import sys,zlib,struct,json,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.snapshot import _load_blob
from emu.harness import PAGE
from emu import sparse
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *
snapshot=Path('work/user-session-audio/stock/snapshots/Digitone_OS1.44/resume.snap')
blob=_load_blob(str(snapshot));pages={}
def read(addr,size):
 data=bytearray()
 while size:
  base=addr&~(PAGE-1)
  if base not in pages:pages[base]=zlib.decompress(blob['pages'][base]) if base in blob['pages'] else bytes(PAGE)
  n=min(size,PAGE-(addr-base));data.extend(pages[base][addr-base:addr-base+n]);addr+=n;size-=n
 return bytes(data)
payload=read(0x40555ee4,0x2a7514)
uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);uc.ctl_set_cpu_model(UC_CPU_M68K_CFV4E)
main=Path('work/os144/section-3.bin').read_bytes()
uc.mem_map(0x40085000,4096);uc.mem_write(0x40085000,main[0x40085000-0x40000400:0x40086000-0x40000400])
uc.mem_map(0x40555000,8192);uc.mem_write(0x40555ee4,payload[:0x200]);uc.mem_map(0x4136b000,4096);uc.mem_map(0x50000000,4096)
uc.reg_write(UC_M68K_REG_SR,0x2000);uc.reg_write(UC_M68K_REG_A7,0x50000800)
uc.mem_write(0x50000800,struct.pack('>II',0x50000000,0x40555ee4));uc.emu_start(0x4008521e,0x50000000,count=1000)
valid=uc.reg_read(UC_M68K_REG_D0);assert valid==1,'The saved header must pass the actual stock validator without alteration.'
source=Path('work/user-session-audio/stock/plusdrive.img')
out={'PC_only':True,'header_stock_validator_return':valid,'header':payload[:0x68].hex(),'payload_sha256':hashlib.sha256(payload).hexdigest(),'payload_bytes':len(payload),'snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),'fixtures':[],'limits':['Mirror payload copied from saved emulator RAM; not extracted physical storage.','Header accepted without recomputing or changing its checksum. Only the header validation contract is exercised here; full restoration is tested separately.']}
for name in ['valid_first','invalid_first_valid_second']:
 path=Path('work/os144/PC_ONLY-saved-mirror-'+name+'.img')
 with source.open('rb') as f,path.open('wb') as dest:
  sparse.make_sparse(dest);sparse.extend(dest,source.stat().st_size)
  while block:=f.read(1024*1024):
   if block.strip(b'\0'):dest.seek(f.tell()-len(block));dest.write(block)
  if name=='valid_first':dest.seek(0xf400000);dest.write(payload)
  else:
   bad=bytearray(payload);bad[4]^=1
   dest.seek(0xf400000);dest.write(bad);dest.seek(0xf800000);dest.write(payload)
 out['fixtures'].append({'name':name,'path':str(path),'fixture_change':'Install the complete retained RAM mirror at first bank' if name=='valid_first' else 'Flip one checksum byte in first bank and install unchanged retained RAM mirror in second bank'})
Path('outputs/Digitone-E04-PC-saved-mirror-fixtures.json').write_text(json.dumps(out,indent=2)+'\n')
print('stock header validation',valid,'payload',len(payload),out['payload_sha256'])
