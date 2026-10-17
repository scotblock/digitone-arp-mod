from pathlib import Path
import sys,json,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom
from dt2.elz import depack_section
handoff=bootrom.load_handoff('work/os144/E04-loader-handoff.bin')
writes={a:v for a,s,v in handoff['mmio'] if s==4 and 0xfc0b8000<=a<0xfc0b8100}
regs={n:writes[0xfc0b8000+n*4] for n in [4,7,8,12,15,16]}
addpins=(regs[15]>>24)&7;colsiz=(regs[16]>>24)&7
row_bits=16-addpins;column_bits=12-colsiz;banks=8 if regs[4]&0x100 else 4
reduc=(regs[8]>>24)&1;assert reduc==1
chip_enabled=bool(regs[12]&0x1000000);protection=bool(regs[7]&0x100)
capacity=(1<<row_bits)*(1<<column_bits)*banks
reservation=(0x47be0000,0x47c00000);offsets=tuple(a-0x40000000 for a in reservation)
assert capacity==0x08000000 and chip_enabled and not protection
assert 0<=offsets[0]<offsets[1]<=capacity
stock_boot=depack_section(bootrom.container_section('outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx',2))
mod_boot=depack_section(bootrom.container_section('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx',2))
assert stock_boot==mod_boot
r={'PC_only':True,'hardware_readback':False,'bootstrap_sections_equal':True,'bootstrap_decoded_sha256':hashlib.sha256(stock_boot).hexdigest(),
 'source':'guest DDR register writes retained in the previously traced exact E04 loader handoff; bootstrap byte-identical to stock',
 'register_writes':{f'CR{n:02d}':hex(v) for n,v in regs.items()},'decoded':{'ADDPINS':addpins,'row_bits':row_bits,'COLSIZ':colsiz,'column_bits':column_bits,'banks':banks,'datapath_bytes':1,'chip_enabled':chip_enabled,'range_protection_enabled':protection},
 'configured_capacity_bytes':capacity,'configured_capacity_MiB':capacity//1048576,'first_nonaliased_CPU_window':['0x40000000',hex(0x40000000+capacity)],
 'reservation':[hex(a) for a in reservation],'reservation_offsets':[hex(a) for a in offsets],
 'occupied_span':['0x47be0000','0x47be1b74'],'remaining_bytes_above_full_reservation':capacity-offsets[1],
 'fits_configured_window':True,'passed':True,
 'limits':['Decoded firmware configuration, not DRAM chip identification, board wiring measurement or physical RAM readback.','Fits address decoding does not mean exclusively owned or safe under all workloads.','BootHardware forces DDR initialization-complete status; no physical training/retention behavior is simulated.','Higher-address alias interpretation follows programmed contiguous geometry; no physical alias test.']}
Path('outputs/Digitone-E04-DDR-reservation-checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
