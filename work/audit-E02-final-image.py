from pathlib import Path
import sys,json,hashlib,struct,math
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from dt2.container import decode_syx,sections
from dt2.elz import depack_section
original=Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx');modified=Path('outputs/Digitone_OS1.44E02_SCALE_ARP_DIGIEMU_ONLY.syx');stock=Path('work/os144/section-3.bin').read_bytes();build=json.loads(Path('outputs/Digitone-OS1.44E02-build.json').read_text())
b=modified.read_bytes();stream=decode_syx(modified);n,check=struct.unpack_from('>II',stream);container=stream[8:8+n]
assert sum((i+1)^w[0] for i,w in enumerate(struct.iter_unpack('>I',container)))&0xffffffff==check
c,es=sections(modified);orig,oes=sections(original);entries={sid:(o,l,d) for sid,o,l,d in es};osids={sid:(o,l,d) for sid,o,l,d in oes}
o,l,d=entries[3];main=depack_section(c[o:o+l]);assert main==Path('work/os144/emulator-E02-main.bin').read_bytes()
assert all(c[o:o+l]==orig[osids[sid][0]:sum(osids[sid][:2])] for sid,(o,l,d) in entries.items() if sid!=3)
expected=bytearray(stock)
for h in build['changes']:
 offset=int(h['site'],16)-0x40000400;a=bytes.fromhex(h['original']);z=bytes.fromhex(h['patched']);assert expected[offset:offset+len(a)]==a;expected[offset:offset+len(z)]=z
assert main[:len(stock)]==expected
r={'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'modified_sha256':hashlib.sha256(b).hexdigest(),'main_sha256':hashlib.sha256(main).hexdigest(),'container_bytes':n,'syx_bytes':len(b),'main_bytes':len(main),'main_growth':len(main)-len(stock),'original_region_only_nine_documented_sites_changed':True,'all_other_sections_unchanged':True,'checksum_verified':True,'flash_arithmetic':{'os_start':hex(0x80000),'observed_stock_data_boundary':hex(0x380000),'nonoverlap_budget':0x300000,'oversize_bytes':n-0x300000,'program_end':hex(0x80000+math.ceil(n/512)*512),'erase_end':hex(0x80000+math.ceil(n/0x40000)*0x40000),'erase_units':math.ceil(n/0x40000),'program_blocks':math.ceil(n/512),'final_program_padding_needed':(-n)%512,'transport_padding_present':len(stream)-8-n},'memory':{'code_start':hex(0x47be0000),'code_end':hex(0x47be0000+2212),'private_pointer':hex(0x47be1000),'metadata_start':hex(0x47be1004),'metadata_end':hex(0x47be1004+0xb70),'metadata_bytes':0xb70,'occupied_span_bytes':0x1b74,'stock_startup_clear_start':hex(0x4028f000),'stock_startup_clear_end':hex(0x4322ae60),'global_ownership_proven':False}}
Path('outputs/Digitone-OS1.44E02-final-image-review.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
