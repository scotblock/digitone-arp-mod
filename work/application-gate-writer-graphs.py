exec(open('work/setup-failure-entry-audit.py').read().split('graphs=[')[0])
entries=[('settings_constructor',0x4006f83a,0x4006fc62),('settings_menu_builder',0x4006f0fe,0x4006f57e),('selected_child_helper',0x400d5f02,0x400d5f64),('config_defaults',0x40013722,0x400138de),('config_deserializer',0x400094aa,0x40009d24),('receive_gate_setter',0x4002af1a,0x4002af70),('note_gate_setter',0x4002b344,0x4002b38e),('note_gate_toggle',0x4002b38e,0x4002b3e2),('config_binding',0x40029546,0x400295aa),('project_binding',0x40022366,0x40022432),('config_pointer_getter',0x40138354,0x4013835e),('project_pointer_getter',0x40136086,0x40136090),('property_pointer_binding',0x4013835e,0x40138374),('receive_ui_change',0x40066750,0x40066798),('note_ui_toggle',0x40066fe6,0x40067000),('boot_project_pointer',0x4002235a,0x40022366)]
graphs=[cfg(n,s,e) for n,s,e in entries]
checks=[]
def check(n,c):assert c,n;checks.append(n)
by={g['name']:g for g in graphs}
check('global config address equals project base plus offset',0x407b00b0+0xb6b8e0==0x4131b990)
check('receive gate lies at config +8c',0x4131b990+0x8c==0x4131ba1c)
check('note gate lies at config +b0',0x4131b990+0xb0==0x4131ba40)
check('config defaults initialize gates at their recovered fields',by['config_defaults']['instructions']['0x400137b4']['instruction']=='move.l d1, $8c(a2)' and by['config_defaults']['instructions']['0x400137ea']['instruction']=='move.l d0, $b0(a2)')
check('project config binding adds recovered config offset',by['project_binding']['instructions']['0x40022384']['instruction']=='addi.l #$b6b8e0, d0')
check('property binding publishes underlying pointer',by['property_pointer_binding']['instructions']['0x40138364']['instruction']=='move.l $8(a7), $10(a0)')
check('UI config getter uses underlying pointer',by['config_pointer_getter']['instructions']['0x40138358']['instruction']=='move.l $10(a0), d0')
check('concrete property vtable getter and notifier resolved',struct.unpack_from('>I',b,0x40174fc8-base+0x28)[0]==0x40138354 and struct.unpack_from('>I',b,0x40174fc8-base+0x10)[0]==0x401386a8)
check('actual receive setter writes recovered field',by['receive_gate_setter']['instructions']['0x4002af52']['instruction']=='move.l d2, $8c(a0)')
check('actual note setter and toggle write recovered field',by['note_gate_setter']['instructions']['0x4002b370']['instruction']=='move.l d2, $b0(a0)' and by['note_gate_toggle']['instructions']['0x4002b3ca']['instruction']=='move.l d0, $b0(a3)')
check('serialized gate source offsets resolved',by['config_deserializer']['instructions']['0x40009732']['instruction']=='mvz.b $28(a3), d1' and by['config_deserializer']['instructions']['0x40009806']['instruction']=='mvz.b $31(a3), d1')
check('AudioTestMenuView label exact',b[0x401bd1ce-base:].split(b'\0',1)[0]==b'AudioTestMenuView')
check('settings constructor creates audio page then stores its reference',by['settings_constructor']['instructions']['0x4006fb6c']['instruction']=='jsr $400ae9fa.l' and by['settings_constructor']['instructions']['0x4006fb90']['instruction']=='pea.l $2b4(a2)')
# The leaf callbacks are a confirmed contiguous set of complete functions.
starts=[0x4006f57e,0x4006f5c4,0x4006f60a,0x4006f650,0x4006f696,0x4006f6dc,0x4006f722,0x4006f768,0x4006f7ae,0x4006f7f4]
ends=starts[1:]+[0x4006f83a]
actions=[]
for start,end in zip(starts,ends):
 g=cfg('settings_action_'+hex(start),start,end);graphs.append(g)
 child=[x['instruction'] for x in g['instructions'].values() if x['instruction'].startswith('lea.l') and re.search(r'\$2[0-9a-f]{2}\(a0\)',x['instruction'])]
 assert len(child)==1
 actions.append({'entry':hex(start),'child_field':child[0]})
registered=[]
for a,v in by['settings_menu_builder']['instructions'].items():
 match=re.fullmatch(r'move.l #\$(4006f[0-9a-f]+), d0',v['instruction'])
 if match and int(match[1],16) in starts:registered.append(int(match[1],16))
check('all ten menu action callbacks recovered',registered==starts)
check('none of recovered normal-menu actions selects audio field',all('$2b4(' not in a['child_field'] for a in actions))
check('selected child helper invokes recovered outer entry',by['selected_child_helper']['instructions']['0x400d5f3c']['instruction']=='jsr $400d7a6e.l')
check('selected child helper has no local gate or payload references',not any(any(t in v['instruction'] for t in ['4131ba1c','4131ba40','4002af1a','4002b344','4002b38e','4199fe','4199d590','41345f08']) for v in by['selected_child_helper']['instructions'].values()))
pathlib.Path('outputs/Digitone-application-gate-writer-graphs.json').write_text(json.dumps({'checks':checks,'graphs':graphs,'settings_actions':actions,'firmware_modified':False,'limits':['Normal-menu action enumeration does not exclude computed or diagnostic selection elsewhere.','Writer inventory is concrete recovered routes, not global exhaustive alias certification.']},indent=2))
print(json.dumps({'checks':len(checks),'graphs':len(graphs),'instructions':sum(len(g['instructions']) for g in graphs),'actions':actions}))
