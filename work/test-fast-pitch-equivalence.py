import pathlib,json,time
p=pathlib.Path('work/test-native-arp-overlays.py').read_text().split('\ndef run(mode):')[0]
p='\n'.join(x for x in p.splitlines() if not x.startswith('subprocess.run('));exec(p)
from emu.harness import call
blob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()
def installed(s):
 s.m.ensure(RAM);s.m.uc.mem_write(RAM,blob);s.m.install_isa_patches_scoped(blob[:1892],RAM)
s=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=installed);uc=s.m.uc;stack=0x47fdff00;s.m.ensure(stack)
began=time.monotonic();count=0
try:
 for root in range(128):
  for raw in range(-1,35):
   allowed=[n for n in range(128) if (n-root)%12 in rows[raw]]
   for note in range(128):
    word=0x80000000|root|((raw+1)<<7)
    preserved=[UC_M68K_REG_D2+i for i in range(6)]+[UC_M68K_REG_A2,UC_M68K_REG_A3]
    before={r:uc.reg_read(r) for r in preserved}
    got=call(s.m,layout['quantize']['address'],[note,word],stack_top=stack,limit=10000)
    want=min(allowed,key=lambda n:(abs(n-note),n))
    assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and got==want,(root,raw,note,got,want)
    assert before=={r:uc.reg_read(r) for r in preserved}
    count+=1
  if root%16==15:print('root',root,'comparisons',count,flush=True)
 malformed=0
 for note in [0,61,127,128,0xffffffff]:
  for word in [0,1,0x80008000,0x80001200,0xffffffff]:
   got=call(s.m,layout['quantize']['address'],[note,word],stack_top=stack,limit=10000)
   assert got==note,(note,word,got);malformed+=1
 result={'firmware_modified':False,'comparisons':count,'invalid_fallback_comparisons':malformed,'preserved_registers':True,'seconds':time.monotonic()-began,'roots':[0,127],'raw_scales':[-1,34],'all_MIDI_notes':True,'build':json.loads(pathlib.Path('work/fast-pitch-build.json').read_text())}
 pathlib.Path('outputs/Digitone-fast-pitch-equivalence.json').write_text(json.dumps(result,indent=2));print('PASS',result,flush=True)
finally:s.close()
