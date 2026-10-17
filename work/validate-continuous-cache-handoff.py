"""Check observed control writes against documented coherence prerequisites."""
import pathlib,json,hashlib
stock=json.loads(pathlib.Path('outputs/Digitone-stock-loader-cache-continuity.json').read_text())
run=json.loads(pathlib.Path('outputs/Digitone-continuous-loader-copier.json').read_text())
events=run['events'];writes=run['cache_writes']
checks={}
def check(name,value):checks[name]=bool(value);assert value,name
check('full stock loader reached original MAIN entry',stock['reached']=='0x400004e8' and stock['main_os_matches'])
check('extended ephemeral image reached original MAIN entry',run['passed'] and run['loader']['main_matches'])
check('original firmware hash unchanged',stock['before']==stock['after']==run['before']==run['after'])
check('neither emulated flash programmed nor erased',not stock['flash_writes'] and not run['loader']['flash_writes'])
check('stock and extended loader produce same inherited controls',stock['controls']==run['loader']['controls'])
check('source intact on copier entry and return',all(e['source_intact'] for e in events[:2]))
check('all 581 longwords copied by native instructions',run['copy_stores']==581)
check('destination preserved across stock clear and cache setup',events[1]['copied_exact'] and events[2]['copied_exact'])
check('data cache disabled throughout copy boundaries',all(not int(e['controls']['0x2'],16)&0x80000000 for e in events[:2]))
check('store buffer disabled throughout copy boundaries',all(not int(e['controls']['0x2'],16)&0x20000000 for e in events[:2]))
check('ACR0 and ACR1 disabled at copy boundaries',all(e['controls']['0x4']=='0x0' and e['controls']['0x5']=='0x0' for e in events[:2]))
check('stock CACR write requests instruction and data invalidation after copy',any(w['pc']=='0x4000055a' and int(w['value'],16)&0x01000100==0x01000100 for w in writes))
check('copyback DDR mapping established after copy',writes[-1]=={'pc':'0x40000564','selector':'0x4','value':'0x4007e020'})
check('loader synchronization NOP actually executed',len(run['synchronizing_nop'])==1 and run['synchronizing_nop'][0]['pc']=='0x80000632')
check('stock post-copy clear observed on extension source',run['source_writers'].get('0x400004d2',0)>0)
# Trace-derived value model with deliberately stale cache contents. Not a
# timing model: completion rules come from MCF54418RM 6.3.1 and 6.4.4.2.2.
table=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()[1904:2324]
def value_model(dec,desb,invalidate,drain,push=False):
 memory=bytearray(b'\xa5'*len(table));cache=bytearray(b'\x5a'*len(table));pending=[];dirty=False
 for i,v in enumerate(table):
  if dec:cache[i]=v;dirty=True
  elif desb:pending.append((i,v))
  else:memory[i]=v
 if drain:
  for i,v in pending:memory[i]=v
 if push and dirty:memory[:]=cache
 if invalidate:cache=None
 return bytes(memory if cache is None else cache)==table
cases=[]
for label,dec,desb,inv,drain,push,expected in [
 ('observed disabled-cache disabled-buffer copy plus stock invalidate',False,False,True,False,False,True),
 ('counterexample: old cache retained',False,False,False,False,False,False),
 ('counterexample: dirty copyback discarded',True,False,True,False,False,False),
 ('counterexample: delayed writes without synchronization',False,True,True,False,False,False),
 ('buffered writes drained by documented supervisor synchronization',False,True,True,True,False,True)]:
 actual=value_model(dec,desb,inv,drain,push);assert actual==expected
 cases.append({'case':label,'visible':actual,'expected':expected})
out={'passed':True,'checks':checks,'trace_derived_coherence_model':cases,'physical_cache_coherence_verified':False,'scope':'One modeled normal boot route with Digitone UI-card and strap responses. Serial reset hardware is represented by loaded SRAM, peripheral timings are modeled, and Unicorn has no physical cache lines/store-buffer/DDR visibility model.','self_clearing_bits':'Control maps retain last MOVEC values, including invalidate request bits; these are writes, not measured persistent hardware states.','manual':'https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf','sections':['6.3.1','6.3.2','6.4.4.2.2','6.4.6'],'next_gap':'Continuous loader-derived startup through initializer and playback; independent device/cache evidence remains required for physical certification.'}
pathlib.Path('outputs/Digitone-inherited-cache-checks.json').write_text(json.dumps(out,indent=2));print('passed',len(checks),'trace checks and',len(cases),'value-model controls')
