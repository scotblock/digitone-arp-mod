"""Explicit producer/begin/success/commit/pitch sequence, no DMA or scheduling."""
import pathlib
exec(pathlib.Path('work/measure-packed-pitch-local-cost.py').read_text().split("exec(compile(source,")[0])
source=source.replace("m.install_isa_patches_scoped(blob[:info['code_bytes'] if mode=='packed' else 1892],ram)","m.install_isa_patches_scoped(blob[:info['code_bytes'] if mode=='packed' else 1892],ram)\n if mode=='original':m.install_isa_patches_scoped(blob[2368:],ram+2368)")
a=source.index(' for repetition in range(3):');b=source.index(' assert c.decode_mismatches==0',a)
source=source[:a]+'''
 def execute(start,end,sp=0x47fdff00):
  uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A7,sp)
  uc.emu_start(start,end,count=100000);assert uc.reg_read(UC_M68K_REG_PC)==end
 for repetition in range(3):
  before=c.cycles;instructions=c.instructions;counts=dict(mem.counts);parts.clear()
  pattern=0x47bc0000;m.ensure(pattern)
  uc.mem_write(pattern+track*0x3d0+0x3cb,bytes([59]));uc.mem_write(pattern+track*0x3d0+0x3ce,bytes([5]))
  uc.reg_write(UC_M68K_REG_A3,pattern);uc.reg_write(UC_M68K_REG_A2,event);uc.reg_write(UC_M68K_REG_D4,track)
  execute(layout['producer_capture']['address'],0x40093efc)
  uc.mem_write(0x47fdff00,u32(0x12345678)+u32(track));execute(layout['before']['address'],0x4009719e)
  # Explicit successful selector result; no claim to execute the stock selector.
  uc.reg_write(UC_M68K_REG_D0,1);execute(layout['after']['address'],0x4009ddac,0x47fdff04)
  uc.reg_write(UC_M68K_REG_A3,event);execute(layout['caller_commit']['address'],0x4009de50)
  uc.reg_write(UC_M68K_REG_A3,event);uc.reg_write(UC_M68K_REG_D6,57)
  execute(0x4009df9a,0x4009dfa8)
  assert uc.reg_read(UC_M68K_REG_D6)==57<<16
  assert int.from_bytes(uc.mem_read(bss+32+(event-0x4199da94)//72*4,4),'big')==word
  rows.append({'mode':mode,'repetition':repetition,'cache_state':'cold' if repetition==0 else 'self-warmed','cycles':c.cycles-before,'instructions':c.instructions-instructions,'memory_costs':{k:v-counts.get(k,0) for k,v in mem.counts.items() if k.endswith('_stall_cycles')},'helper_parts':{k:dict(v) for k,v in parts.items()}})
''' +source[b:]
source=source.replace('Digitone-packed-pitch-local-cost.json','Digitone-packed-combined-local-cost.json')
source=source.replace('No scheduler or DMA execution.','Explicit producer/begin/success/commit/pitch sequence, supplied successful selector result. No actual producer ordering, stock selector, scheduler or DMA execution.')
exec(compile(source,'packed-combined-local-cost','exec'))
