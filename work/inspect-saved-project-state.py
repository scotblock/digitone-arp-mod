from pathlib import Path
import sys,json,hashlib,zlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.snapshot import _load_blob
from emu.harness import PAGE
import numpy as np
out={'PC_only':True,'cards':[],'resume_snapshots':[]}
factory=Path('work/os144-emulator-E02-engine/plusdrive.img')
for label,path in [('factory',factory),('saved_stock',Path('work/user-session-audio/stock/plusdrive.img')),('saved_modified',Path('work/user-session-audio/modified/plusdrive.img'))]:
 row={'label':label,'path':str(path),'size':path.stat().st_size};out['cards'].append(row)
 h=hashlib.sha256();changed=[]
 with factory.open('rb') as ref,path.open('rb') as f:
  offset=0
  while block:=f.read(1024*1024):
   original=ref.read(len(block));h.update(block)
   a=np.frombuffer(block,dtype='u1').reshape(-1,512);b=np.frombuffer(original,dtype='u1').reshape(-1,512)
   changed.extend((np.flatnonzero(np.any(a!=b,axis=1))+offset//512).tolist());offset+=len(block)
 row['sha256']=h.hexdigest();row['changed_sectors_from_factory']=len(changed)
 groups=[]
 for sector in changed:
  if groups and groups[-1][1]==sector:groups[-1][1]=sector+1
  else:groups.append([sector,sector+1])
 row['changed_byte_intervals']=[[hex(lo*512),hex(hi*512)] for lo,hi in groups]
for mode in ['stock','modified']:
 path=Path('work/user-session-audio')/mode/'snapshots/Digitone_OS1.44/resume.snap'
 blob=_load_blob(str(path));pages={}
 def peek(addr,size):
  result=bytearray()
  while size:
   base=addr&~(PAGE-1)
   if base not in pages:pages[base]=zlib.decompress(blob['pages'][base]) if base in blob['pages'] else bytes(PAGE)
   n=min(size,PAGE-(addr-base));result.extend(pages[base][addr-base:addr-base+n]);addr+=n;size-=n
  return bytes(result)
 current=int.from_bytes(peek(0x4138f214,4),'big')
 row={'mode':mode,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'current_source_pointer':hex(current),'snapshot_pc':hex(blob['regs']['pc']),'patterns':[]}
 for source in sorted({current,0x407fd414,0x40813531}):
  data=peek(source,0x16111)
  row['patterns'].append({'source':hex(source),'pattern_sha256':hashlib.sha256(data).hexdigest(),'track_fields':[{'track_index':t,'root':data[t*0x3d0+0x3cb],'raw_scale':data[t*0x3d0+0x3ce]} for t in range(4)]})
 out['resume_snapshots'].append(row)
out['limits']=['Saved emulator cards and RAM snapshots are not physical Digitone project backups.','A resume snapshot starts after startup and cannot prove its current pattern was restored during cold boot.','Sector differences identify changed persistence; they do not by themselves identify the active project or prove that the firmware loaded it.']
Path('outputs/Digitone-E04-saved-project-state-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
