from pathlib import Path
s=Path('work/summarize-E04-producer-startup-control.py').read_text()
s=s.replace('Digitone-E04-producer-startup-control-checks.json','Digitone-E04-restored-capture-control-checks.json')
s=s.replace("scales[0]['bytes']=='ff'","scales[0]['bytes']=='00'")
s=s.replace(" assert roots[0]['bytes'] in ['43','3c']", " assert track==0 and roots[0]['bytes']=='3c'\n assert roots[0]['bytes'] in ['43','3c']")
s=s.replace("expected=0x80000000|(track<<13)|int(roots[0]['bytes'],16)","expected=0x80000000|(track<<13)|(((int(scales[0]['bytes'],16)+1)&63)<<7)|int(roots[0]['bytes'],16)")
s=s.replace(" assert all(x['outputs'][k]==y['outputs'][k] for k in regs)"," assert all(x['outputs'][k]==y['outputs'][k] for k in regs)\n assert all(x['outputs'][k]==y['outputs'][k] for k in ['event_bytes','private_header','stack_64_bytes'])\n assert x['replay_matches_live_memory'] and y['replay_matches_live_memory']\n assert x['isolated_replay']['outputs']['context_slots'].startswith('800000bc')\n assert y['outputs']['context_slots']=='00'*16")
needle="summary={'only_changed_interval':['0x400947ec','0x400947f4'],'calls':[],'all_checks_passed':True}"
addition="""assert len(a['producer_calls'])==len(b['producer_calls'])==4
for row in [a,b]:
 assert row['intro_exit_seen']
 assert not any(e['pc']=='0x400a8402' for e in row['restore_events'])
 assert any(e['pc']=='0x400a838c' and e['d0']=='0x1' for e in row['restore_events'])
 assert any(e['pc']=='0x400a83f4' for e in row['restore_events'])
 assert any(e['pc']=='0x400a8410' and e['d2']=='0x0' and not int(e['global_flags'],16)&4 for e in row['restore_events'])
"""
assert needle in s;s=s.replace(needle,addition+needle)
s=s.replace("syx=Path(","summary['isolated_instruction_counts']=[[len(x['isolated_replay']['instructions']),len(y['isolated_replay']['instructions'])] for x,y in zip(a['producer_calls'],b['producer_calls'])]\nsyx=Path(",1)
s=s.replace("p.write_text(json.dumps(j,indent=2)+'\\n')", "p.write_text(json.dumps(j,indent=2)+'\\n')\nPath('outputs/Digitone-E04-restored-capture-control-summary.json').write_text(json.dumps(summary,indent=2)+'\\n')")
exec(compile(s,'E04-restored-capture-control-summary','exec'))
