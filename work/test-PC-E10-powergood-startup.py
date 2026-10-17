"""Native cold startup with the stock board power-good input asserted."""
from pathlib import Path
import json,sys,zlib
exec(Path('work/audit-E04-startup-ISA.py').read_text(encoding='utf-8').split('\nregions=')[0])
cfg=json.loads(Path('work/os144/PC_ONLY-E10-life-full-layout.json').read_text())
proof=json.loads(Path('outputs/Digitone-E10-PC-life-cache-write.json').read_text());assert proof['passed']
source=Path('work/E10_powerfail_startup_template.py').read_text(encoding='utf-8')
source=source.replace('work/E10-life-startup-','work/E10-powergood-startup-').replace('Digitone-E10-PC-life-startup.json','Digitone-E10-PC-powergood-startup.json')
source=source.replace('work/E10-bound-panel-patterns/plusdrive.img',Path(proof['card']).as_posix())
source=source.replace('from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE','from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ')
fixture="""
  def install_power(mm):
   def good(u,access,a,n,value,data):
    u.mem_write(0xec09401e,bytes([u.mem_read(0xec09401e,1)[0]|8]))
   mm.uc.hook_add(UC_HOOK_MEM_READ,good,begin=0xec09401e,end=0xec09401e)
  install_power(m)
"""
source=source.replace('  sp=m.uc.reg_read(UC_M68K_REG_A7);',fixture+'  sp=m.uc.reg_read(UC_M68K_REG_A7);',1)
source=source.replace("   held['ev']=ev", "   held['ev']=ev\n   install_power(mm)")
exec(compile(source,'E10-power-good-native-cold-startup','exec'))
from emu.snapshot import _load_blob
from emu.harness import PAGE
p=Path('outputs/Digitone-E10-PC-powergood-startup.json');r=json.loads(p.read_text());assert r['passed']
b=_load_blob(r['cases'][0]['ui_snapshot']);pages={a:zlib.decompress(v) for a,v in b['pages'].items()}
def read(a,n):return bytes(pages.get((a+i)&~(PAGE-1),bytes(PAGE))[(a+i)&(PAGE-1)] for i in range(n))
assert read(0x4139420c,1)==b'\x01', 'Stock power-good gate did not arm'
assert read(cfg['E10']['bank'],4096)==bytes.fromhex(proof['expected_bank'])
r.update(stock_powerfail_gate_armed=True,board_power_good_high_fixture=True,bank_records_preserved=128)
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
print('Native startup arms stock power-fail gate from board power-good pin.',flush=True)
