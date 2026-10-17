from pathlib import Path
s=Path('work/test-PC-queued-pattern-retirement.py').read_text();s=s.replace("['baseline','clear_after_publish','rebind_after_publish']","['native_parent_rebind']");s=s.replace("if not row['injected'] and mode!='baseline':","if False:")
anchor="   def event(label,**fields):row['events'].append({'kind':label,'ms':s.now_ms(),**fields})"
addition='''
   site=0x400a88d6;base=0x47fb0100;original=bytes(u.mem_read(site,6));assert original.hex()=='486a00102f06'
   head=bytes.fromhex('4fefffc048d77fff40c02f40003c4879407fd3f8487941a720a04eb9400283544fef0008')
   tail=bytes.fromhex('202f003c46c04cd77fff4fef0040')+original+bytes.fromhex('4ef9')+(site+6).to_bytes(4,'big');stub=head+tail
   s.m.load(stub,base);s.m.install_isa_patches_scoped(stub,base);u.mem_write(site,bytes.fromhex('4ef9')+base.to_bytes(4,'big'));row['PC_only_guest_stub']={'address':hex(base),'bytes':stub.hex(),'target':'0x40028354','parent':'0x41a720a0','new_project_base':'0x407fd3f8','new_pattern_destination':'0x40a96df8','displaced':original.hex()}
   def rebind_enter(u,pc,n,d):
    if builder['active']:event('native_parent_rebind_enter',prior_field=hex(rd(u,0x41a720f0)),prior_parent_base=hex(rd(u,0x41a720c0)))
   def rebind_return(u,pc,n,d):
    if not builder['active']:return
    assert rd(u,0x41a720f0)==0x40a96df8 and rd(u,0x41a720c0)==0x407fd3f8;row['injected']=True;event('native_parent_rebind_return',field=hex(rd(u,0x41a720f0)),parent_base=hex(rd(u,0x41a720c0)))
   s.at(0x40028354,rebind_enter);s.at(base+len(head),rebind_return)
'''
assert anchor in s;s=s.replace(anchor,anchor+addition);s=s.replace("if mode!='baseline':assert row['injected'] and kinds.index('field_fixture')<kinds.index('callback_selected')", "assert row['injected'] and kinds.index('queue_published')<kinds.index('native_parent_rebind_enter')<kinds.index('native_parent_rebind_return')<kinds.index('callback_selected')")
s=s.replace('Digitone-E04-PC-queued-pattern-retirement-controls.json','Digitone-E04-PC-queued-pattern-native-parent-rebind.json');s=s.replace('Field clear/rebind at publication is an explicit host fixture between stock queue publication and worker consumption; not naturally scheduled reset/rebind or timing evidence.', 'A temporary guest call stub invokes the complete native parent rebinder after queue publication; the selected existing backing is a PC fixture. This does not prove a normal application dispatcher permits the overlap.');s=s.replace('No new firmware or guard is installed.', 'Guest registers and status are saved/restored around the injected native call. Code is transient in PC RAM; firmware and existing overlay binaries are unchanged.')
exec(compile(s,'queued-native-parent-rebind','exec'))
