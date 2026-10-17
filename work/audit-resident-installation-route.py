"""Read-only evidence for the resident padding installation candidate."""
exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import hashlib,json
rawhash=hashlib.sha256(b).hexdigest();count=int.from_bytes(b[0x40241ab4-base:0x40241ab8-base],'big');table=0x40241ab8;end=table+count*4;start=0x40241ca0;limit=0x40242000
assert count==119 and end==0x40241c94
assert all(x==0 for x in b[end-base:limit-base])
# All byte alignments, literal addresses only; not a computed alias proof.
hits=[]
for p in range(len(b)-3):
 val=int.from_bytes(b[p:p+4],'big')
 if end<=val<limit:hits.append({'location':hex(base+p),'value':hex(val)})
anchors={0x4008c7d4:'47f940241ab8',0x4008c7dc:'243940241ab4',0x4008c7e2:'b48a670e',0x4000045e:'45f940242000',0x40000486:'45f9402478f0',0x400004ba:'207c40242000',0x400004c0:'223c431dc690',0x400f0504:'2f032f0241f94199dad8',0x400f05d0:'241f261f4e75',0x4009dda6:'4eb94009719e',0x4009de46:'202b000841f941345ef8'}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h
reader=[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[0x4008c7d4-base:0x4008c7f4-base],0x4008c7d4)]
clearlo=0x40242000;clearhi=0x431dc690
assert (clearhi-clearlo)%16==0 and start<clearlo
# Source range, cleared range and counted table cannot touch resident interval.
interval_checks={'startup_table_excludes_resident':end<=start,'initialized_data_sources_exclude_resident':limit<=0x40242000,'startup_clear_excludes_resident':limit<=clearlo,'original_main_section_contains_resident':base<=start<limit<=base+len(b)}
assert all(interval_checks.values())
r={'table_count':count,'table_start':hex(table),'table_end_exclusive':hex(end),'resident_start':hex(start),'resident_limit_exclusive':hex(limit),'guard_bytes_after_table':start-end,'resident_capacity':limit-start,'raw_literal_references_into_gap':hits,'anchors_verified':{hex(a):h for a,h in anchors.items()},'startup_table_reader':reader,'interval_checks':interval_checks,'clear_iterations':(clearhi-clearlo)//16,'route':'Reserve selected resident padding inside the existing main section; all instructions arrive with normal main-image loading, before stock cache initialization. Only metadata requires allocation. No runtime code copying or additional container section.','sha256_main':rawhash,'ownership_status':'bounded placement candidate supported by recovered table and startup ranges, not global computed-pointer exclusion','limits':['Runtime instruction-fetch/MMU/cache mapping not executed','No loader or hardware execution; image size/destination would remain the stock values if this placement were later implemented','No firmware patch or rebuild generated']}
pathlib.Path('outputs/Digitone-resident-installation-route-audit.json').write_text(json.dumps(r,indent=2));print('PASS',len(anchors),'anchors; resident gap',limit-start,'bytes; literal gap refs',len(hits))
