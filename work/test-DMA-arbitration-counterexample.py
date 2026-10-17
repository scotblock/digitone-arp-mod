"""Counterexample for missing single-controller arbitration in existing model."""
import pathlib,json,struct
exec(pathlib.Path('work/test-timestamped-DMA-native.py').read_text().split('c.left=100000;')[0])
m.uc.mem_write(0xfc044000,struct.pack('>I',0xe406));m.uc.mem_write(0xfc044100,bytes(range(64)))
for number,src,dst,byte in [(42,0x40001000,0x40003000,b'A'),(47,0x40004000,0x40005000,b'B')]:
 ch=bank.channels[number];m.uc.mem_write(src,byte*12);count=0x8000|(number<<9)|3
 m.uc.mem_write(ch.tcd,struct.pack(edma_sw.TCD_FMT,src,0x0202,4,4,0,dst,count,4,0,count,0))
 ch._transfer(m.uc,False)
initial={str(n):hex(bank.channels[n]._u16(edma_sw.CSR)) for n in [42,47]}
# Service every cycle to avoid conflating this with delayed event service.
for cycle in range(1,101):c.cycles=cycle;t.service_payload()
assert bytes(m.uc.mem_read(0x40003000,12))==b'A'*12 and bytes(m.uc.mem_read(0x40005000,12))==b'B'*12
samples=t.report()['timestamped_payload']['samples'];first_read={x['channel']:x['due'] for x in samples if x['kind']=='read' and x['address'] in ['0x40001000','0x40004000']};first_write=next(x['due'] for x in samples if x['channel']==42 and x['kind']=='write')
assert all(int(v,16)&0x40 for v in initial.values())
assert first_read[47]<first_write
out={'scope':'Controlled diagnostic of current timestamped engine; not a validated hardware arbiter','CR':'0xe406','CSR_after_two_starts':initial,'first_read_cycles':first_read,'first_channel_first_write':first_write,'counterexample':'Channel 47 reads before channel 42 completes its first minor loop; both channels marked ACTIVE although ERCA=1 disables hardware preemption','payload_correct':True,'payload':t.report()['timestamped_payload'],'firmware_modified':False}
pathlib.Path('outputs/Digitone-DMA-arbitration-counterexample.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='payload'}))
