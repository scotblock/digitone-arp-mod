from pathlib import Path
s=Path('work/test-E05-PC-playback.py').read_text()
s=s.replace("[('stock_restored','ordinary'),('E05_restored','ordinary'),('stock_restored','scale'),('E05_restored','scale'),('E05_disabled','ordinary')]","[('E05_restored','scale')]")
s=s.replace('Digitone-E05-PC-playback-comparison.json','Digitone-E06-arp-offset-provenance.json')
anchor="   session.at(0x4009e890,lambda"
add="""   row['arithmetic_inputs']=[];row['offset_producers']=[]
   def signed(v):return v-0x100000000 if v&0x80000000 else v
   def arithmetic(u,pc,n,d):
    base=u.reg_read(UC_M68K_REG_D1);index=u.reg_read(UC_M68K_REG_D5);event=u.reg_read(UC_M68K_REG_A3)
    row['arithmetic_inputs'].append({'ms':session.now_ms(),'base':base,'global_offset':signed(rd(u,0x80003fc4)),'table_index':index,'table_adjustment':signed(rd(u,0x800034c4+index*4)),'event':hex(event),'note_index':u.reg_read(UC_M68K_REG_D4),'event_note_bytes':bytes(u.mem_read(event+0x18,8)).hex()})
   session.at(0x4009e870,arithmetic)
   def offset_writer(u,pc,n,d):
    event=u.reg_read(UC_M68K_REG_A3);ptr=u.reg_read(UC_M68K_REG_A0);pattern=rd(u,0x4138f214)
    row['offset_producers'].append({'ms':session.now_ms(),'event':hex(event),'source':hex(ptr),'source_pattern_delta':hex(ptr-pattern),'value':signed(u.reg_read(UC_M68K_REG_D2)),'type':rd(u,event),'pattern':hex(pattern),'fields':bytes(u.mem_read(event,64)).hex()})
   session.at(0x4009d4fc,offset_writer)
"""
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s[:s.index("ordinary={r['image']")]+"out['passed']=all(r.get('passed') for r in out['cases']);dest.write_text(json.dumps(out,indent=2));assert out['passed']\n"
exec(compile(s,'E06-offset-trace','exec'))
