from pathlib import Path
import json
port=json.loads(Path('work/os144/helper-port.json').read_text());info=json.loads(Path('work/packed-context-build.json').read_text())
s=Path('work/test-native-arp-controlled.py').read_text()
prefix='''
import sys,struct,hashlib,traceback
exec(Path('work/os144-stock-env.py').read_text())
from emu.harness import Machine
from unicorn.m68k_const import *
RAM,PTR,BSS=0x47be0000,0x47be1000,0x47be1004
blob=Path('work/os144/packed-context-overlay.bin').read_bytes();layout=info['layout']
rows={r['raw_scale']:r['pitch_classes'] for r in json.loads(Path('outputs/Digitone-OS1.42-scale-map.json').read_text())['scales']}
def oracle(note,word):
 raw=((word>>7)&63)-1;root=word&127
 if not word>>31 or raw not in rows or not 0<=note<128:return note
 return min((n for n in range(128) if (n-root)%12 in rows[raw]),key=lambda n:(abs(n-note),n))
class Session:
 def __init__(self,*args,on_machine=None,**kw):
  self.m=Machine(ddr=DDR);stock=Path('work/os144/section-3.bin').read_bytes()
  for offset in range(0,len(stock)+0x400,0x100000):self.m.ensure(0x40000000+offset)
  for address in [RAM,0x47fdff00,0x47bccf04,0x419ebe2c,0x413915f4]:self.m.ensure(address)
  self.m.uc.mem_write(0x40000400,stock)
  on_machine(self)
 def close(self):pass
'''
line=next(x for x in s.splitlines() if x.startswith('exec(pathlib.Path'))
s=s.replace(line,prefix)
for old,new in port['mapping'].items():s=s.replace(old,new)
for h in port['hooks']:s=s.replace(h['old_site'],h['site'])
s=s.replace('0x4009dfa8','0x4009e890')
s=s.replace('m.install_isa_patches_scoped(blob,RAM)',"m.install_isa_patches_scoped(blob[:info['code_bytes']],RAM)")
s=s.replace('Digitone-native-arp-controlled-results.json','Digitone-OS1.44-native-helper-ABI.json')
s=s.replace('in restored native engine','in isolated 1.44 instruction engine')
exec(compile(s,'OS1.44-native-helper-ABI','exec'))
