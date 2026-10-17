from pathlib import Path
import json,struct
START=0x47be2860;SIZE=400
payload=Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes();main=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes()
assert payload[START-0x47be0000:START-0x47be0000+SIZE]==bytes(SIZE)
source=0x4029c5b0+START-0x47be0000
assert main[source-0x40000400:source-0x40000400+SIZE]==bytes(SIZE)
regions=[('context',0x47be1000,0xb74),('sidecar_pending',0x47be2000,2080),('admission',0x47be2840,4),('capture_code',0x47be3000,474),('reset_code',0x47be3400,304),('atomic_copy_code',0x47be3600,182)]
assert all(not (a<START+SIZE and START<a+n) for _,a,n in regions)
hits=[]
for name,path in [('stock_main','work/os144/section-3.bin'),('custom_main','work/os144/PC_ONLY-atomic-storage-main.bin'),('custom_payload','work/os144/PC_ONLY-atomic-storage-payload.bin')]:
 d=Path(path).read_bytes();found=[]
 for p in range(0,len(d)-3,2):
  v=int.from_bytes(d[p:p+4],'big')
  if 0x40000000<=v<0x80000000 and START<=0x40000000+(v-0x40000000)%0x08000000<START+SIZE:found.append({'offset':hex(p),'literal':hex(v)})
 hits.append({'image':name,'aligned_word_candidates':found})
Path('outputs/Digitone-E04-PC-deferred-storage-screen.json').write_text(json.dumps({'PC_only':True,'candidate':hex(START),'end':hex(START+SIZE),'bytes':SIZE,'payload_and_native_copy_source_zero':True,'source':hex(source),'known_layout_regions_disjoint':True,'literal_screen':hits,'heap_config':json.loads(Path('outputs/Digitone-OS1.44-heap-bounds-checks.json').read_text())['initial_globals'],'limits':['Scanning even-offset words is a candidate literal screen, not computed-write or complete instruction reachability proof.','Non-overlap with known allocations does not certify global or physical reserved-RAM ownership.']},indent=2));print('PASS candidate padding, source and layout; literal hit counts',[(x['image'],len(x['aligned_word_candidates'])) for x in hits])
s=Path('work/build-PC-deferred-release-overlay.py').read_text().replace('COUNT=0x47fa2000','COUNT=0x47be2860').replace('PC_ONLY-deferred-release-overlay','PC_ONLY-resident-deferred-release-overlay').replace('New RAM is fixture-only and zeroed by test installation, not owned/initialized through a packaged boot path.','Queue occupies existing payload zero padding; native copier initialization is under PC test. Exclusive RAM ownership and packaged delivery remain unverified.')
exec(compile(s,'resident-deferred-release-builder','exec'))
