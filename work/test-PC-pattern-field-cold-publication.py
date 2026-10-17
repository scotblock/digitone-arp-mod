from pathlib import Path
import json
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
for variable,file in [('startup_input_cfg','PC_ONLY-input-live-overlay'),('release_startup_cfg','PC_ONLY-release-reset-overlay'),('joined_UI_cfg','PC_ONLY-persistent-admission'),('native_defer_spec','PC_ONLY-resident-deferred-release-overlay'),('native_boot_cfg','PC_ONLY-cold-admission-overlay'),('native_admission_cfg','PC_ONLY-persistent-admission')]:globals()[variable]=json.loads(Path('work/os144/'+file+'.json').read_text())
s=Path('work/generated-deferred-startup-debug.py').read_text();line=next(x for x in s.splitlines() if x.startswith('for name,syx,imgfile,cardfile in '));s=s.replace(line,"for name,syx,imgfile,cardfile in [('E04_restored','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/PC_ONLY-atomic-storage-main.bin','work/os144/PC_ONLY-saved-mirror-valid_first.img')]:")
s=s.replace('work/resident-deferred-startup-','work/PC-pattern-field-cold-').replace('outputs/Digitone-E04-PC-resident-deferred-startup-startup.json','outputs/Digitone-E04-PC-pattern-field-cold-publication.json')
anchor="  install_strict(m,'cold')"
add='''  row['owner_field_writes']=[];row['owner_setter_entries']=[];row['large_allocation_requests']=[]
  def observe_owner(mm,stage):
   def ownerwrite(u,access,a,n,v,data):
    canonical=0x40000000+(a-0x40000000)%0x08000000
    if canonical<0x41a720f4 and canonical+n>0x41a720f0:row['owner_field_writes'].append({'stage':stage,'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(a),'bytes':n,'value':hex(v),'sp':hex(u.reg_read(UC_M68K_REG_A7)),'a6':hex(u.reg_read(UC_M68K_REG_A6))})
   for alias in range(8):mm.uc.hook_add(UC_HOOK_MEM_WRITE,ownerwrite,begin=0x41a720ef+alias*0x08000000,end=0x41a720f4+alias*0x08000000)
   def setter(u,pc,n,data):
    sp=u.reg_read(UC_M68K_REG_A7);args=struct.unpack('>IIII',u.mem_read(sp,16));entry={'stage':stage,'pc':hex(pc),'caller':hex(args[0]),'object':hex(args[1]),'arg2':hex(args[2]),'arg3':hex(args[3]),'sp':hex(sp),'a6':hex(u.reg_read(UC_M68K_REG_A6))}
    if 0x40000000<=args[1]<0x48000000:entry['prior_field']=hex(int.from_bytes(u.mem_read(args[1]+32,4),'big'));entry['vtable']=hex(int.from_bytes(u.mem_read(args[1],4),'big'))
    row['owner_setter_entries'].append(entry)
   for pc in [0x40152ffe,0x40153060,0x40153078]:mm.uc.hook_add(UC_HOOK_CODE,setter,begin=pc,end=pc)
   def largealloc(u,pc,n,data):
    sp=u.reg_read(UC_M68K_REG_A7);caller,size=struct.unpack('>II',u.mem_read(sp,8))
    if size>=0x100000:row['large_allocation_requests'].append({'stage':stage,'caller':hex(caller),'size':hex(size)})
   mm.uc.hook_add(UC_HOOK_CODE,largealloc,begin=0x400e96c0,end=0x400e96c0)
  observe_owner(m,'cold')
'''
assert anchor in s;s=s.replace(anchor,add+anchor);s=s.replace("   install_strict(mm,'intro')","   install_strict(mm,'intro')\n   observe_owner(mm,'intro')")
exec(compile(s,'pattern-owner-cold-trace','exec'))
