"""Execute actual counted startup-table traversal; callbacks supplied as returns."""
exec(open('work/test-resident-caller-helpers.py').read().split('checks=[];cases=[];OWNER=')[0])
count=int.from_bytes(b[0x40241ab4-base:0x40241ab8-base],'big');table=0x40241ab8
entries=[int.from_bytes(b[table-base+4*j:table-base+4*j+4],'big') for j in range(count)]
assert all(base<=x<0x40241ab4 and x%2==0 for x in entries)
RANGES.append((0x4008c7d4,0x4008c7f4))
tablesrc=rtsrc.replace('def route(self,entry,stop):','def table_route(self,entry,stop):').replace('   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)',"   if pc in entries:\n    self.callbacks.append(pc);pc=self.get('(a7)+',4);continue\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)")
exec('if True:\n'+tablesrc);Machine.table_route=table_route
m=create();m.callbacks=[];sp=m.reg['a7'];m.table_route(0x4008c7d4,0x4008c7f4)
assert m.callbacks==entries and m.reg['a3']==0x40241c94 and m.reg['a2']==119 and m.reg['a7']==sp
p=pathlib.Path('outputs/Digitone-resident-installation-route-audit.json');r=json.loads(p.read_text());r['actual_table_traversal']={'instruction_steps':len(m.steps),'callback_count':len(m.callbacks),'final_pointer':hex(m.reg['a3']),'callbacks':'supplied immediate returns; callback bodies not executed','stack_restored':True}
# Raw odd-alignment matches overlap instruction bytes, not address operands.
classifications=[(0x400057a5,0x400057a4,'7040241fd1b9'),(0x40030e27,0x40030e26,'4240241f4e75'),(0x4003243f,0x4003243c,'10280140241f245f'),(0x40129f8d,0x40129f8a,'103c0040241f8280')]
for loc,lo,h in classifications:
 assert b[lo-base:lo-base+len(bytes.fromhex(h))].hex()==h
 item=next(x for x in r['raw_literal_references_into_gap'] if x['location']==hex(loc));item['classification']='overlapping instruction bytes at odd alignment, not a decoded address operand';item['surrounding_decode']=[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(bytes.fromhex(h),lo)]
p.write_text(json.dumps(r,indent=2));print('PASS actual table traversal:',len(m.callbacks),'callbacks;',len(m.steps),'instructions; all four raw gap matches classified')
