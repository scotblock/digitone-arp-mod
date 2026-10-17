exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json,hashlib
anchors={0x400efa90:'296a00280038',0x400efab8:'4294',0x400efbe0:'4e95',0x400efc08:'4e95',0x400efc2a:'4eb9400ec23c',0x400efc3e:'4ef9400f0886',0x400f0886:'4feffff4',0x400f08aa:'21420044',0x400f08f0:'4fefffe8',0x400f0908:'42b94199fe94',0x400f0910:'4bfafd4a',0x400f0914:'4dfafdbe',0x400f0924:'242b0044',0x400f092e:'4e94',0x400f0934:'4e95',0x400f0942:'4e96',0x4009bd6a:'487afd28',0x4009bd6e:'4eb9400f08f0',0x4009bd7c:'4eb94009713c',0x4009bd84:'4ef9400ef9d0',0x40094858:'48781410',0x40094872:'23c2419a38a4',0x40094880:'41e80504',0x40094884:'23c8419a38a8',0x4009488e:'23c8419a38ac',0x40094894:'23c2419a38b0',0x400ec2c8:'202f0004',0x400ec2cc:'4e75',0x400f059e:'20394199d590',0x4009afdc:'307b1a06',0x4009afe0:'4efb8802',0x4009afd6:'b881',0x4009afd8:'650001b2'}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),h)
switchbase=0x4009afe4
switchtargets=[switchbase+struct.unpack_from('>h',b,switchbase-base+slot*2)[0] for slot in range(5)]
assert 0x4009bde8 not in switchtargets
# Validate that the bitmap/arp reset after queue drain contains no retained
# template references and no call instructions in its confirmed linear body.
reset=list(md.disasm(b[0x4009713c-base:0x4009719e-base],0x4009713c))
assert reset[-1].mnemonic=='rts'
assert not any(x.mnemonic.split('.')[0] in ('jsr','bsr','jmp') for x in reset)
assert not any('41345f' in x.op_str for x in reset)
checks=[]
def check(name,c):assert c,name;checks.append(name)
# Ownership examples explain why a raw copy needs a source contract. These
# are constructed specifications, never claims about a live firmware bug.
ref=1;queued=1;borrowed_cache=1
check('borrowed cache does not own reference',ref==queued)
queued=0;ref-=1
check('transfer consumes one reference exactly once',ref==0)
ref=1;queued=2
check('duplicating owning source without retain undercounts',ref<queued)
ref+=1
check('retaining second owner restores balance',ref==queued)
ref=2;queueowners=1;templateowners=1
ref-=queueowners;queueowners=0
check('draining queue leaves retained template live',ref==templateowners==1)
check('empty queue is insufficient reset precondition',queueowners==0 and ref>0)
# Proposed cold-init publication protocol at every intermediate step. Null
# allocation halts pool setup; it cannot merely omit a feature on top of a
# missing stock-required pool.
states=[];owner=None;ready=False;allocated=False;cleared=False;linked=False
for phase in ['before_allocation','allocated','cleared','linked','trailer_initialized','published']:
 if phase=='allocated':allocated=True
 if phase=='cleared':cleared=True
 if phase=='linked':linked=True
 if phase=='trailer_initialized':ready=True
 if phase=='published':owner=0x419a38c0
 accessible=owner is not None and ready
 assert not accessible or (allocated and cleared and linked)
 states.append(dict(phase=phase,owner_visible=owner is not None,capture_allowed=accessible))
check('every cold-init prefix hides incomplete storage',all(not x['capture_allowed'] for x in states[:-1]))
check('final owner publication enables initialized storage',states[-1]['capture_allowed'])
check('null allocation cannot publish owner',None is None)
check('clear returns local pointer for delayed publication',anchors[0x400ec2c8]=='202f0004')
check('four-record auxiliary allocation distinct from 64-record pool',4*0x504==0x1410 and 64*0x504==0x14100)
source=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(source.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
r=dict(read_only=True,firmware_modified=False,verified_anchors={hex(a):h for a,h in anchors.items()},nearby_signed_word_switch=dict(base=hex(switchbase),selectors=5,targets=[hex(x) for x in switchtargets],reset_entry_excluded=True),raw_event_copies=dict(sites=['400efbe0','400efc08','400efc2a'],payload_source='descriptor+28 -> cached event+38',common_publication='400f0886',reference_retain_at_publication=False,ownership_contract='Unresolved borrowed-source or transfer semantics; no runtime defect demonstrated'),queue_drain=dict(entry='400f08f0',caller='4009bd6e',normal_release='400f065c',callback='4009ba94',callback_handles='event type 3 through 400e42ec',retained_template_release_proven=False),auxiliary_pool=dict(allocation='4009485c',owner_pointer_table='419a38a4..419a38b4',bytes=0x1410,records=4,stride=0x504,separate_from_payload_pool=True),proposed_cold_init_states=states,specification_checks=checks,model_limit='Specification examples only; not execution of the actual firmware or its callbacks',remaining=['Establish owning/borrowed source lifetime for raw copies and cache+38','Validate exact cold-init control-flow split to bypass global reload on first allocation','Select allocation failure continuation that prevents missing-pool use','Second setup route still lacks a complete computed-entry reachability proof'],unchanged_sha256=dict(syx=hashes[0],decoded_section_3=hashes[1]))
pathlib.Path('outputs/Digitone-payload-publication-followup-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(anchors=len(anchors),spec_checks=len(checks),switchtargets=[hex(x) for x in switchtargets],hashes_unchanged=True),indent=2))
