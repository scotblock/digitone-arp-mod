from pathlib import Path
import json
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
cfg=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text())
s=Path('work/test-E04-native-startup-delay.py').read_text()
s=s.replace("payload=Path('work/os144/fallback-final-payload.bin').read_bytes()","payload=Path('work/os144/E07-PC-payload.bin').read_bytes()")
old="for name,syx,imgfile in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:"
cases=[]
for name in ['stock_default','stock_restored','E07_default','E07_restored','E07_disabled']:
 stock=name.startswith('stock');card='work/os144-emulator-E02-engine/plusdrive.img' if name.endswith('default') else 'work/os144/PC_ONLY-saved-mirror-valid_first.img'
 cases.append((name,'outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx' if stock else 'work/os144/E07-PC-candidate.syx','work/os144/section-3.bin' if stock else 'work/os144/E07-PC-main.bin',card))
assert old in s;s=s.replace(old,'for name,syx,imgfile,cardfile in '+repr(cases)+':')
s=s.replace("root=Path('work/native-delay-'+name)","source=Path(cardfile)\n  root=Path('work/E07-startup-'+name)")
s=s.replace('Digitone-E04-native-startup-delay-checks.json','Digitone-E07-PC-startup-comparison.json')
s=s.replace("  image=Path(imgfile).read_bytes();", "  from dt2.container import sections\n  cc,ee=sections(Path(syx));_,off,n,_=next(e for e in ee if e[0]==7);blob=cc[off:off+n]\n  assert blob==Path('work/os144/section-7-stored.bin').read_bytes()\n  Path(paths.sections,'section_7_BLOB.bin').write_bytes(blob)\n  row['DSP_section_from_candidate_verified']=True\n  image=Path(imgfile).read_bytes();")
s=s.replace("   held['ev']=ev", "   held['ev']=ev\n   row['DSP_model']=type(ev['dsplink']).__name__;assert row['DSP_model']=='DspCpu'")
s=s.replace("if name=='E04'", "if name.startswith('E07')")
s=s.replace("m.ensure(0x47be0000);m.install_isa_patches_scoped(payload[:1784],0x47be0000);m.install_isa_patches_scoped(payload[2212:],0x47be08a4)","m.ensure(0x47be0000)")
s=s.replace("mm.install_isa_patches_scoped(payload[:1784],0x47be0000);mm.install_isa_patches_scoped(payload[2212:],0x47be08a4)","install_strict(mm,'intro')")
anchor='  done=0;timer=Dtims(m,channels=(1,),clear_stale=False)'
add='''  row['strict_failures']=[];row['strict_executed']={};row['phase_events']=[];row['copied_components_verified']=False
  def install_strict(mm,stage):
   if not name.startswith('E07'):return
   def strict(u,pc,n,d):
    ins=cfisa.decode(lambda off:int.from_bytes(u.mem_read(pc+off,2),'big'),pc)
    bad=move_restriction(int.from_bytes(u.mem_read(pc,2),'big'))
    if bad or ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) or (ins.flags&cfisa.PRIV and not u.reg_read(UC_M68K_REG_SR)&0x2000):
     row['strict_failures'].append({'pc':hex(pc),'op':ins.op,'stage':stage,'reason':bad});raise AssertionError(row['strict_failures'][-1])
    row['strict_executed'][stage]=row['strict_executed'].get(stage,0)+1
   for r in cfg['regions']:
    data=image[r['base']-0x40000400:r['base']-0x40000400+r['bytes']] if r['base']<0x47be0000 else payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']]
    mm.install_isa_patches_scoped(data,r['base']);mm.uc.hook_add(UC_HOOK_CODE,strict,begin=r['base'],end=r['base']+r['bytes']-1)
  install_strict(m,'cold')
  def copied(u,pc,n,d):
   for r in cfg['components']:
    off=r['base']-0x47be0000;assert bytes(u.mem_read(r['base'],r['bytes']))==payload[off:off+r['bytes']],r['name']
   assert bytes(u.mem_read(0x47be2860,400))==bytes(400) and int.from_bytes(u.mem_read(0x47be2840,4),'big')==0
   row['copied_components_verified']=True
  def phase(u,pc,n,d):row['phase_events'].append({'pc':hex(pc),'phase':hex(int.from_bytes(u.mem_read(0x47be2840,4),'big'))})
  if name.startswith('E07'):
   # Dirty only the destination before the native copier. No executable helper is host-loaded.
   m.uc.mem_write(0x47be3800,bytes([0xa5])*0x1004);m.uc.mem_write(0x47be2860,bytes([0xa5])*400)
   m.uc.hook_add(UC_HOOK_CODE,copied,begin=0x4029c518,end=0x4029c518)
   for pc0 in [0x4000053e,0x4009d0d8,0x4008d3fa]:m.uc.hook_add(UC_HOOK_CODE,phase,begin=pc0,end=pc0)
   if name=='E07_disabled':
    def corrupt(u,pc,n,d):u.mem_write(0x47be1000,struct.pack('>I',0xffffffff))
    m.uc.hook_add(UC_HOOK_CODE,corrupt,begin=0x47be3400,end=0x47be3400)
'''
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s.replace("assert bytes(m.uc.mem_read(0x47be0000,len(payload)))==payload", "assert row['copied_components_verified'] and not row['strict_failures']\n  if name.startswith('E07'):row['phase_after_cold']=hex(int.from_bytes(m.uc.mem_read(0x47be2840,4),'big'));assert row['phase_after_cold']=='0x4c495645';row['READY']=int.from_bytes(m.uc.mem_read(0x47be1010,4),'big');assert row['READY']==(0 if name=='E07_disabled' else 1)")
s=s.replace('paths.cold,budget=', 'paths.cold,out=paths.gui_raw,budget=')
s=s.replace("  row['passed']=True", "  row['ui_snapshot']=paths.gui_raw\n  row['packaged_helpers_host_loaded']=False\n  assert not row['strict_failures']\n  row['passed']=True")
s=s.replace("  row['seconds']=", "  row['seconds']=")
s += "\nout['passed']=all(r.get('passed') for r in out['cases']);dest.write_text(json.dumps(out,indent=2));\nif not out['passed']:raise SystemExit(1)\n"
Path('work/generated-E07-startup.py').write_text(s)
s=s.replace("  save(m,paths.cold", "  if name.startswith('E07'):\n   row['MIDI_header_after_cold']=hex(int.from_bytes(m.uc.mem_read(cfg['MIDI_state'],4),'big'));assert row['MIDI_header_after_cold']=='0x53414d31'\n  save(m,paths.cold")
s=s.replace('for name,syx,imgfile,cardfile in ', "if '--resume' in sys.argv:out['cases']=[r for r in json.loads(dest.read_text())['cases'] if r.get('passed') and r['image'].startswith('stock')]\nfor name,syx,imgfile,cardfile in ")
s=s.replace(" row={'image':name", " if any(r['image']==name for r in out['cases']):continue\n row={'image':name")
exec(compile(s,'E07-packaged-startup','exec'))
