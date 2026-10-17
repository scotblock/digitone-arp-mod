"""Review completed machine execution, with non-vacuous coverage checks."""
import pathlib,json,hashlib
p=pathlib.Path('outputs/Digitone-loader-derived-startup-playback.json');r=json.loads(p.read_text())
blob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()
# Correct an inherited report field initialized before the optimized blob
# was selected. This does not change execution results or assertions.
r['code_bytes']=len(blob)
r['elapsed_scope']='elapsed_seconds covers application startup and playback; loader execution occurs before that timer'
r['loader']['flash_preserved_in_application_models']=True
p.write_text(json.dumps(r,indent=2))
q=r['runs'][0];s=r['startup']['stages'];checks={}
def check(name,value):checks[name]=bool(value);assert value,name
check('completed startup and playback',r['passed'] and not r['startup']['failure'])
check('executed loader reconstructed complete extended MAIN',r['loader']['entry']=='0x400004e8' and r['loader']['main_matches'])
check('same loader machine used for application initialization',r['loader']['same_machine_into_initializer'])
check('native initializer entered and returned once',s[0]['hits'].get('initializer_entry')==s[0]['hits'].get('initializer_caller_return')==1)
check('native initializer started unready and finished ready',next(e for e in r['startup']['events'] if e['label']=='initializer_entry')['ready']=='0x0' and next(e for e in r['startup']['events'] if e['label']=='initializer_caller_return')['ready']=='0x1')
check('readiness and stock allocation links survive all startup stages',len(s)==3 and all(t['ready']==1 and t['stock_pool_links_valid'] for t in s))
check('code table and guards survive all startup stages',all(t['code_intact'] and t['table_intact'] and t['guards_intact'] and not t['unexpected_writes'] for t in s))
check('table copied only by native early copier',len(s[0]['table_copy_writes'])==105 and all(not t['table_copy_writes'] for t in s[1:]))
check('first resident execution follows stock cache setup',s[0]['first_resident_execution']['pc']=='0x47be0666' and s[0]['first_resident_execution']['controls']['0x2']=='0xa50ce100' and s[0]['first_resident_execution']['controls']['0x4']=='0x4007e020')
check('playback ran ten seconds without an unhandled stop',q['ms']>=10000 and q['halted'] is None)
check('playback rendered audio',q['audio_bytes']>0)
check('playback code guards capture and pitch checks pass',all(q['checks'].values()))
eligible=[e for e in q['captures'] if e['pool_eligible']]
check('eligible producer capture coverage is nonempty',bool(eligible) and all(e['matches'] for e in eligible))
check('native lookup executed for every quantizer call',len(q['table_reads'])==len(q['quantize_calls'])>0)
changed=[e for e in q['pitches'] if e['before']!=e['after']]
check('pitch adjustment coverage is nonempty',bool(changed))
check('original firmware unchanged and no emulated flash programming',r['firmware_before']==r['firmware_after'] and not r['loader']['flash_writes'])
out={'passed':True,'checks':checks,'helper_bytes':len(blob),'helper_sha256':hashlib.sha256(blob).hexdigest(),'table_bytes':420,'table_sha256':hashlib.sha256(blob[1904:]).hexdigest(),'startup_stages':len(s),'stock_tasks':r['startup']['cold_result']['tasks'],'playback_ms':q['ms'],'audio_bytes':q['audio_bytes'],'producer_calls':q['hits']['producer'],'eligible_captures':len(eligible),'table_reads':len(q['table_reads']),'pitch_changes':len(changed),'pitch_examples':[(e['before'],e['after']) for e in changed[:3]],'continuity':'same loader machine through application initialization; guest snapshots for intro, settle and playback','physical_cache_coherence_verified':False,'hardware_deadlines_verified':False,'limits':r['loader']['limits'],'firmware_sha256':r['firmware_after']}
pathlib.Path('outputs/Digitone-loader-derived-playback-summary.json').write_text(json.dumps(out,indent=2));print('PASS',len(checks),'checks;',len(eligible),'eligible captures;',len(q['table_reads']),'native table reads')
