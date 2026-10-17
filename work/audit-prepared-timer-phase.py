import pathlib,json,sys,hashlib,pickle
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import snapshot
names={'shared':'work/cache-fresh-trace-prepared.snap','previous_stock':'work/cache-native-prepared-stock-handoff.snap'}
blobs={k:snapshot._load_blob(v) for k,v in names.items()}
out={'firmware_modified':False,'snapshots':{k:{'path':p,'sha256':hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(),'regs':blobs[k]['regs'],'components':{n:hashlib.sha256(pickle.dumps(v,protocol=4)).hexdigest() for n,v in blobs[k]['components'].items()}} for k,p in names.items()}}
out['same_timer_state']=blobs['shared']['components'].get('timers')==blobs['previous_stock']['components'].get('timers')
out['same_registers']=blobs['shared']['regs']==blobs['previous_stock']['regs']
out['component_names']=list(blobs['shared']['components'])
out['timer_states']={k:b['components'].get('timers') for k,b in blobs.items()}
pathlib.Path('outputs/Digitone-prepared-timer-phase-audit.json').write_text(json.dumps(out,indent=2,default=str))
print(json.dumps({k:v for k,v in out.items() if k not in ['timer_states','snapshots']},indent=2))
print('timer states',str(out['timer_states'])[:1600])
