import json,pathlib
out=pathlib.Path('outputs');p=out/'Digitone-shared-memory-long-summary.json';s=json.loads(p.read_text());j=json.loads((out/'Digitone-shared-memory-long-comparison.json').read_text());r=j['runs'][1]
q=r['quantizer_calls'];pitches=[x for x in r['pitch'] if x['track']==2]
assert len(q)==len(pitches)==5
validation=[]
for call,event in zip(q,pitches):
 assert event['fixed_note']==call['expected']*65536
 validation.append({'input':call['note'],'expected':call['expected'],'actual':event['fixed_note']//65536})
assert [(x['track'],x['fixed_note']) for x in j['runs'][0]['pitch'] if x['track']!=2]==[(x['track'],x['fixed_note']) for x in r['pitch'] if x['track']!=2]
s['pitch_validation']=validation;s['other_observed_tracks_unchanged']=True
p.write_text(json.dumps(s,indent=2));print('All five quantized outputs match the oracle; other observed tracks match stock.')
