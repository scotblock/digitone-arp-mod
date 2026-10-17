from pathlib import Path
import sys,json,time,traceback,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom,longrun
from dt2.elz import depack_section
syx=Path('work/os144/E08-PC-path-candidate.syx');main=Path('work/os144/E08-PC-layout-main.bin').read_bytes()
original=longrun.spin
def fast(*a,**k):k['fast']=True;return original(*a,**k)
longrun.spin=fast
out={'PC_only':True,'candidate_sha256':hashlib.sha256(syx.read_bytes()).hexdigest(),'limits':['Flash/PLL/DDR hardware is modeled. Physical cache coherence is not emulated.','This executes the stock loader from its bootstrap, not the MIDI update receiver.']};start=time.monotonic()
try:
 r=bootrom.boot(str(syx),depack_section(bootrom.container_section(str(syx),2)),main,limit=300000000,chunk=10000000,on_machine=lambda m,f,d:m.install_isa_patches_scoped(main,0x40000400),trace=lambda m,n,pc:print('loader',n,hex(pc),flush=True),ui_card=8,straps={0xec09401b:8},groups=7)
 out.update(reached=hex(r.reached) if r.reached else None,main_matches=r.main_os_matches,instructions=r.instructions,flash_writes=r.flash_writes,boot_flags=r.boot_flags,cache_controls={hex(k):hex(v) for k,v in r.m.ctlregs.items()})
 assert r.reached==0x400004e8 and r.main_os_matches and not r.flash_writes
 out['handoff']=bootrom.save_handoff(r,'work/os144/E08-PC-loader-handoff.bin');out['passed']=True
except Exception:out.update(passed=False,failure=traceback.format_exc());print(out['failure'],flush=True)
out['seconds']=time.monotonic()-start;Path('outputs/Digitone-E08-packed-loader.json').write_text(json.dumps(out,indent=2));print('passed',out['passed'],flush=True)
if not out['passed']:raise SystemExit(1)
