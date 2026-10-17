from pathlib import Path
exec(Path('work/test-E06-degree-contracts.py').read_text().split('count=0;examples=[]')[0])
count=0
for raw in range(35):
 for root in [0,60,127]:
  word=0x80000000|root|((raw+1)<<7)
  for base in [0,60,127]:
   for offset in range(-128,128):
    expected=oracle(base,offset,0,word);got=signed(call(m,cfg['degree_address'],[base+offset,word,base,offset,0],stack_top=STACK,limit=20000))
    assert got==expected,(raw,root,base,offset,got,expected);count+=1
e5=Path('work/os144/E05-PC-main.bin').read_bytes();e6=Path('work/os144/E06-PC-main.bin').read_bytes();p5=Path('work/os144/E05-PC-payload.bin').read_bytes();p6=Path('work/os144/E06-PC-payload.bin').read_bytes()
allowed=[(0xa00,0xa00+cfg['degree_bytes']),(0xc00,0xc00+cfg['degree_hook_bytes']),(0xd00,0xf30)]
assert len(e5)==len(e6) and len(p5)==len(p6)
changed=[i for i,(a,b) in enumerate(zip(p5,p6)) if a!=b];assert all(any(lo<=i<hi for lo,hi in allowed) for i in changed)
source=0x4029c5b0-0x40000400;site=0x40098116-0x40000400
main_changes=[i for i,(a,b) in enumerate(zip(e5,e6)) if a!=b];assert all(site<=i<site+8 or any(source+lo<=i<source+hi for lo,hi in allowed) for i in main_changes)
assert hashlib.sha256(Path('outputs/Digitone_OS1.44E05_SCALE_ARP_PC_ONLY.syx').read_bytes()).hexdigest()=='17fbe13d6b2aad9c096df7ac20fd4499a7bb0951e146fd0fd0aaeace4037e474'
out={'passed':True,'signed_byte_offset_cases':count,'only_intended_hook_and_padding_bytes_changed':True,'same_main_and_payload_lengths':True,'E05_preserved':True,'changed_MAIN_bytes':len(main_changes),'changed_payload_bytes':len(changed)}
Path('outputs/Digitone-E06-boundaries-and-preservation.json').write_text(json.dumps(out,indent=2));print('PASS signed-byte boundary cases',count,'and exact E05 change boundary')
