"""Read-only setup entry and terminal-continuation audit."""
exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json,hashlib
cond={'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs'}
def cfg(name,start,end,terminal_calls=()):
 todo=[start];seen={};calls=[];tails=[]
 while todo:
  a=todo.pop()
  if a in seen:continue
  assert start<=a<end,(name,hex(a))
  i=next(md.disasm(b[a-base:a-base+16],a,count=1));m=i.mnemonic.split('.')[0]
  assert i.id or i.bytes.hex() in [f'4a8{x:x}' for x in range(8,16)],(hex(a),i.mnemonic)
  seen[a]={'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str}
  if m=='rts':continue
  if m=='jmp':tails.append({'site':hex(a),'instruction':i.mnemonic+' '+i.op_str});continue
  if m in ('jsr','bsr'):
   calls.append({'site':hex(a),'instruction':i.mnemonic+' '+i.op_str})
   if any(f'${target:x}' in i.op_str for target in terminal_calls):continue
  if m in cond|{'bra'}:
   target=int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16)
   if start<=target<end:todo.append(target)
   else:tails.append({'site':hex(a),'target':hex(target),'instruction':i.mnemonic+' '+i.op_str})
   if m!='bra':todo.append(a+i.size)
  else:todo.append(a+i.size)
 return {'name':name,'instructions':{hex(a):v for a,v in sorted(seen.items())},'calls':calls,'external_transfers':tails}
graphs=[cfg('pool_initializer',0x400f0504,0x400f05d6),cfg('common_setup_wrapper',0x4009bcb8,0x4009bcc6),cfg('audio_setup',0x4009bcc6,0x4009bd6a),cfg('initial_setup_entry',0x4009c7f0,0x4009c802),cfg('test_exit_setup_entry',0x4009c802,0x4009c80c),cfg('test_queue_setup',0x4009bde8,0x4009be8e),cfg('node_allocator_failstop',0x400f04c0,0x400f04f0),cfg('assertion_handler',0x40126624,0x40126690,(0x400f09e2,)),cfg('assertion_terminal',0x400f09e2,0x400f09e4)]
checks=[]
def check(name,c):assert c,name;checks.append(name)
discovery=json.load(open('work/setup-entry-discovery.json'))
graphs.append(cfg('setup_tail_callback',0x400ae45e,0x400ae464))
graphs.append(cfg('adjacent_function_boundary',0x400ae3e4,0x400ae458))
check('raw callback reference is operand false positive', '0x400ae3f6' not in graphs[-1]['instructions'] and graphs[-1]['instructions']['0x400ae3f2']['bytes']=='4eb9400d6966')
check('callback target is explicitly constructed',b[0x400aeae4-base:0x400aeaea-base].hex()=='203c400ae45e')
check('callback stored in local record',b[0x400aeaec-base:0x400aeaf0-base].hex()=='2d40fffc')
check('test exit command string matches',b[0x401bb024-base:].split(b'\0',1)[0]==b'#EXIT_TEST_MODE')
check('sole recovered direct initializer call',discovery['refs']['0x400f0504']==['0x4009bcbc'])
check('two recovered wrapper calls',discovery['refs']['0x4009bcb8']==['0x4009bcec','0x4009bdec'])
check('two direct setup entry branches',discovery['refs']['0x4009bcc6']==['0x4009c7fe','0x4009c808'])
check('no recovered outside direct transfer into initializer interior',not discovery['interior_candidates'])
check('earliest initializer store precedes allocation check',graphs[0]['instructions']['0x400f051a']['instruction']=='move.l d0, (a0)')
check('queue head clear precedes owner check',graphs[0]['instructions']['0x400f0534']['instruction']=='clr.l $4199fe94.l')
check('audio setup continues without testing pool setup return',graphs[2]['instructions']['0x4009bcf0']['instruction']=='jsr $400979f0.l')
check('test setup continues without testing pool setup return',graphs[5]['instructions']['0x4009bdf0']['instruction']=='lea.l $400f0626.l, a3')
check('audio setup has no explicit SR protection before initializer',not any(re.search(r'\bsr\b',v['instruction']) for a,v in graphs[2]['instructions'].items() if int(a,16)<=0x4009bcec))
check('terminal endpoint is exact branch to self',b[0x400f04d0-base:0x400f04d2-base].hex()=='60fe')
check('stock exhaustion masks before terminal spin',graphs[6]['instructions']['0x400f04c2']['instruction']=='move.w #$2700, sr')
check('assertion terminal does not itself mask interrupts',len(graphs[8]['instructions'])==1 and b[0x400f09e2-base:0x400f09e4-base].hex()=='60fe')
# Execute existing allocator's exhausted-head branch for a bounded 12 steps.
# This is the stock failure precedent, not an injected setup hook.
exec(open('work/execute-payload-lifecycle.py').read().split('checks=[];scenarios=[];total_steps=0')[0])
RANGES.append((0x400f04c0,0x400f04f0))
src=' def run'+pathlib.Path('work/execute-payload-lifecycle.py').read_text().split(' def run',1)[1].split('\nP=',1)[0]
src=src.replace('range(20000)','range(12)');exec('if True:\n'+src);Machine.run=run
m=fresh();m.sr=0x2000;startwrites=len(m.writes)
try:m.run(0x400f04c0);raise AssertionError('terminal returned')
except RuntimeError as exc:check('stock exhaustion remains in loop for bounded execution','instruction budget exceeded' in str(exc))
check('stock terminal retains mask seven',m.sr&0xff00==0x2700)
check('no pool writes on exhausted allocator path',all(0x30000000<=a<0x30003000 for a,n,v in m.writes[startwrites:]))
check('repeated terminal address reached',m.steps.count(0x400f04d0)>=3)
syx=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx');hashes=[hashlib.sha256(syx.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
check('firmware hashes unchanged',hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'])
result={'firmware_modified':False,'checks':checks,'local_graphs':graphs,'direct_entry_discovery':discovery,'stock_terminal_execution':{'steps':[hex(x) for x in m.steps],'sr':hex(m.sr),'scope':'Existing node allocator empty-head path, not modified pool setup.'},'terminal_assessment':'400f04d0 is a verified local nonreturning endpoint; requires interrupt mask precondition. Not a verified graceful hardware shutdown or recovery path.','guard_points':{'common':'400f0504 entry, before 400f051a first pool write','wrapper':'4009bcb8 entry, covers recovered direct wrapper callers only','outer_entries':['4009c7f0 before state stores','4009c802 before state clear','4009bde8 before initialization']},'remaining':['No graceful allocation-failure propagation in recovered callers.','No verified full shutdown/quiescence across runtime reentry.','No complete computed caller inventory.','Masking interrupts does not prove DMA/peripheral cessation or exception immunity.'],'sha256':hashes}
pathlib.Path('outputs/Digitone-setup-failure-and-entry-audit-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'checks':len(checks),'graphs':len(graphs),'instructions':sum(len(g['instructions']) for g in graphs),'terminal_sr':hex(m.sr),'hashes_unchanged':True}))

