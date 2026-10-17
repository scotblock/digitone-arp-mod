"""PC-only RAM placement evidence; no installation or firmware output."""
exec(open('work/test-actual-capture-and-pitch.py').read().split('# Capture across')[0])
import hashlib,zlib,lzma
anchors={0x40000554:'203ca50ce1004e7b0002',0x4000055e:'203c4007e0204e7b0004',0x400004ba:'207c40242000',0x400004c0:'223c431dc690',0x400dab98:'487941945eb8',0x400daba8:'4ab9401fe590',0x400dac10:'23c0401fe590'}
for addr,h in anchors.items():assert b[addr-base:addr-base+len(bytes.fromhex(h))].hex()==h
stock_end=base+len(b);clearlo,clearhi=0x40242000,0x431dc690
assert clearlo<=stock_end<stock_end+4096<=clearhi
code_offset=0x14c80;reserve=4096;request=code_offset+reserve
rounded=lambda n:1<<(max(16,n)-1).bit_length()
assert request==0x15c80 and rounded(request)==rounded(0x14c70)==0x20000
assert code_offset%16==0 and 0x14c70<=code_offset and code_offset+1678<=request
heaplo,heaphi=0x419a38c0,0x429a38c0
placements=range(heaplo,heaphi,0x20000)
assert all(p+request<=p+0x20000<=heaphi for p in placements)
cacr=0xa50ce100;acr=0x4007e020
fields={'DEC':cacr>>31&1,'DDCM':cacr>>25&3,'IEC':cacr>>15&1,'IDCM':cacr>>10&1,'SPA':cacr>>14&1,'DNFB':cacr>>13&1,'BEC':cacr>>19&1,'DDPI':cacr>>28&1,'IDPI':cacr>>12&1}
assert fields==dict(DEC=1,DDCM=2,IEC=1,IDCM=0,SPA=1,DNFB=1,BEC=1,DDPI=0,IDPI=0)
assert acr>>24==0x40 and (acr>>16&255)==7 and (acr>>15&1)==1 and (acr>>13&3)==3 and (acr>>5&3)==1
assert all((p>>24 & ~7)==0x40 for p in [heaplo,heaphi-1])
RANGES.extend([(0x40001a4c,0x40001ad0),(0x40001b6e,0x40001be0)])
m=create();m.map(0x41945eb8,32);m.map(0x429a39a8,4);m.write(0x429a39a8,4,0)
before=m.sr;sp=m.reg['a7'];acquire=m.run(0x40001a4c,(0x41945eb8,));split=len(m.steps)
assert acquire==1 and m.read(0x41945ebc,4)==0
release=m.run(0x40001b6e,(0x41945eb8,))
assert release==0 and m.sr&0xff00==before&0xff00 and m.reg['a7']==sp and 0x40001a9e not in m.steps and 0x40001bcc not in m.steps
blob=b''.join(code for addr,code in sorted(fixtures.items()) if addr>=0x40241ca0 and (addr<0x40242000 or 0x50010000<=addr<0x50020000))
assert len(blob)==1678
z=zlib.compress(blob,9);lz=lzma.compress(blob);assert zlib.decompress(z)==blob and lzma.decompress(lz)==blob
assert len(z)>864 and len(lz)>864
controls=[]
for p in range(0,len(b)-3,2):
 op=int.from_bytes(b[p:p+2],'big');sel=int.from_bytes(b[p+2:p+4],'big')&0xfff
 if op in [0x4e7a,0x4e7b] and sel in [2,4,5,6,7,12,13,14,15]:controls.append({'address':hex(base+p),'selector':hex(sel)})
assert controls==[{'address':'0x4000055a','selector':'0x2'},{'address':'0x40000564','selector':'0x4'}]
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
assert hashlib.sha256(syx.read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
assert hashlib.sha256(b).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
r={'read_only':True,'firmware_modified':False,'anchors':{hex(a):h for a,h in anchors.items()},'proposed_allocation':{'code_offset':hex(code_offset),'code_reserve':reserve,'explicit_request':hex(request),'calculated_rounded_block':'0x20000','placements_checked':len(placements),'allocator_execution':'not yet executed'},'source_lifetime':{'append_start':hex(stock_end),'startup_clear':[hex(clearlo),hex(clearhi)],'append_erased':True,'source_route_established':False},'cache_fields_under_MCF5441x_interpretation':fields,'control_scan':controls,'early_zero_context_mutex_execution':{'acquire_result':acquire,'release_result':release,'acquire_steps':split,'release_steps':len(m.steps)-split,'scheduler_trap_taken':False,'scope':'supplied zero lock/current-thread state; not full allocator or device execution'},'compression_screen':{'fixture_bytes':len(blob),'zlib_bytes':len(z),'lzma_bytes':len(lz),'existing_resident_capacity':864,'decompressor_overhead_not_included':True},'manual':'https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf','next_target':'Execute actual lazy allocator after startup clear, before scheduler creation; then audit an appended-source preservation/copy/erase route and loader bounds. No such hook is implemented.'}
pathlib.Path('outputs/Digitone-RAM-code-route-audit.json').write_text(json.dumps(r,indent=2))
print('PASS: RAM geometry, stock control anchors, 39 mutex instructions, compression round trips, and unchanged firmware hashes')
