"""Initialization layout test: allocator return supplied, actual clear/link executed."""
exec(open('work/execute-context-init-reset.py').read().split('# Stock cold path')[0])
EXTENT=0x14c70;OFFSET=0x14100;SIZE=0xb70;MAGIC=0x534c4332
checks=[];cases=[]
def check(n,c):assert c,n;checks.append(n)

def prepared():
 m=init_setup();m.map(P,EXTENT)
 for j in range(EXTENT):m.write(P+j,1,0xa5)
 m.write(0x4199d590,4,0);return m

def prepare_cold(m,result):
 before=len(m.writes)
 # Hypothetical wrapper calls allocator before original initializer's first mutation.
 m.allocations.append(EXTENT)
 if result==0:
  return {'status':'terminal_failure','writes':len(m.writes)-before,'stock_initializer_called':False}
 m.run(0x400ec284,(result,0,EXTENT))
 m.write(result+OFFSET,4,MAGIC);m.write(result+OFFSET+4,4,2);m.write(result+OFFSET+8,4,SIZE)
 # +0c ready remains zero until the stock record linking completes.
 m.write(0x4199d590,4,result)
 m.run(0x400f0504,(158,))
 m.write(result+OFFSET+12,4,1)
 return {'status':'ready','writes':len(m.writes)-before,'stock_initializer_called':True}

m=prepared();begin=len(m.steps);r=prepare_cold(m,P)
check('cold wrapper requests explicit extended size once',m.allocations==[EXTENT])
check('prepared owner makes actual stock initializer skip allocation',0x400f0580 not in m.steps[begin:])
check('actual stock linker creates exactly64 original records',len(freechain(m)['slots'])==64 and all(m.read(P+j*0x504,4)==0 for j in range(64)))
check('header layout and final ready state survive actual stock linking',m.read(P+OFFSET,4)==MAGIC and m.read(P+OFFSET+8,4)==SIZE and m.read(P+OFFSET+12,4)==1)
check('actual extended clear initializes all metadata entries',all(m.read(P+OFFSET+j,1)==0 for j in range(32,SIZE)))
check('event and node heads have stock fixed pool values',m.read(0x4199fea0,4)==0x4199da94 and m.read(0x4199fe9c,4)==0x4199d594)
cases.append({'name':'proposed preallocation plus actual full memset/stock linking','stock_steps':len(m.steps)-begin,'status':r,'allocation_result_supplied':hex(P)})

for busy in [0,1]:
 # Retained table and pattern depth deliberately survive reentry.
 m.write(P+OFFSET+16,4,busy);m.write(P+OFFSET+0xb30,4,77);m.write(P+OFFSET+0xb34,4,0x80000080)
 table_before=bytes(m.mem[P+OFFSET+j] for j in range(SIZE));begin=len(m.steps);m.run(0x400f0504,(158,))
 check('existing-owner reentry keeps entire trailer byte-for-byte',bytes(m.mem[P+OFFSET+j] for j in range(SIZE))==table_before)
 check('existing-owner reentry does not allocate',m.allocations==[EXTENT])
 cases.append({'name':'actual existing-owner linking preserves proposed table','busy_depth':busy,'stock_steps':len(m.steps)-begin,'limit':'No proof stock pool reentry is safe with actual live owners'})

m=prepared();before=len(m.writes);begin=len(m.steps);r=prepare_cold(m,0)
check('null allocation takes no stock initializer or memory clear path',not r['stock_initializer_called'] and len(m.steps)==begin)
check('null result leaves owner and fixed-pool state unmodified',len(m.writes)==before and m.read(0x4199d590,4)==0)
cases.append({'name':'proposed null preflight rejection','status':r,'stock_steps':0,'allocation_result_supplied':0})

# A local failure endpoint fixture: mask then spin, no ordinary return.
HALT=0x50000400;fixture=bytes.fromhex('46fc270060fe')
def fetch(pc):return fixture[pc-HALT:pc-HALT+16] if HALT<=pc<HALT+len(fixture) else b[pc-base:pc-base+16]
halt_source=source.replace('b[pc-base:pc-base+16]','fetch(pc)').replace('range(80000)','range(16)')
exec('if True:\n'+halt_source);Machine.run=run;RANGES.append((HALT,HALT+len(fixture)))
wb=len(m.writes)
try:m.run(HALT)
except RuntimeError as exc:check('local failure endpoint cannot return normally',str(exc)=='instruction budget exceeded')
else:raise AssertionError('failure fixture returned')
# run's initial sentinel push is the only added write, on its controlled stack.
check('failure fixture only masks CPU and loops without pool stores',m.sr==0x2700 and all(a>=0x30000000 for a,n,v in m.writes[wb:]) and set(m.steps)=={HALT,HALT+4})
cases.append({'name':'synthetic local mask-and-spin failure endpoint','stock_steps':0,'fixture_steps':len(m.steps),'limits':'Not a graceful recovery path; does not establish DMA/peripheral shutdown or hardware recovery'})

result={'passed':len(checks),'checks':checks,'cases':cases,'request':hex(EXTENT),'firmware_modified':False,'limits':['Allocator itself not executed; P/zero results supplied','Preflight owner publication and final readiness store are proposed Python actions','Actual stock memset and linking executed','No init wrapper machine code or final firmware executable placement','Local halt demonstrates non-return only; real recovery unverified']}
pathlib.Path('outputs/Digitone-preallocated-initialization-layout-results.json').write_text(json.dumps(result,indent=2));print('PASS',len(checks),'initialization checks')
