"""Explicit SPI/UART completion fixtures; stock instructions, no hardware I/O."""
import pathlib,json,hashlib,copy
# Recover the unchanged original container into memory for realistic SPI
# descriptor/header reads. Do not persist a container or firmware artifact.
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx').read_bytes();pos=0;wire=bytearray()
while pos<len(syx):
 end=syx.index(247,pos+1);packet=syx[pos+1:end];pos=end+1
 if packet[5]!=126:continue
 for k in range(9,125,8):
  tag=packet[k];wire.extend(v|(((tag>>(6-j))&1)<<7) for j,v in enumerate(packet[k+1:min(k+8,125)]))
stock_container=bytes(wire[8:8+int.from_bytes(wire[:4],'big')])
t={};exec(pathlib.Path('work/trace-intervening-startup.py').read_text().split('\nm,owner=fresh()')[0],t)
s=t['s'];base=t['base'];b=t['b'];checks=[];cases=[]
def check(name,ok):assert ok,name;checks.append(name)
class FixtureWait(Exception):pass
s['FixtureWait']=FixtureWait
oldobserve=s['observe_placed']
def observe(m,pc):
 if pc==0x400ec45c and getattr(m,'timer_complete',False):
  registers=m.reg.copy();status=m.sr;stops=m.startup_stops[:];m.startup_stops=[0x400ec3ce]
  try:m.run(0x400ec3a0)
  except t['Stop']:pass
  else:raise AssertionError('timer ISR return boundary not reached')
  m.reg=registers;m.sr=status;m.startup_stops=stops;m.timer_events+=1
 if pc==0x400ece52:
  sp=m.reg['a7'];m.spi_address=m.read(sp+4,4)&0xffffff;m.spi_jobs.append((m.read(sp+4,4),m.read(sp+8,4),m.read(sp+12,4)));m.spi_cursor=-4;m.spi_polls=0;m.spi_commands=[]
 oldobserve(m,pc)
s['observe_placed']=observe
src=t['src'].replace("   elif m=='nop':pass","   elif m in ('nop','tpf'):pass\n   elif m=='shi':self.put(ops[0],1,255 if not self.sr&5 else 0)")
exec('if True:\n'+src,s)
class ResponseMachine(t['StartupMachine']):
 def configure(self,spi='ready',uart='echo'):
  self.spi_mode=spi;self.uart_mode=uart;self.spi_jobs=[];self.spi_cursor=-4;self.spi_polls=0;self.spi_commands=[];self.spi_data=bytes(range(17));self.spi_readback=[];self.stock_flash=False;self.spi_address=0
  self.uart_tx=[];self.rx=[];self.query=[];self.command=[];self.status_polls=0;self.timer=0;self.uart_events=[];self.delay_polls=0
  self.timer_complete=False;self.timer_events=0
 def read(self,a,z):
  if 0x4b000000<=a<0x4c000000:return self.hardware.get(a,0)
  if a==0xfc05c02c:
   self.spi_polls+=1
   ready=self.spi_mode!='no_receive' and not(self.spi_mode=='short_receive' and self.spi_cursor>=3)
   if self.spi_mode=='delayed' and self.delay_polls<3:self.delay_polls+=1;ready=False
   if not ready and self.spi_polls>40:raise FixtureWait('SPI receive unavailable; PC poll bound')
   if self.spi_mode=='no_completion' and self.spi_polls>80:raise FixtureWait('SPI completion absent; PC poll bound')
   return (0x10 if ready else 0)|(0 if self.spi_mode=='no_completion' else 0x10000000)
  if a==0xfc05c038:
   p=self.spi_cursor;self.spi_cursor+=1
   at=self.spi_address+p-0x80000
   v=0 if p<0 else (stock_container[at] if self.stock_flash and 0<=at<len(stock_container) else self.spi_data[p%len(self.spi_data)]);self.spi_readback.append(v);return v
  if a==0xec070004:
   self.status_polls+=1
   if self.uart_mode=='no_transmit' and self.status_polls>40:raise FixtureWait('UART transmit unavailable; PC poll bound')
   if self.uart_mode in ['no_receive','query_short'] and not self.rx and self.status_polls>60:raise FixtureWait('UART receive unavailable; PC poll bound')
   tx=self.uart_mode!='no_transmit'
   if self.uart_mode=='delayed' and self.delay_polls<3:self.delay_polls+=1;tx=False
   return (4 if tx else 0)|(1 if self.rx else 0)
  if a==0xec07000c:
   assert self.rx,'read without queued UART data';v=self.rx.pop(0);self.uart_events.append(('rx',v));return v
  if a==0xfc07000c:
   value=self.timer;self.timer=(self.timer+0x4ead9a00)&0xffffffff;return value
  return super().read(a,z)
 def write(self,a,z,v):
  if 0x4b000000<=a<0x4c000000:self.hardware[a]=v;self.mmio_writes.append((hex(a),z,v));return
  if a==0xfc05c034:self.spi_commands.append(v&255)
  if a==0xec07000c:
   v&=255;self.uart_tx.append(v);self.uart_events.append(('tx',v));self.query.append(v);self.command.append(v)
   if self.uart_mode.startswith('query') or self.uart_mode=='current_version':
    if self.query[-4:]==[0x60,2,0x70,0]:
     response=[0x70,8,5,0,2]
     if self.uart_mode=='query_bad_identity':response[0]=0
     if self.uart_mode=='query_bad_platform':response[4]=0
     if self.uart_mode=='query_short':response=response[:3]
     self.rx.extend(response);self.command=[]
   elif len(self.command)==5:
    response=self.command.copy();self.command=[]
    if self.uart_mode=='mismatch':response[-1]^=1
    if self.uart_mode in ['echo','delayed','mismatch']:self.rx.extend(response)
    if self.uart_mode=='short_timeout':self.rx.extend(response[:3])
  return super().write(a,z,v)

def new():
 m,owner=t['fresh']();m.__class__=ResponseMachine;m.configure();m.run=s['run'].__get__(m,ResponseMachine);s['active']=m;return m,owner
for mode in ['ready','delayed','no_receive','short_receive','no_completion']:
 m,owner=new();m.configure(spi=mode);snapshot=t['protected'](m,owner);m.map(0x29000000,64);m.reg['a7']=0x30002000;m.sr=0x2700
 for j in range(64):m.write(0x29000000+j,1,0xa5)
 wait=None;before=len(m.steps)
 try:m.run(0x400ece52,(0x123456,17,0x29000010))
 except FixtureWait as exc:wait=str(exc)
 check(mode+': SPI outcome',bool(wait)==(mode in ['no_receive','short_receive','no_completion']))
 check(mode+': SPI preserves proposed allocation',t['protected'](m,owner)==snapshot)
 check(mode+': SPI commands carry opcode and 24-bit address',m.spi_commands[:4]==[3,0x12,0x34,0x56])
 check(mode+': SPI guards preserved',m.read(0x2900000f,1)==165 and m.read(0x29000021,1)==165)
 if mode in ['ready','delayed']:check(mode+': actual SPI reader copies exact response',bytes(m.read(0x29000010+j,1) for j in range(17))==bytes(range(17)))
 cases.append({'kind':'SPI reader','mode':mode,'wait':wait,'instructions':len(m.steps)-before,'polls':m.spi_polls,'received_words':len(m.spi_readback),'commands':m.spi_commands[:4]})

for mode in ['echo','delayed','mismatch','timeout','short_timeout','no_transmit']:
 m,owner=new();m.configure(uart=mode);snapshot=t['protected'](m,owner);m.reg['a7']=0x30002000;m.sr=0x251b;before=len(m.steps);wait=None;result=None
 try:result=m.run(0x4009f3b4,(3,0x12345678))
 except FixtureWait as exc:wait=str(exc)
 expected={'echo':0,'delayed':0,'mismatch':0xffffffff,'timeout':0xfffffffe,'short_timeout':0xfffffffe}.get(mode)
 check(mode+': UART transaction outcome',(bool(wait) and mode=='no_transmit') or (wait is None and result==expected))
 check(mode+': UART preserves owner/allocation',t['protected'](m,owner)==snapshot)
 if mode!='no_transmit':check(mode+': UART sends exact five-byte request',m.uart_tx==[3,0x12,0x34,0x56,0x78])
 cases.append({'kind':'UART checked transaction','mode':mode,'result':None if result is None else hex(result),'wait':wait,'instructions':len(m.steps)-before,'events':m.uart_events})

for mode in ['current_version','query_bad_identity','query_bad_platform','query_short','no_transmit']:
 m,owner=new();m.configure(uart=mode);snapshot=t['protected'](m,owner);m.reg['a7']=0x30002000;m.sr=0x251b;before=len(m.steps);wait=None;result=None
 try:result=m.run(0x4009f5c0)
 except FixtureWait as exc:wait=str(exc)
 expected={'current_version':0xfffffffd,'query_bad_identity':0xffffffff,'query_bad_platform':0xfffffffe}.get(mode)
 check(mode+': UART startup query outcome',(bool(wait) and mode in ['query_short','no_transmit']) or (wait is None and result==expected))
 check(mode+': UART startup preserves owner/allocation',t['protected'](m,owner)==snapshot)
 if wait is None:check(mode+': UART startup restores status',m.sr&0xff00==0x2500)
 cases.append({'kind':'UART startup version query','mode':mode,'result':None if result is None else hex(result),'wait':wait,'instructions':len(m.steps)-before,'events':m.uart_events})

# Resume full second-thread setup with explicit FIFO-ready/completion signals.
# Reads use the original container where available and synthetic bytes outside
# that range; this is a conditioned PC run, not observed external flash contents.
m,owner=new();m.stock_flash=True;snapshot=t['protected'](m,owner);m.map(0,4);m.map(0x80000000,0x10000)
t['runstop'](m,0x4012b344,[0x4012b3be]);m.reg['a7']=0x30002000;m.sr=0x2000
t['runstop'](m,0x4008c4f6,[0x4008c524]);m.reg['a7']=0x30002000
# Supplied scheduler boundary: select the actual second-thread object created
# by stock code. Physical trap/RTE machinery remains unexecuted.
m.write(0x429a39a8,4,0x41327598)
m.sr=0x2000;m.startup_stops=[0x4008c7d4,0x8000f100];before=len(m.steps);error=None;complete=False
try:m.run(0x4008c634)
except t['Stop']:complete=True
except (FixtureWait,AssertionError,RuntimeError,KeyError,NotImplementedError) as exc:error=f'{type(exc).__name__}: {exc}'
check('resumed hardware setup preserves owner/allocation',t['protected'](m,owner)==snapshot)
cases.append({'kind':'second-thread setup with SPI completion','complete':complete,'boundary':hex(m.stop_pc) if complete else None,'error':error,'last_pc':hex(m.steps[-1]),'instructions':len(m.steps)-before,'SPI_jobs':[(hex(a),z,hex(d)) for a,z,d in m.spi_jobs[:20]],'SPI_job_count':len(m.spi_jobs),'flash_contents':'unchanged original container at 80000; synthetic outside that range'})

# A completion before the blocking wait is a separate supplied event ordering.
# Execute the stock timer ISR body to its RTE boundary rather than directly
# setting its semaphore. Interrupt entry/RTE themselves remain unmodeled.
m,owner=new();m.stock_flash=True;m.timer_complete=True;snapshot=t['protected'](m,owner);m.map(0,4);m.map(0x80000000,0x10000)
t['runstop'](m,0x4012b344,[0x4012b3be]);m.reg['a7']=0x30002000;m.sr=0x2000;t['runstop'](m,0x4008c4f6,[0x4008c524]);m.reg['a7']=0x30002000;m.write(0x429a39a8,4,0x41327598);m.startup_stops=[0x4008c7d4,0x8000f100];before=len(m.steps);error=None;complete=False
try:m.run(0x4008c634)
except t['Stop']:complete=True
except (FixtureWait,AssertionError,RuntimeError,KeyError,NotImplementedError) as exc:error=f'{type(exc).__name__}: {exc}'
check('SPI plus timer event preserves owner/allocation',t['protected'](m,owner)==snapshot)
check('timer event executes stock signal ISR',m.timer_events>0)
cases.append({'kind':'second-thread SPI and timer completion','complete':complete,'boundary':hex(m.stop_pc) if complete else None,'error':error,'last_pc':hex(m.steps[-1]),'instructions':len(m.steps)-before,'timer_events':m.timer_events})

# Continue the same second-thread state without adding a synthetic call frame
# at each stop. The only supplied context boundary is initial thread selection.
frame="  for v in reversed(args):self.put('-(a7)',4,v)\n  self.put('-(a7)',4,0xffffffff);pc=entry"
assert frame in src
advance_src=src.replace('def run(self,entry,args=()):','def advance(self,entry,args=()):').replace(frame,'  pc=entry')
exec('if True:\n'+advance_src,s);m.advance=s['advance'].__get__(m,ResponseMachine)
m.startup_stops=[0x4008c7f4];before=len(m.steps)
try:m.advance(0x4008c7d4)
except t['Stop']:pass
else:raise AssertionError('table continuation boundary not reached')
callback_entries=[int.from_bytes(b[0x40241ab8-base+4*j:0x40241abc-base+4*j],'big') for j in range(119)]
check('continuous second-thread state executes all constructors in order',[pc for pc in m.steps[before:] if pc in callback_entries]==callback_entries)
check('continuous constructor path preserves allocation',t['protected'](m,owner)==snapshot)
cases.append({'kind':'SPI timer setup followed by real constructor table','instructions':len(m.steps)-before,'actual_allocator_entries':m.steps[before:].count(0x400dab8c),'callbacks':119})
constructor_state=m;constructor_owner=owner
# Bound the asset-decompression continuation separately from the constructor run.
exec('if True:\n'+advance_src.replace('range(2000000)','range(50000)'),s)
for mode in ['current_version','query_bad_identity','query_bad_platform']:
 m=copy.deepcopy(constructor_state);m.configure(uart=mode);m.stock_flash=True;m.timer_complete=True;s['active']=m;m.run=s['run'].__get__(m,ResponseMachine);m.advance=s['advance'].__get__(m,ResponseMachine);m.startup_stops=[0x400f0504];before=len(m.steps);error=None;complete=False;before_owner=t['protected'](m,constructor_owner)
 try:m.advance(0x4008c7f4)
 except t['Stop']:complete=True
 except (FixtureWait,AssertionError,RuntimeError,KeyError,NotImplementedError) as exc:error=f'{type(exc).__name__}: {exc}'
 check(mode+': resumed post-table path preserves allocation',t['protected'](m,constructor_owner)==before_owner)
 check(mode+': post-table startup version query returns',0x4009f75e in m.steps[before:])
 cases.append({'kind':'post-table startup with UART responses','mode':mode,'complete':complete,'error':error,'last_pc':hex(m.steps[-1]),'instructions':len(m.steps)-before,'query_return_executed':0x4009f75e in m.steps[before:],'tx_count':len(m.uart_tx),'first_tx':m.uart_tx[:12]})

check('original decoded firmware unchanged',hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
check('original SysEx unchanged',hashlib.sha256(syx).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
result={'check_count':len(checks),'checks':checks,'cases':cases,'firmware_modified':False,'limits':['SPI data and UART responses are explicit synthetic PC fixtures, not observed device responses.','FixtureWait is a PC bound, not a firmware timeout.','UART checked transaction executes the recovered timer-based timeout; short version-query receive has no equivalent local timeout.','Physical interrupts, trap/RTE scheduling and cache coherence not modeled.','Full application/initializer bridge remains conditioned on resumed path results.']}
pathlib.Path('outputs/Digitone-startup-completion-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'checks':len(checks),'cases':[dict((k,v) for k,v in x.items() if k not in ['events','SPI_jobs']) for x in cases]},indent=2))
