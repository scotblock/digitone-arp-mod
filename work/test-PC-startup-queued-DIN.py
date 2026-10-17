"""Queue DIN bytes before note initialization and continue actual startup."""
from pathlib import Path
import json
queued_DIN_original_read=Path.read_text
def queued_DIN_source_read(path,*args,**kwargs):
 s=queued_DIN_original_read(path,*args,**kwargs)
 if path.name=='test-PC-startup-producer-order.py':
  s=s.replace('startup-producer-order-','startup-queued-DIN-')
  anchor="  saved_points=set();input_hook_ids={}"
  assert anchor in s;s=s.replace(anchor,"  row['startup_DIN_injection']=None\n"+anchor)
  anchor="   if pc==0x4008d3ec:u.hook_del(input_hook_ids[(order_stage[0],pc)])"
  injection=r'''
   if order_stage[0]=='cold' and pc==0x4009d0d8 and row['startup_DIN_injection'] is None:
    from emu import midi
    channel=getword(u,0x41368d2c)&15
    row['startup_DIN_injection']={'site':hex(pc),'channel':channel,'bytes':bytes([0x90|channel,64,100]).hex(),'before':inputstate(u),'read_index_before':getword(u,0x405285cc),'no_gate_changes':True}
    midi.feed(m,bytes([0x90|channel,64,100]))
    row['startup_DIN_injection']['interrupt_taken']=midi._take(m,156)
'''
  assert anchor in s;s=s.replace(anchor,anchor+'\n'+injection)
 return s
Path.read_text=queued_DIN_source_read
try:exec(compile(queued_DIN_source_read(Path('work/test-PC-startup-producer-order.py')),'queued-DIN-through-startup','exec'))
finally:Path.read_text=queued_DIN_original_read
