import pathlib,json,collections,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import cfisa
o=pathlib.Path('outputs');raw={k:json.loads((o/('Digitone-fresh-handoff-'+k+'-native-pattern-copy.json')).read_text()) for k in ['trace','pitch-fetch-neutral']}
segments={}
for k,r in raw.items():
 d=r['fresh_cost'];entry=next(x['cycles'] for x in d['boundaries'] if x['label']=='pitch_output')
 store=d['next_stores'][0]['store_cycles']
 bb=[x for x in d['blocks'] if entry<=x['cycles']<store and x['instructions']]
 totals=collections.Counter()
 for b in bb:totals[b['pc']]+=b['cost']
 segments[k]={'start_cycle':entry,'first_store_cycle':store,'elapsed_cycles':store-entry,'block_cycles':sum(b['cost'] for b in bb),'fetch_cycles':sum(b['fetch_cycles'] for b in bb),'instructions':sum(b['instructions'] for b in bb),'vectors':sorted(set(tuple(b['vectors']) for b in bb)),'highest_block_cost_addresses':totals.most_common(12),'blocks':bb}
a,b=segments['trace']['blocks'],segments['pitch-fetch-neutral']['blocks']
i=0
while i<min(len(a),len(b)) and (a[i]['pc'],a[i]['size'])==(b[i]['pc'],b[i]['size']):i+=1
comparison={'matching_post_pitch_blocks':i,'first_PC_sequence_divergence':{'trace':a[max(0,i-2):i+4],'pitch-fetch-neutral':b[max(0,i-2):i+4]} if i<min(len(a),len(b)) else None,'first_store_advance_cycles':segments['trace']['first_store_cycle']-segments['pitch-fetch-neutral']['first_store_cycle'],'pitch_fetch_removed_cycles':raw['pitch-fetch-neutral']['fresh_cost']['removed_fetch_cycles']}
filtered={k:[(x['pc'],x['size']) for x in d['blocks'] if x['vectors']==[191]] for k,d in segments.items()}
comparison['same_render_PC_sequence_excluding_nested_IRQ']=filtered['trace']==filtered['pitch-fetch-neutral']
comparison['post_pitch_extra_block_cycles_in_control']=segments['pitch-fetch-neutral']['block_cycles']-segments['trace']['block_cycles']
comparison['post_pitch_extra_fetch_cycles_in_control']=segments['pitch-fetch-neutral']['fetch_cycles']-segments['trace']['fetch_cycles']
comparison['post_pitch_extra_other_cycles_in_control']=(segments['pitch-fetch-neutral']['elapsed_cycles']-segments['pitch-fetch-neutral']['block_cycles'])-(segments['trace']['elapsed_cycles']-segments['trace']['block_cycles'])
stock=pathlib.Path('work/section-3.bin').read_bytes();base=0x40000400;read=cfisa.reader(stock,base)
disassembly={}
for pc in [0x4009a052,0x4009a38c,0x40096be0,0x40096c26]:
 instructions=[];at=pc
 while at<pc+32:
  ins=cfisa.decode(read(at),at)
  instructions.append({'pc':hex(at),'bytes':stock[at-base:at-base+ins.length].hex(),'operation_class':ins.op,'length':ins.length,'flags':ins.flags})
  at+=ins.length
 disassembly[hex(pc)]=instructions
report={'firmware_modified':False,'model_only':True,'comparison':comparison,'post_pitch_segments':{k:{x:v for x,v in d.items() if x!='blocks'} for k,d in segments.items()},'instruction_windows':disassembly,'limitations':['Block costs include computation/flow/fetch; data charges are separate.','Addresses at the remaining capture are observed positions, not proof that these routines uniquely caused the delay.','No new replay or hardware test; this compares the two completed diagnostic traces.']}
(o/'Digitone-fresh-downstream-comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
