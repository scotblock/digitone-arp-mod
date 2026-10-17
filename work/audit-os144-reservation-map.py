from pathlib import Path
exec(Path('work/audit-E02-startup-failure.py').read_text().split('\ntry:\n for mode')[0])
stock=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;m=machine()
def read(a):return int.from_bytes(m.uc.mem_read(a,4),'big')
heap={hex(a):hex(read(a)) for a in [0x40240058,0x4024005c,0x40240060,0x40240064,0x40240068,0x4024006c,0x40240070]}
hits=[];task_sites=[]
for p in range(0,len(stock)-4,2):
 value=int.from_bytes(stock[p:p+4],'big')
 if 0x40000000<=value<0x80000000:
  canonical=0x40000000+(value-0x40000000)%0x08000000
  if RAM<=canonical<0x47c00000:hits.append({'word_location':hex(base+p),'value':hex(value),'canonical':hex(canonical)})
 if stock[p:p+6]==bytes.fromhex('4eb94000170c'):task_sites.append({'call_site':hex(base+p),'preceding_48_bytes':stock[max(0,p-48):p].hex()})
r={'PC_only':True,'stock_SHA256':hashlib.sha256(stock).hexdigest(),'startup_clear':[hex(0x4028f000),hex(0x4322ae60)],'startup_stack_top':hex(0x48000000),'reservation':[hex(RAM),hex(0x47c00000)],'occupied_end':hex(BSS+0xb70),'occupied_bytes':BSS+0xb70-RAM,'clear_does_not_overlap':0x4322ae60<RAM,'separation_from_reservation_end_to_entry_stack_top':0x400000,'snapshot_A7':hex(m.uc.reg_read(UC_M68K_REG_A7)),'heap_globals_in_stopped_capture':heap,'aligned_word_alias_matches':hits,'literal_task_constructor_calls':task_sites,'limits':['Clear/entry stack values checked in stock 1.44 instructions. Stopped capture is a bounded observation, not worst-case stack/heap use.','Raw aligned word search includes data and misses computed pointers; zero matches cannot certify ownership.','Constructor records are literal calls only; computed/relative/wrapper calls remain outside this inventory. No DMA coverage added.']}
Path('outputs/Digitone-OS1.44-reservation-map-checks.json').write_text(json.dumps(r,indent=2));print('reservation alias matches',len(hits),'literal constructor calls',len(task_sites));print('heap globals',heap)
