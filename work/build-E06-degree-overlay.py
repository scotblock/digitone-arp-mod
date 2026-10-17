from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
DEGREE=0x47be0a00;HOOK=0x47be0c00;TABLE=0x47be0d00;SITE=0x40098116
rows={r['raw_scale']:r['pitch_classes'] for r in json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']}
table=b''.join(bytes([len(rows[s])])+bytes(rows[s])+bytes(15-len(rows[s])) for s in range(35));assert len(table)==560
# degree(fallback_sum, retained_word, selected_note, signed_step_offset, octave_semitones).
a=Asm();a.emit('4fefffe048d70cfc242f0024222f0028262f002c282f00302a2f0034')
a.emit('4a81');a.branch('6a00','fallback');a.emit('200102807fff8000');a.branch('6600','fallback')
a.emit('2c0102860000007f2e01ee8f02870000003f0c8700000024');a.branch('6400','fallback');a.emit('4a87');a.branch('6700','fallback');a.emit('5387')
a.emit('0c8300000080');a.branch('6400','fallback');a.emit('0c84ffffff80');a.branch('6d00','fallback');a.emit('0c840000007f');a.branch('6e00','fallback')
# Stable old quantizer anchors an off-scale held note, choosing lower on ties.
a.emit('2f012f03');absolute(a,'4eb9',0x47be0312);a.emit('508f2600');absolute(a,'45f9',TABLE);a.emit('e98fd5c7') # scale index * 16; A2 += D7
a.emit('7e001e124a87');a.branch('6700','fallback');a.emit('20039086')
a.label('negative_pc');a.emit('4a80');a.branch('6a00','positive_pc');a.emit('06800000000c');a.branch('6000','negative_pc')
a.label('positive_pc');a.emit('0c800000000c');a.branch('6500','rank');a.emit('04800000000c');a.branch('6000','positive_pc')
a.label('rank');a.emit('2c007200')
a.label('scan');a.emit('700010321801bc80');a.branch('6700','found');a.emit('5281b287');a.branch('6d00','scan');a.branch('6000','fallback')
a.label('found');a.emit('d2849686d685')
a.label('negative_rank');a.emit('4a81');a.branch('6a00','positive_rank');a.emit('d28704830000000c');a.branch('6000','negative_rank')
a.label('positive_rank');a.emit('b287');a.branch('6d00','result');a.emit('928706830000000c');a.branch('6000','positive_rank')
a.label('result');a.emit('700010321801d0834a80');a.branch('6d00','outside_byte');a.emit('0c8000000100');a.branch('6400','outside_byte');a.branch('6000','end')
a.label('outside_byte');a.emit('70ff');a.branch('6000','end');a.label('fallback');a.emit('2002');a.label('end');a.emit('4cd70cfc4fef00204e75');degree=a.done();assert len(degree)<=512
# Tail hook runs only after stock selection/step-enable/identity checks succeed.
# An 80-byte stack frame preserves registers, SR and the fallback sum across
# scratch-register-clobbering context helpers. Original track/identity: +120/+124.
a=Asm();a.emit('4fefffb048d77fff40c03f40003c46fc2700752901162f4200082017d081d0822f4000402a2f00782005');absolute(a,'4eb9',0x47be0114);a.emit('4a88');a.branch('6700','fallback')
a.emit('2f052f2f00802f08');absolute(a,'4eb9',0x47be00d6);a.emit('4fef000c')
a.emit('2f2f00042f2f000c2f2f00082f002f2f0050');absolute(a,'4eb9',DEGREE);a.emit('4fef0014');a.branch('6000','restore')
a.label('fallback');a.emit('202f0040');a.label('restore');a.emit('242f000890822f400000302f003c46c04cd77fff4fef0050d082');absolute(a,'4ef9',SITE+8);hook=a.done();assert len(hook)<=256
oldpayload=Path('work/os144/E05-PC-payload.bin').read_bytes();payload=bytearray(oldpayload);assert payload[0xa00:0xf30]==bytes(0x530)
payload[DEGREE-0x47be0000:DEGREE-0x47be0000+len(degree)]=degree;payload[HOOK-0x47be0000:HOOK-0x47be0000+len(hook)]=hook;payload[TABLE-0x47be0000:TABLE-0x47be0000+len(table)]=table
main=bytearray(Path('work/os144/E05-PC-main.bin').read_bytes());off=SITE-0x40000400;assert main[off:off+8].hex()=='75290116d081d082';main[off:off+8]=bytes.fromhex('4ef9')+struct.pack('>I',HOOK)+bytes.fromhex('4e71');main[0x4029c5b0-0x40000400:]=payload
assert len(payload)==len(oldpayload) and len(main)==Path('work/os144/E05-PC-main.bin').stat().st_size
Path('work/os144/E06-PC-main.bin').write_bytes(main);Path('work/os144/E06-PC-payload.bin').write_bytes(payload)
cfg=json.loads(Path('outputs/Digitone-E05-PC-candidate-layout.json').read_text());cfg.update(candidate='pending',hardware_ready=False,pitch_policy='Arp step offsets count selected-scale degrees from the selected held note. Off-scale bases use E05 nearest/lower-tie anchoring; chromatic/invalid/unready context keeps stock arithmetic. Octave semitones and later stock transposes remain separate.',degree_address=DEGREE,degree_bytes=len(degree),degree_hook_address=HOOK,degree_hook_bytes=len(hook),degree_table_address=TABLE,degree_table_bytes=len(table),main_sha256=hashlib.sha256(main).hexdigest(),payload_sha256=hashlib.sha256(payload).hexdigest())
cfg['regions']+= [{'name':'degree_helper','base':DEGREE,'bytes':len(degree)},{'name':'arp_degree_tail_hook','base':HOOK,'bytes':len(hook)}];cfg['components']+=[{'name':'degree_helper','base':DEGREE,'bytes':len(degree)},{'name':'arp_degree_tail_hook','base':HOOK,'bytes':len(hook)},{'name':'degree_table','base':TABLE,'bytes':len(table)}]
cfg['hooks']+=[{'name':'arp_degree_tail_hook','site':SITE,'length':8,'previous':'75290116d081d082','replacement':main[off:off+8].hex()}]
Path('outputs/Digitone-E06-PC-candidate-layout.json').write_text(json.dumps(cfg,indent=2));print('E06 degree helper',len(degree),'hook',len(hook),'table',len(table),'payload size unchanged',len(payload))
