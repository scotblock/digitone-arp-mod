from pathlib import Path
import sys,json,copy
sys.path.insert(0,'work')
from digitone_reinitialization_policy import *
checks=[]
def check(name,ok):assert ok,name;checks.append(name)
def rejected(f):
 try:f()
 except ProtectionViolation:return True
 return False
for completion in [('normal',True,True,True),('feature_unavailable',True,False,True),('stock_failed',False,False,True),('diagnostic_state',True,True,False)]:
 name,stock,context,normal=completion;p=ReinitializationPolicy();check(name+': producers closed before boot',not p.producer().allowed);token=p.begin_boot();p.initializer_entry(token);check(name+': no nested entry',rejected(lambda:p.initializer_entry(token)));p.finish_boot(stock_complete=stock,context_complete=context,mode_is_normal=normal)
 check(name+': no second setup permit',rejected(p.begin_boot));check(name+': live initializer entry rejected',rejected(lambda:p.initializer_entry(token)));check(name+': context publication follows completion',p.context_ready==bool(stock and context and normal));check(name+': failure cannot open producers',p.producer().allowed==bool(stock and normal))
 for queue,retained,pending,inflight in [(0,0,0,0),(2,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(2,1,1,1)]:
  for op in ['diagnostic_enter','diagnostic_exit','audio_test_select','audio_test_remove','reinitialize','unknown_setup']:
   state={'queue':queue,'retained':retained,'pending':pending,'inflight':inflight,'test_flag':0,'audio_handler':'normal','page':'pattern','scale_context':'old','boot_permit':p._permit_consumed};before=copy.deepcopy(state);calls=[]
   d=p.run_operation(op,lambda:(calls.append(op),state.clear()))
   check(f'{name}/{queue,retained,pending,inflight}/{op}: whole operation rejected without mutation',not d.allowed and not calls and state==before)
p=ReinitializationPolicy();check('forged initialization permit rejected',rejected(lambda:p.initializer_entry(object())));t=p.begin_boot();check('forged permit after admission rejected',rejected(lambda:p.initializer_entry(object())));p.initializer_entry(t);p.finish_boot(stock_complete=True,context_complete=True,mode_is_normal=True)
for_operation=['pattern_change','note_release','sustain_release','playback_stop']
for op in for_operation:
 check(op+': admitted without reconstructing pool',p.operation(op).allowed and p.initializations==1 and p.context_ready)
check('unknown operation fails closed',not p.operation('computed_unmapped_route').allowed)
out={'PC_only':True,'native_guard_installed':False,'policy':'one initialization permit per fresh boot; no live reconstruction in V1','checks':checks,'passed':True,'limits':['Abstract admission/state model; no producer count or native caller guard is implemented.','Actual command rejection continuation and AudioTest selection veto remain to be verified before machine-code integration.']}
Path('outputs/Digitone-E04-PC-reinitialization-policy-model.json').write_text(json.dumps(out,indent=2));print('PASS',len(checks),'policy assertions')
