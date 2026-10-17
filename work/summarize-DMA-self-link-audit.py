import json,pathlib
p=pathlib.Path('outputs')
r=json.loads((p/'Digitone-DMA-runtime-configuration.json').read_text());a=r['runs'][0]['memory_model']['configuration_audit'];n=json.loads((p/'Digitone-DMA-startup-config-native.json').read_text());b=json.loads((p/'Digitone-DMA-main-startup-config-trace.json').read_text());boot=json.loads((p/'Digitone-DMA-bootstrap-config-trace.json').read_text());c=json.loads((p/'Digitone-DMA-arbitration-counterexample.json').read_text());ssi=json.loads((p/'Digitone-DMA-SSI-profile-check.json').read_text())
assert r['failure'] is None and r['firmware_before']==r['firmware_after']
assert len(n['cases'])==5 and b['writes']==[{'pc':'0x40000552','address':'0xfc044000','size':4,'value':'0xe406'}]
assert b['CR']=='0xe406' and b['priority_bytes']==bytes(range(64)).hex()
assert a['writes']==[] and a['counts']['starts_with_other_software_active']==0 and a['counts']['minor_boundaries_with_competitor']==0
assert boot['stop']=='limit' and boot['reached'] is None
assert ssi['tx_channel']==54 and ssi['rx_channel']==52
s={'firmware_modified':False,'firmware_sha256':r['firmware_after'],'explicit_firmware_operation':'EDMA_CR |= 0x6 at 0x40000552','documented_reset_seed_result':{'CR':'0xe406','CLM':False,'ERCA':True,'ERGA':False,'group_priorities':[0,1,2,3],'preemption_available':False},'native_startup_cases':n['cases'],'main_startup_trace':b,'bootstrap_scope':{'stop':boot['stop'],'estimated_instructions':boot['instructions'],'full_handoff_verified':False},'sampled_runtime':{'total_ms':r['runs'][0]['ms'],'active_playback_ms':100,'configuration':a['initial'],'configuration_writes':a['writes'],'counts':a['counts']},'controlled_counterexample':{k:v for k,v in c.items() if k!='payload'},'SSI':ssi,'remaining_gap':'Single shared eDMA arbiter at minor-loop boundaries including SSI requests; inherited reset/handoff, arbitration latency and real hardware timing remain unverified'}
(p/'Digitone-DMA-self-link-audit-summary.json').write_text(json.dumps(s,indent=2));print('Configuration, runtime observations and controlled counterexample checks passed.')
