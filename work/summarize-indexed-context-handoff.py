import pathlib,json
O=pathlib.Path('outputs');rows=[]
for name in ['all','stock','all-scaled','stock-scaled']:
 r=json.loads((O/f'Digitone-indexed-context-handoff-{name}.json').read_text())
 assert r['failure'] is None and r['halted'] is None and all(r['storage_checks'].values())
 assert not r['helper_reinjected'] and r['firmware_sha256']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
 delayed=r['delayed_note_fixture'];e=delayed['event'];g=delayed['generation']
 writer=next(x for x in r['events'] if x['kind']=='backing_write' and x['incoming_backing']!=x['backing'])
 complete=next(x for x in r['events'] if x['kind']=='transition_commit_done' and x['ms']>=writer['ms'] and x['backing']==writer['incoming_backing'])
 publication=next(x for x in writer['pending_publications'] if x['event']==e and x['generation']==g)
 acceptance=next(x for x in r['events'] if x['kind']=='acceptance' and x['event']==e and x['generation']==g and x['ms']>writer['ms'])
 assert acceptance['backing']==writer['incoming_backing'] and acceptance['publication']['generation']==g
 assert writer['pc']=='0x40095926' and complete['pc']=='0x40095bd6'
 assert bytes.fromhex(writer['sustain_flags'])[3]==1 and writer['sustain_lists'][3]!='0x0'
 release=next(x for x in r['marks'] if x['label']=='CC64 released after handoff')
 assert set(bytes.fromhex(release['sustain_flags']))=={0} and all(x=='0x0' for x in release['sustain_lists'])
 assert len([x for x in r['events'] if x['kind']=='CC_handler'])>=2
 checks=[]
 for q in r['quantizer_calls']:
  output=next(x for x in r['pitch_outputs'] if x['ordinal']>q['ordinal'] and x['event']==q['event'] and x['generation']==q['generation'])
  assert output['fixed_note']==q['expected']<<16,(name,q,output)
  if name=='all-scaled':assert (int(q['word'],16)&127)==61 and ((int(q['word'],16)>>7)&63)==1
  checks.append({'ms':q['ms'],'note':q['note'],'expected':q['expected'],'actual':output['fixed_note']//65536,'word':q['word']})
 if name=='all-scaled':
  assert acceptance['candidate_at_acceptance']==publication['metadata']=='0x8000033b'
  assert any(x['note']!=x['actual'] for x in checks)
 rows.append({'case':name,'duration_ms':r['marks'][-1]['ms'],'writer':{k:writer[k] for k in ['ms','pc','backing','incoming_backing','sustain_flags','sustain_lists']},'complete_ms':complete['ms'],'queue_crossing':{'event':e,'generation':g,'publication_ms':publication['ms'],'acceptance_ms':acceptance['ms'],'publication_context':publication.get('metadata'),'acceptance_context':acceptance.get('candidate_at_acceptance'),'arp_eligibility_proved':False},'MIDI_sustain_crosses_and_releases':True,'quantizer_outputs':checks,'storage_checks':r['storage_checks'],'root_scale_fixture':r.get('root_scale_fixture')})
out={'firmware_modified':False,'passed':True,'timing':'native functional, not cycle-aware','cases':rows,'limits':['Queue crossing is deliberately induced by delaying one actual stock-produced event by 48,000,000 queue ticks in PC RAM.','The crossing event is a direct note with zero identity; its original metadata survives, but this does not prove an eligible queued arp quantizer uses the old scale after replacement.','Scaled cases set the two pattern root/scale fields in PC RAM; candidate/retained metadata is captured by the native hooks, with no metadata injection.','MIDI input bytes and receive-enable setting are explicit fixtures; the stock UART receive/parser/controller path executes.','Finite native observations do not establish physical protection or full RAM ownership.']}
(O/'Digitone-indexed-context-handoff-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps({'passed':True,'cases':[{'case':x['case'],'handoff_ms':x['writer']['ms'],'quantizer_calls':len(x['quantizer_outputs'])} for x in rows]},indent=2))
