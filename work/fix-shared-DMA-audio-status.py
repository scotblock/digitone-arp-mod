import pathlib
p=pathlib.Path('work/shared_dma_arbiter.py');s=p.read_text()
s=s.replace("  if not state.get('ssi'):\n   c=state['channel'];c._w16(e.CSR,(c._u16(e.CSR)&~(e.CSR_DONE|e.CSR_START))|e.CSR_ACTIVE)", "  if state.get('ssi'):\n   self.ssi._w16(ch,e.CSR,(self.ssi._u16(ch,e.CSR)&~(e.CSR_DONE|e.CSR_START))|e.CSR_ACTIVE)\n  else:\n   c=state['channel'];c._w16(e.CSR,(c._u16(e.CSR)&~(e.CSR_DONE|e.CSR_START))|e.CSR_ACTIVE)")
s=s.replace('   s.half_loops+=1;s.int50_asserted=True;s.int50_delivered=False', '   s.half_loops+=1;s.int50_asserted=True;s.int50_delivered=False\n  s._w16(ch,e.CSR,(s._u16(ch,e.CSR)&~(e.CSR_ACTIVE|e.CSR_START|e.CSR_DONE))|(e.CSR_DONE if citer==1 else 0))')
p.write_text(s)
