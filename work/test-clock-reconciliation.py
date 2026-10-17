import pathlib,sys,json,struct
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from types import SimpleNamespace
from emu import longrun
from emu.pit import Pits
from emu.dtim import Dtims
from emu.harness import Machine
checks=[]
def check(n,v):assert v,n;checks.append(n)
class UC:
 def reg_read(self,r):return 0x40001000
class Stepper:
 def __init__(self):self.clock=SimpleNamespace(cycles=0)
 def run(self,pc,n):self.clock.cycles+=n;return n
class Timer:
 now=10000
 def step(self,t,r):return 10
 def service(self,t):seen.append(('timer',t));stepper.clock.cycles+=7
class Source:
 def __init__(self,cost):self.cost=cost
 def step(self,t,r):return None
 def service(self,t):seen.append(('source',t));stepper.clock.cycles+=self.cost
m=SimpleNamespace(uc=UC(),halt_vec=None);stepper=Stepper();timer=Timer();seen=[]
pc,done,why=longrun.spin(m,0x40001000,1,pits=timer,fast=stepper,async_events=(Source(18),Source(3)))
check('all boundary interrupt costs counted',done==38 and stepper.clock.cycles==38)
check('later sources see earlier entry costs',seen==[('source',10010),('source',10028),('timer',10031)])
check('timer equals core with preserved epoch',timer.now==10038)
for j in range(20):longrun.spin(m,pc,1,pits=timer,fast=stepper,async_events=(Source(18),))
check('split calls never lose boundary charges',timer.now-10000==stepper.clock.cycles==738)
stepper.clock.cycles+=147
longrun.spin(m,pc,1,pits=timer,fast=stepper)
check('out-of-loop guest cycles preserve global epoch',timer.now-10000==stepper.clock.cycles)
# Combined PIT/DTIM sources must also see preceding source entry charges.
from emu.dtim import Timers
stepper=Stepper();seen=[]
a=Timer();b=Timer();combined=Timers(a,b)
_,done,_=longrun.spin(m,pc,1,pits=combined,fast=stepper)
check('combined timer services use current core time',seen==[('timer',10010),('timer',10017)] and done==24 and combined.now==10024)
# Non-cycle steppers retain original accounting.
legacy=SimpleNamespace(run=lambda pc,n:n);timer2=Timer();seen=[]
_,done,_=longrun.spin(m,pc,1,pits=timer2,fast=legacy)
check('legacy instruction accounting preserved',done==10 and timer2.now==10010)
m=Machine(ddr=128<<20);m.ensure(0xfc000000)
m.uc.mem_write(0xfc080000,struct.pack('>HH',0x53f,41249))
p=Pits(m);p.ips=250000000;p.fbus=125000000
check('PIT core-to-bus ratio is two',p.period(0)==5280000)
p.fbus=132000000
check('PIT rate change invalidates cache',p.period(0)==5000000)
m.uc.mem_write(0xfc070000,struct.pack('>HBBI',0x1b,0,0,99))
d=Dtims(m);d.ips=250000000;d.fbus=125000000
check('DTIM core-to-bus ratio is two',d.period(0)==200)
d.fbus=132000000
check('DTIM rate change invalidates cache',abs(d.period(0)-100*250/132)<1e-8)
p.ips=264000000;p.fbus=132000000
check('intended 264/132 MHz pair retains ratio',p.period(0)==5280000)
pathlib.Path('outputs/Digitone-clock-reconciliation-checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks,firmware_modified=False),indent=2));print(checks)

