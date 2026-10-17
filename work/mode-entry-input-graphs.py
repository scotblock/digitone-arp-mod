exec(open('work/setup-failure-entry-audit.py').read().split('graphs=[')[0])
import hashlib
entries=[('entry_callbacks',0x400d6d46,0x400d6db6),('parent_entry',0x400d653a,0x400d65d4),('mode_entry_invoker',0x400ae458,0x400ae45e),('alternate_install',0x400d95cc,0x400d95ee),('test_audio_entry',0x4008dfd2,0x4008e032),('test_channel_clear',0x4008dc96,0x4008dce0),('test_pair_clear',0x4008db90,0x4008dbc6),('midi_receive_task',0x400db15a,0x400db300),('enter_request',0x400d6aba,0x400d6adc)]
graphs=[cfg(n,s,e) for n,s,e in entries]
checks=[]
def check(n,c):assert c,n;checks.append(n)
check('first receive queue tests enable bit one',graphs[7]['instructions']['0x400db220']['instruction']=='moveq #$1, d6' and graphs[7]['instructions']['0x400db222']['instruction']=='and.l $4131ba1c.l, d6')
check('second receive queue tests enable bit two',graphs[7]['instructions']['0x400db286']['instruction']=='moveq #$2, d7' and graphs[7]['instructions']['0x400db288']['instruction']=='and.l $4131ba1c.l, d7')
check('mode vectors and test flag absent from local MIDI task',not any(any(t in x['instruction'] for t in ['400002fc','40253e80','400d95cc']) for x in graphs[7]['instructions'].values()))
check('mode installers have no local payload-owner/receive-gate accesses',not any(any(t in x['instruction'] for t in ['4199fe94','4199fe98','4199d590','41345f08','4131ba1c']) for g in graphs[3:7] for x in g['instructions'].values()))
check('test helper only calls diagnostic clears and timer installation', [c['instruction'] for c in graphs[4]['calls']]==['jsr (a2)','jsr (a2)','jsr (a2)','jsr $400012c8.l'])
check('entry callback dispatcher clears page close request',graphs[0]['instructions']['0x400d6d6a']['instruction']=='move.b d0, $30(a2)')
check('test clear helpers use diagnostic base',all(any('$429a3c14' in v['instruction'] for v in g['instructions'].values()) for g in graphs[5:7]))
text=b[0x401bb013-base:].split(b'\0',1)[0].decode();check('test entry command recognized',text=='#ENTER_TEST_MODE')
refs=[]
for off in range(0,len(b)-6,2):
 if b[off+2:off+6]==struct.pack('>I',0x4131ba1c):refs.append(hex(base+off))
check('only exact absolute-literal gate candidates are receive reads',refs==['0x400db222','0x400db288'])
pathlib.Path('outputs/Digitone-mode-entry-input-graphs.json').write_text(json.dumps({'firmware_modified':False,'graphs':graphs,'checks':checks,'test_entry_command':text,'receive_gate_exact_literal_candidates':refs,'limitations':['Gate writers may use containing-object offsets or computed pointers.','Called child-page methods and outer command/task state not certified.','Both MIDI queues admit SysEx f0 independently of these enable bits.']},indent=2))
print(json.dumps({'checks':len(checks),'graphs':len(graphs),'instructions':sum(len(g['instructions']) for g in graphs),'command':text}))
