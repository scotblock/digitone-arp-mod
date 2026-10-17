exec(open('work/setup-failure-entry-audit.py').read().split('graphs=[')[0])
entries=[('outer_add_page',0x400d7a6e,0x400d7bcc),('virtual_enter_wrapper',0x400d6944,0x400d6950),('signed_parent_thunk',0x400d65d4,0x400d65de),('parent_entry',0x400d653a,0x400d65d4),('entry_dispatcher',0x400d6d46,0x400d6db6),('base_entry_callback',0x400d5eca,0x400d5ee6),('base_entry_registration',0x400d59dc,0x400d5b60),('mode_constructor',0x400ae9fa,0x400aeb1a),('note_on_wrapper',0x400dc8c4,0x400dc90c),('note_channel_router',0x400dc758,0x400dc8c4),('live_note_producer',0x400dc432,0x400dc758),('input_notification',0x400db642,0x400db68a)]
graphs=[cfg(n,s,e) for n,s,e in entries]
checks=[]
def check(n,c):assert c,n;checks.append(n)
check('signed thunk uses MOVEQ C8 encoding',graphs[2]['instructions']['0x400d65d4']['bytes']=='70c8')
check('base constructor clears optional child handle',graphs[6]['instructions']['0x400d5a60']['instruction']=='clr.l $8c(a2)')
check('base constructor registers entry before derived mode constructor',graphs[6]['instructions']['0x400d5ab6']['instruction']=='move.l #$400d5eca, d0' and graphs[7]['instructions']['0x400aeab4']['instruction']=='move.l #$400ae458, d0')
check('full handler contains additional note gate',graphs[8]['instructions']['0x400dc8d0']['instruction']=='tst.l $4131ba40.l')
check('outer entry rejects already attached page via actual predicate',graphs[0]['instructions']['0x400d7b50']['instruction']=='jsr $400d6b9c.l')
check('outer virtual entry is after page insertion and maintenance',all(a in graphs[0]['instructions'] for a in ['0x400d7b94','0x400d7b9c','0x400d7bb0']))
pathlib.Path('outputs/Digitone-full-handler-transition-graphs.json').write_text(json.dumps({'graphs':graphs,'checks':checks,'firmware_modified':False},indent=2))
print(json.dumps({'checks':len(checks),'graphs':len(graphs),'instructions':sum(len(g['instructions']) for g in graphs)}))
