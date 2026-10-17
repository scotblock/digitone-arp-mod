"""Actual root/scale capture and coarse pitch instructions; PC overlays only."""
exec(open('work/test-resident-caller-helpers.py').read().split('checks=[];cases=[];OWNER=')[0])
RESIDENT_END=cursor;cursor=0x50010000
# capture(backing, source track): validated header plus supplied writer gates.
a=Asm();a.emit('4feffff848d7000c40c346fc2700242f00102002');absolute(a,'4eb9',names['resolve']);a.emit('4a88');a.branch('6700','none');a.emit('4aa90010');a.branch('6600','none');a.emit('4aa90014');a.branch('6600','none');a.emit('206f000c4a88');a.branch('6700','none');a.emit('2202');a.label('track_loop');a.emit('4a81');a.branch('6700','read');a.emit('41e803d05381');a.branch('6000','track_loop');a.label('read');a.emit('71a803cb0c8000000080');a.branch('6400','none');a.emit('732803ce52810c8100000024');a.branch('6400','none');a.emit('ef89e18aeb8a80818082008080000000');a.branch('6000','end');a.label('none');a.emit('4280');a.label('end');a.emit('46c34cd7000c4fef00084e75');add('capture',a)
# Write candidate only for an exactly matched fixed pool entry, no union bytes.
a=Asm();a.emit('7000');absolute(a,'4eb9',names['resolve']);a.emit('4a88');a.branch('6700','end');a.emit('d1fcfffff4f0226f0004223c00000080203c4199da94');a.label('loop');a.emit('b3c0');a.branch('6700','found');a.emit('06800000004841e800045381');a.branch('6600','loop');a.branch('6000','end');a.label('found');a.emit('202f00082080');a.label('end');a.emit('4e75');add('candidate_store',a)
# Nearest permitted MIDI note, lower ties first; use actual stock membership.
a=Asm();a.emit('4fefffe048d70cfc242f0024222f0028');a.emit('0c8200000080');a.branch('6400','fallback');a.emit('4a81');a.branch('6a00','fallback');a.emit('200102807fff8000');a.branch('6600','fallback');a.emit('260102830000007f2801ee8c02840000003f0c8400000024');a.branch('6400','fallback');a.emit('4a84');a.branch('6700','fallback');a.emit('53847a00');a.label('loop');a.emit('2c029c85');a.branch('6b00','upper');a.emit('2f042f032f06');absolute(a,'4eb9',0x40106b6c);a.emit('4fef000c4a80');a.branch('6600','lower_hit');a.label('upper');a.emit('2e02de850c8700000080');a.branch('6400','next');a.emit('2f042f032f07');absolute(a,'4eb9',0x40106b6c);a.emit('4fef000c4a80');a.branch('6600','upper_hit');a.label('next');a.emit('52850c8500000080');a.branch('6500','loop');a.label('fallback');a.emit('2002');a.branch('6000','end');a.label('lower_hit');a.emit('2006');a.branch('6000','end');a.label('upper_hit');a.emit('2007');a.label('end');a.emit('4cd70cfc4fef00204e75');add('quantize',a)
# pitch(event, coarse): validate stock event, state, head and retained binding.
a=Asm();a.emit('4fefffdc48d71cfc40c746fc2700246f0028282f002c');a.emit('202a00000c8000000002');a.branch('6400','fallback');a.emit('0caa000000010004');a.branch('6600','fallback');a.emit('242a00080c8200000004');a.branch('6400','fallback');a.emit('202a002808000013');a.branch('6700','fallback');a.emit('262a0040');a.branch('6700','fallback');a.emit('207c41344530267c41345f08227c413456202002');a.label('track_loop');a.emit('4a80');a.branch('6700','stock_checks');a.emit('41e8002847eb004843e900045380');a.branch('6000','track_loop');a.label('stock_checks');a.emit('b6a80018');a.branch('6600','fallback');a.emit('4a91');a.branch('6700','fallback');a.emit('202b00000c8000000002');a.branch('6400','fallback');a.emit('0cab000000010004');a.branch('6600','fallback');a.emit('b4ab0008');a.branch('6600','fallback');a.emit('b6ab0040');a.branch('6600','fallback');a.emit('202b002808000013');a.branch('6700','fallback');a.emit('2002');absolute(a,'4eb9',names['resolve']);a.emit('4a88');a.branch('6700','fallback');a.emit('2f022f032f08');absolute(a,'4eb9',names['read']);a.emit('4fef000c2f0046c72f04');absolute(a,'4eb9',names['quantize']);a.emit('508f');a.branch('6000','end');a.label('fallback');a.emit('2004');a.label('end');a.emit('46c74cd71cfc4fef00244e75');add('pitch',a)
# Source producer hook, B=a3, t=d4, newly built event=a2.
a=Asm();save(a);a.emit('2f042f0b');absolute(a,'4eb9',names['capture']);a.emit('508f2f002f0a');absolute(a,'4eb9',names['candidate_store']);a.emit('508f');restore(a);a.emit('254400082544003c');absolute(a,'4ef9',0x40093efc);add('producer_capture',a)
# Shared note-loop hook; keep all state except saved coarse d6.
a=Asm();save(a);a.emit('2f062f0b');absolute(a,'4eb9',names['pitch']);a.emit('508f2f400018');restore(a);a.emit('2f037a07202b0028');absolute(a,'4ef9',0x4009dfa2);add('pitch_hook',a)
# Event allocator has no arguments: an extra return frame preserves original caller.
a=Asm();after_alloc=cursor+16;absolute(a,'4879',after_alloc);a.emit('40c046fc2700');absolute(a,'4ef9',0x400f062c);assert len(a.code)==18 # PEA6 + original6 + JMP6
# correct after address for 18-byte prefix
for j,x in enumerate(u32(cursor+18)):a.code[2+j]=x
save(a);a.emit('42a72f08');absolute(a,'4eb9',names['candidate_store']);a.emit('508f');restore(a);a.emit('4e75');add('allocate_clear',a)
OLD_FETCH=fetch
# Existing fixture fetch sees added helper bodies too; preserve original fallback.
def fetch(pc):
 if not overlay_enabled:return b[pc-base:pc-base+16]
 if pc==0x40093ef4:return bytes.fromhex('4ef9')+u32(names['producer_capture'])+bytes.fromhex('4e71')
 if pc==0x4009df9a:return bytes.fromhex('4ef9')+u32(names['pitch_hook'])+bytes.fromhex('4e71')
 if pc==0x400f0626:return bytes.fromhex('4ef9')+u32(names['allocate_clear'])
 return OLD_FETCH(pc)
RANGES.extend((addr,addr+len(code)) for addr,code in fixtures.items())
RANGES.extend([(0x40106b6c,0x40106be2),(0x40093ef4,0x40093f12),(0x4009df78,0x4009dfae),(0x4009755e,0x400978b8),(0x4009de50,0x4009dfae)])
# Stock membership SGT is derived from the arithmetic flags, not an oracle result.
for var in ['source','route_source']:
 st=globals()[var];st=st.replace("   elif m=='swap':", "   elif m=='sgt':self.put(ops[0],1,255 if not self.sr&4 and not (bool(self.sr&8)^bool(self.sr&2)) else 0)\n   elif m=='swap':")
 globals()[var]=st
src=source.replace('b[pc-base:pc-base+16]','fetch(pc)');exec('if True:\n'+src);Machine.run=run
rtsrc=route_source.replace('b[pc-base:pc-base+16]','fetch(pc)');exec('if True:\n'+rtsrc);Machine.route=route
for addr,code in fixtures.items():
 items=list(md.disasm(code,addr));assert sum(i.size for i in items)==len(code),(hex(addr),len(code),sum(i.size for i in items))
 assert all(i.id or bytes(i.bytes) in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)] for i in items)
checks=[];cases=[];OWNER=0x28000000;PATTERN=0x29000000;OTHER=0x2a000000;POOL=0x4199da94

def machine():
 m=create();m.map(0x413424e8,4);m.map(OWNER,0x14c70);m.map(0x4199d590,0x2918);m.map(PATTERN,0x3d0*4);m.map(OTHER,0x3d0*4);m.map(0x41342150,4)
 m.write(0x4199d590,4,OWNER)
 for off,val in [(0,0x534c4332),(4,2),(8,0xb70),(12,1)]:m.write(OWNER+0x14100+off,4,val)
 for j in range(128):m.write(POOL+j*72+68,4,POOL+(j+1)*72 if j<127 else 0)
 m.write(0x4199fea0,4,POOL);m.sr=0x2510
 return m

def fields(m,B,t,root,raw):m.write(B+t*0x3d0+0x3cb,1,root);m.write(B+t*0x3d0+0x3ce,1,raw)
# Capture across all raw scale values and tracks uses actual backing bytes.
for t in range(4):
 for raw in range(-1,35):
  m=machine();fields(m,PATTERN,t,60+t,raw);word=m.run(names['capture'],(PATTERN,t))
  check('capture root/scale from backing storage',word==(0x80000000|(60+t)|((raw+1)<<7)|(t<<13)) and m.sr==0x2510)
for why in ['busy','fault','null','bad_root','bad_scale','bad_track']:
 m=machine();fields(m,PATTERN,0,60,0);ptr=PATTERN;t=0
 if why=='busy':m.write(OWNER+0x14110,4,1)
 if why=='fault':m.write(OWNER+0x14114,4,1)
 if why=='null':ptr=0
 if why=='bad_root':fields(m,PATTERN,0,128,0)
 if why=='bad_scale':fields(m,PATTERN,0,60,35)
 if why=='bad_track':t=4
 check('invalid/busy capture falls back',m.run(names['capture'],(ptr,t))==0)
# Independent exhaustive nearest-note oracle uses extracted rows, not membership code.
scale_map=json.loads(pathlib.Path('outputs/Digitone-OS1.42-scale-map.json').read_text())


rows={x['raw_scale']:x['pitch_classes'] for x in scale_map['scales']}
def oracle(n,root,raw):return min((j for j in range(128) if (j-root)%12 in rows[raw]),key=lambda j:(abs(j-n),j))
m=machine();quant_cases=0
for root,notes in [(60,range(128)),(0,[0,1,6,61,126,127]),(11,[0,1,6,61,126,127]),(127,[0,1,6,61,126,127])]:
 for raw in range(-1,35):
  for n in notes:
   word=0x80000000|root|((raw+1)<<7)
   got=m.run(names['quantize'],(n,word));want=oracle(n,root,raw)
   check('instruction quantizer matches independent nearest-note oracle',got==want);quant_cases+=1
for word in [0,1,0x80008000,0x80001200,0xffffffff]:check('malformed quantizer context leaves coarse note unchanged',m.run(names['quantize'],(61,word))==61)
print('PASS',quant_cases,'instruction quantizer comparisons')
import copy
pipelines=[]
RANGES.extend([(0x400f07ac,0x400f0886),(0x4009dffa,0x4009e010)])
for t in range(4):
 m=machine();fields(m,PATTERN,t,60+t,0);fields(m,OTHER,t,62+t,0);m.write(0x41342150,4,OTHER)
 e=event(m);idx=(e-POOL)//72
 check('allocator clears recycled candidate',m.read(OWNER+0x14120+idx*4,4)==0)
 # Recovered producer boundary has a2=event, a3=B, d4=t.
 m.reg['a2']=e;m.reg['a3']=PATTERN;m.reg['d4']=t;m.reg['d0']=0;m.sr=0x2510
 before=copy.deepcopy(m);m.route(0x40093ef4,0x40093efc)
 overlay_enabled=False;before.route(0x40093ef4,0x40093efc);overlay_enabled=True
 word=m.read(OWNER+0x14120+idx*4,4)
 check('producer captures actual B rather than current global',word==(0x80000000|(60+t)|(1<<7)|(t<<13)))
 check('producer hook preserves stock registers and exact SR',m.reg==before.reg and m.sr==before.sr)
 check('producer hook preserves every event byte',all(m.mem[e+j]==before.mem[e+j] for j in range(72)))
 # Finish controlled note fields; this is not execution of the full producer.
 for off,val in [(4,1),(12,2),(20,1),(40,0),(44,SET),(52,0)]:m.write(e+off,4,val)
 m.write(e+24,1,64);m.write(SET+0x114,2,1);m.write(SET+0x116,1,2)
 fields(m,PATTERN,t,67+t,5) # later edit must not replace the captured word
 m.map(NODE,64*20)
 for j in range(64):m.write(NODE+j*20+16,4,NODE+(j+1)*20 if j<63 else 0)
 m.write(0x4199fe9c,4,NODE);CURRENT=0x2b000000;m.map(CURRENT,20)
 m.reg['a6']=0x30001800;m.reg['a3']=e;m.reg['a4']=CURRENT;m.reg['a5']=SET;m.reg['a2']=0x800034c4;m.reg['d2']=t
 m.write(0x80003fc4,4,-5)
 start=len(m.steps);m.route(0x4009dd80,0x4009ddb0);ident=m.reg['d0'];check('stock setup accepts captured source',ident!=0)
 m.route(0x4009ddb0,0x4009de50)
 # Continue actual stock selection and scheduling to the shared coarse boundary.
 m.route(0x4009de50,0x4009df9a)
 check('actual nonnegative selection reaches coarse hook',0x4009755e in m.steps[start:] and 0x4009de98 in m.steps[start:])
 pipelines.append((copy.deepcopy(m),e,t))
 coarse=m.reg['d6'];allocation=m.reg['d1'];expected=oracle(coarse,60+t,0);eventbytes=bytes(m.mem[e+j] for j in range(72));baseline=copy.deepcopy(m)
 m.route(0x4009df9a,0x4009dfa8)
 overlay_enabled=False;baseline.route(0x4009df9a,0x4009dfa8);overlay_enabled=True
 check('pitch hook reaches fixed point with expected constrained coarse',m.reg['d6']==expected<<16)
 check('pitch hook preserves allocation identity and event bytes',m.reg['d1']==allocation and bytes(m.mem[e+j] for j in range(72))==eventbytes)
 check('pitch hook matches all other stock registers, flags and stack',all(m.reg[r]==baseline.reg[r] for r in m.reg if r!='d6') and m.sr==baseline.sr)
 cases.append({'name':'sequencer boundary through actual acceptance/selection/pitch','track':t,'identity':ident,'captured_word':hex(word),'allocation_note':allocation,'coarse_before':coarse,'coarse_after':expected,'steps':len(m.steps)-start,'limits':'Producer entered at recovered finalization boundary; other note fields supplied; actual setup, selection, scheduler and note-loop instructions executed'})
print('PASS pipeline',len(cases),'tracks')


# Reader guard rejection uses actual RAM fields, not externally chosen branches.
base_machine,base_event,_=pipelines[0]
for why in ['type','release','track','no_arp','zero_identity','state_identity','empty_head','retained_type','retained_release','retained_track','retained_identity','retained_no_arp','metadata_busy','metadata_binding','metadata_identity','metadata_missing','metadata_corrupt','not_ready','null_owner']:
 m=copy.deepcopy(base_machine);e=base_event;rec=OWNER+0x14c30;ret=RETAINED
 changes={'type':(e,2),'release':(e+4,2),'track':(e+8,4),'no_arp':(e+40,0),'zero_identity':(e+64,0),'state_identity':(STATE+24,99),'empty_head':(0x41345620,0),'retained_type':(ret,2),'retained_release':(ret+4,2),'retained_track':(ret+8,1),'retained_identity':(ret+64,99),'retained_no_arp':(ret+40,0),'metadata_busy':(rec+8,1),'metadata_binding':(rec+12,0x80000001),'metadata_identity':(rec,99),'metadata_missing':(rec+4,0),'metadata_corrupt':(rec+4,0x80008000),'not_ready':(OWNER+0x1410c,0),'null_owner':(0x4199d590,0)}
 address,value=changes[why];m.write(address,4,value);sr=m.sr
 check('pitch guard rejects '+why,m.run(names['pitch'],(e,61))==61 and m.sr==sr)
m=copy.deepcopy(base_machine);m.write(base_event,4,1);m.write(RETAINED,4,1)
check('pitch reader admits cached synth type one',m.run(names['pitch'],(base_event,61))==60)
# Current pattern busy/fault affects new capture, not accepted context reads.
for off in [0x14110,0x14114]:
 m=copy.deepcopy(base_machine);m.write(OWNER+off,4,1)
 check('completed accepted snapshot survives capture unavailability',m.run(names['pitch'],(base_event,61))==60)
# Remapped incoming event context is not authoritative for continuing playback.
m,e,t=pipelines[1];m=copy.deepcopy(m);m.write(e+60,4,0);m.write(OWNER+0x14120+(e-POOL)//72*4,4,0x80000080)
check('destination retained snapshot wins over remapped incoming source',m.run(names['pitch'],(e,61))==61)
# Negative selection results execute real stock branches and never enter hook.
for kind in ['disabled_step','stale_identity']:
 m=copy.deepcopy(base_machine);e=base_event;start=len(m.steps)
 if kind=='disabled_step':m.write(SET+0x114,2,0);entry=0x4009de86;m.reg['d3']=m.read(e+64,4)
 else:m.write(e+64,4,99);entry=0x4009df4a
 m.route(entry,0x4009cef0)
 check('actual negative selection bypasses coarse hook',names['pitch_hook'] not in m.steps[start:] and m.read(e+20,4)==0)
 cases.append({'name':'actual negative selection bypass','kind':kind,'steps':len(m.steps)-start})
# Non-arp ordinary note hook is an exact no-op compared with stock.
m=copy.deepcopy(base_machine);e=base_event;m.write(e+40,4,0);m.reg['d6']=61;baseline=copy.deepcopy(m)
m.route(0x4009df9a,0x4009dfa8);overlay_enabled=False;baseline.route(0x4009df9a,0x4009dfa8);overlay_enabled=True
check('ordinary note hook exactly matches stock state',m.reg==baseline.reg and m.sr==baseline.sr)
# Recycle a slot that had valid context, proving actual allocation clears it.
m=machine();e=event(m);slot=OWNER+0x14120+(e-POOL)//72*4;m.write(slot,4,0x80000080);m.run(0x400f065c,(e,));again=event(m)
check('actual event reuse cannot inherit captured context',again==e and m.read(slot,4)==0)
# Empty pool returns zero while preserving stock ABI.
m.write(0x4199fea0,4,0);baseline=copy.deepcopy(m);got=m.run(0x400f0626);overlay_enabled=False;stock=baseline.run(0x400f0626);overlay_enabled=True
check('exhausted allocator wrapper preserves zero return and stock registers',got==stock==0 and m.reg==baseline.reg and m.sr==baseline.sr)
new_bodies={n:v for n,v in names.items() if v>=0x50010000}
extra=cursor-0x50010000;total=(RESIDENT_END-0x40241ca0)+extra
word_branches=sum(1 for addr,code in fixtures.items() for i in md.disasm(code,addr) if i.mnemonic.split('.')[0].startswith('b') and i.mnemonic.split('.')[0] not in ('btst','bclr','bset') and i.size==4)
result={'passed':len(checks),'checks':checks,'quantizer_comparisons':quant_cases,'pipeline_cases':cases,'new_fixture_disassembly':{n:{'address':hex(a),'size':len(fixtures[a]),'instructions':[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(fixtures[a],a)]} for n,a in new_bodies.items()},'layout':{'resident_bytes':RESIDENT_END-0x40241ca0,'additional_bytes':extra,'total_bytes':total,'available_resident_bytes':864,'shortfall_bytes':total-864,'optimistic_branch_only_total':total-2*word_branches,'additional_addresses':'Synthetic 50010000 onward; no physical ownership established'},'firmware_modified':False,'limits':['Sequencer producer entered at finalization boundary; full producer not executed','Queued descriptor and held-cache capture/copy hooks not connected by these instruction fixtures','Writer busy/fault fields supplied; full writer hook coverage not implemented','Stock arp selection and its negative branches execute; global asynchronous producer schedule not simulated','Normal stock byte narrowing remains; no new full-width overflow policy implemented here','Cold owner initialization is tested separately; caller fixtures provide initialized allocation/header','Custom CPU interpreter, not hardware or independently validated emulator','New bodies exceed current resident gap and execute only at synthetic addresses']}
pathlib.Path('outputs/Digitone-actual-capture-and-pitch-instruction-results.json').write_text(json.dumps(result,indent=2));print('PASS',len(checks),'checks; layout',result['layout'])
