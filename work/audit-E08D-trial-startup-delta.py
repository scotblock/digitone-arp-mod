"""Bounded E07-to-E08D startup/storage comparison; no physical claims."""
from pathlib import Path
import json,hashlib,struct
out=Path('outputs');read=lambda p:json.loads(Path(p).read_text())
d=read(out/'Digitone-E08D-PC-path-layout.json');e=read(out/'Digitone-E07-PC-candidate-layout.json')
payload=Path('work/os144/E08D-PC-layout-payload.bin').read_bytes()
old=Path('work/os144/E07-PC-payload.bin').read_bytes()
main=Path('work/os144/E08D-PC-layout-main.bin').read_bytes();oldmain=Path('work/os144/E07-PC-main.bin').read_bytes();MB=0x40000400;PB=0x47be0000
assert len(old)==18436 and len(payload)==32256
assert payload[:0x3bb2]==old[:0x3bb2]
assert payload[0x3bb8:len(old)]==old[0x3bb8:]
assert payload[0x3bb2:0x3bb8]==bytes.fromhex('4ef9')+struct.pack('>I',d['bootstrap'])
assert old[0x3bb2:0x3bb8]==bytes.fromhex('4ef940001df4')
assert main[0x40001df4-MB:0x40001f00-MB]==oldmain[0x40001df4-MB:0x40001f00-MB]
assert int.from_bytes(main[0x4029c4be-MB:0x4029c4c2-MB],'big')*4==len(payload)
assert main[d['copy_source']-MB:]==payload
assert PB+len(payload)<=0x47c00000
assert d['state']+344<=d['arena'] and d['arena']+64<=d['bootstrap']
loader=read(out/'Digitone-E08D-packed-loader.json')
assert loader['passed'] and loader['cache_controls']['0x2']=='0x8c000'
assert loader['cache_controls']['0x4']==loader['cache_controls']['0x5']=='0x0'
assert not int(loader['cache_controls']['0x2'],16)&0xa0000000
scope={};exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0],scope)
cf=scope['cfisa'];restriction=scope['move_restriction'];count=0
for r in d['regions']:
    data,base=(main,MB) if r['base']<PB else (payload,PB)
    code=data[r['base']-base:r['base']-base+r['bytes']];offset=0
    while offset<len(code):
        ins=cf.decode(lambda x:int.from_bytes(code[offset+x:offset+x+2],'big'),r['base']+offset)
        assert ins.length>0 and offset+ins.length<=len(code) and not ins.flags&(cf.ILLEGAL|cf.FPU|cf.LINEF) and not restriction(int.from_bytes(code[offset:offset+2],'big')),(r,offset)
        offset+=ins.length;count+=1
result={'PC_only':True,'passed':True,'firmware_changed':False,
    'E07_payload_bytes':len(old),'E08D_payload_bytes':len(payload),'additional_copy_bytes':len(payload)-len(old),
    'existing_E07_payload_unchanged_except_cold_success_jump':True,
    'stock_cache_handoff_bytes_unchanged':True,'loader_CACR':loader['cache_controls']['0x2'],
    'native_executable_regions_checked':len(d['regions']),'strict_ColdFire_instructions_checked':count,
    'reservation':['0x47be0000','0x47c00000'],'occupied_end':hex(PB+len(payload)),
    'unused_reservation_bytes':0x47c00000-(PB+len(payload)),
    'entry_stack_separation_bytes':0x48000000-(PB+len(payload)),
    'state_bytes':344,'arena_bytes':64,'state_to_arena_gap':d['arena']-(d['state']+344),
    'source_start':hex(d['copy_source']),'source_end':hex(d['copy_source']+len(payload)),
    'limits':['Being inside the existing reservation is bounded placement evidence, not proof of physical/exclusive ownership.',
              'Unchanged cache handoff plus a data-cache-disabled loader state supports the inherited installation route; silicon visibility and execution timing are not measured here.',
              'Warm copier replay, corrupted code/bus exceptions and unobserved DMA writers remain outside this check.']}
(out/'Digitone-E08D-trial-startup-delta.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
