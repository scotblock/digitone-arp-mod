"""Read-only shutdown workload/clock accounting; no physical timing claim."""
from pathlib import Path
import json,hashlib,sys,zlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.snapshot import _load_blob
from emu.harness import PAGE
r=json.loads(Path('outputs/Digitone-E10-PC-auto-powerfail.json').read_text());assert r['passed']
c=json.loads(Path('work/os144/PC_ONLY-E10-life-layout.json').read_text())
main=Path('work/os144/PC_ONLY-E10-life-main.bin').read_bytes();stock=Path('work/os144/section-3.bin').read_bytes();base=0x40000400
assert hashlib.sha256(main).hexdigest()==c['main_sha256']
lo,hi=0x400a7a6c,0x400a8452;assert main[lo-base:hi-base]==stock[lo-base:hi-base]
assert main[0x400a7eb4-base:0x400a7eba-base].hex()=='247c002a7514'
assert main[0x400a8080-base:0x400a8088-base].hex()=='708013c0ec090000'
image_bytes=0x2a7514;chunk=0x8000;n=(image_bytes+chunk-1)//chunk
assert n==85 and len(r['commands'])==86 and all(x['bytes']==chunk for x in r['commands'])
new_bytes=n*chunk;write_bytes=sum(x['bytes'] for x in r['commands']);read_bytes=chunk
# The native invalidation path reads the old header's entire bounce buffer.
assert main[0x400a7f28-base:0x400a7f2e-base].hex()=='23c1fc045760'
boot=json.loads(Path('outputs/Digitone-E10-PC-powergood-startup.json').read_text());b=_load_blob(boot['cases'][0]['ui_snapshot']);pages={a:zlib.decompress(v) for a,v in b['pages'].items()}
def rd(a,n):return int.from_bytes(bytes(pages.get((a+i)&~(PAGE-1),bytes(PAGE))[(a+i)&(PAGE-1)] for i in range(n)),'big')
proctl=rd(0xfc0cc028,4);sysctl=rd(0xfc0cc02c,4);misccr=rd(0xec09000e,2)
assert (proctl>>1)&3==1
prescale=(sysctl>>8)&255;dvs=((sysctl>>4)&15)+1
assert prescale==1 and dvs==1 and not misccr&0x40
card_divisor=prescale*2*dvs;width=4;total=write_bytes+read_bytes
scenarios=[dict(card_clock_hz=f,oscillator_hz_if_captured_source=f*card_divisor,payload_only_lower_bound_ms=total*8/(width*f)*1000) for f in [10_000_000,12_500_000,20_000_000,25_000_000]]
out=dict(PC_only=True,analysis_completed=True,firmware_modified=False,device_opened=False,hold_up_time_verified=False,shutdown_time_upper_bound_verified=False,stock_shutdown_code_byte_identical=True,retained_image_bytes=image_bytes,chunk_bytes=chunk,new_image_commands=n,new_image_wire_bytes=new_bytes,native_final_padding_bytes=new_bytes-image_bytes,old_bank_invalidation_write_bytes=chunk,old_bank_header_read_bytes=read_bytes,total_write_bytes=write_bytes,total_payload_wire_bytes=total,additional_E10_shutdown_commands=0,additional_E10_shutdown_wire_bytes=0,captured_model_registers=dict(PROCTL=hex(proctl),SYSCTL=hex(sysctl),MISCCR=hex(misccr)),captured_bus_width=width,captured_source='oscillator output selected; physical frequency unknown',captured_card_clock_divisor=card_divisor,conditional_scenarios=scenarios,actual_card_clock_hz=None,actual_shutdown_ms=None,measured_hold_up_ms=None,physical_safety_margin_ms=None,post_cache_terminal_write='0x80 to RCR 0xec090000 requests software reset; it does not establish a power-hold latch',assurance_limits=['Payload-only lower bounds exclude command/CRC overhead, CPU copies, input/interrupt latency, data-cache/memory timing, eMMC programming/busy time and durability. They are not required hold-up budgets or measured shutdown times.','E10 stores records in existing serialized slots; the shutdown writer has the same fixed count. Equal volume does not prove equal physical timing. Edge-sensitive level-7 requests are nonmaskable; IPL 7 alone does not protect custom updates from that input. The level-5 callback handoff and interrupted-update behavior need separate coverage.','Only captured PC register values are decoded; hardware bootstrap oscillator/source/divider state is not measured. No capacitance, rail current, minimum voltage or signal threshold is known.','Without opening/measuring the unit or obtaining authoritative board hold-up specifications, the available evidence cannot establish a positive physical margin. LEDs/audio stopping do not observe internal eMMC write completion.'],references=['https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=236','https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=635','https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=637','https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=261'])
Path('outputs/Digitone-E10-PC-hold-up-budget.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Unchanged shutdown workload:',n+1,'writes;',total,'payload bytes including old-bank read.')
for row in scenarios:print(row['card_clock_hz'],'Hz: payload-only minimum',round(row['payload_only_lower_bound_ms'],3),'ms (conditional, not measured)')
print('Physical hold-up and safety margin remain unknown.')
