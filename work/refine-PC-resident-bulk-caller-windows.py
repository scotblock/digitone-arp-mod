from pathlib import Path
import json,sys
sys.path.insert(0,'work/emulator-deps')
from capstone import *
p=Path('outputs/Digitone-E04-PC-resident-bulk-caller-windows.json');r=json.loads(p.read_text());d=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
r['windows']=[w for w in r['windows'] if w['instructions']]
for start,n in [(0x4009bfe4,28),(0x4001d66e,34),(0x4018ab70,52)]:
 r['windows'].append({'start':hex(start),'instructions':[{'pc':hex(i.address),'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str} for i in cs.disasm(d[start-base:start-base+n],start)]})
r['bounded_conclusions']=[{'caller_return':'0x4009bff8','fixed_size':1184,'observed_destination_class':'SRAM, not DDR alias of queue','universal_base_pointer_proven':False},{'caller_return':'0x4000a4b8','fixed_size':304,'destination_expression':'A2+0x2df6','universal_A2_proven':False},{'caller_return':'0x4000a4a6','fixed_size':218,'destination_expression':'A2+0x2f26','universal_A2_proven':False},{'caller_return':'0x4001d68a','fixed_size':12,'destination_origin':'Return D0 of malloc wrapper400e96c0 requested for12bytes; copied12bytes immediately','queue_excluded_if_intact_allocator_bounds':True},{'caller_return':'0x4018ab94','observed_max_size':29,'observed_destination_class':'Primary heap buffer area','all_incoming_paths_data_flow_resolved':False}];p.write_text(json.dumps(r,indent=2))
