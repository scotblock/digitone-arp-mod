import pathlib,sys,json,struct
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
exec(pathlib.Path('work/test-timestamped-DMA-native.py').read_text().split('c.left=100000;')[0])
ch=bank.channels[42];checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
def at(cycle):c.cycles=cycle;t.service_payload()
ch._transfer(m.uc,ensure=False)
check('launch leaves destination unchanged',bytes(m.uc.mem_read(0x40003000,64))==bytes(64))
check('launch leaves channel active and DONE clear',ch._u16(edma_sw.CSR)&0xc0==0x40)
at(1);m.uc.mem_write(0x40001000,b'A'*64)
at(4);m.uc.mem_write(0x40001000,b'B'*64)
at(19);check('destination hidden before first write beat',bytes(m.uc.mem_read(0x40003000,4))==bytes(4))
at(20);check('first read captured source at read time',bytes(m.uc.mem_read(0x40003000,4))==b'A'*4)
at(24);check('later read observes source mutation',bytes(m.uc.mem_read(0x40003004,4))==b'B'*4)
check('completion absent during partial visibility',42 in t.active and ch._u16(edma_sw.CSR)&0x80==0)
at(128);check('completion follows last write',42 not in t.active and ch._u16(edma_sw.CSR)&0xc0==0x80)
check('complete payload contains time-selected bytes',bytes(m.uc.mem_read(0x40003000,64))==b'A'*4+b'B'*60)
# A descriptor change before the timed scatter/gather read must be observed.
c.cycles=1000;t.bus.free=1000
first=struct.pack(edma_sw.TCD_FMT,0x40001000,0x0202,4,4,0,0x40004000,1,4,0x40007000,1,0x10)
nextdesc=lambda dst:struct.pack(edma_sw.TCD_FMT,0x40001004,0x0202,4,4,0,dst,1,4,0,1,0)
m.uc.mem_write(ch.tcd,first);m.uc.mem_write(0x40007000,nextdesc(0x40005000));ch._transfer(m.uc,False)
at(1008);m.uc.mem_write(0x40007000,nextdesc(0x40006000));at(1100)
check('scatter descriptor is read at scheduled time',bytes(m.uc.mem_read(0x40006000,4))==b'B'*4 and bytes(m.uc.mem_read(0x40005000,4))==bytes(4))
# Modulo source and unequal source/destination beat sizes.
c.cycles=2000;t.bus.free=2000
m.uc.mem_write(0x40008000,b'abcdefgh');m.uc.mem_write(ch.tcd,struct.pack(edma_sw.TCD_FMT,0x40008006,(3<<11)|2,1,4,0,0x40009000,2,4,0,2,0))
ch._transfer(m.uc,False);at(2200)
check('modulo wrap and unequal beat sizes',bytes(m.uc.mem_read(0x40009000,8))==b'ghabcdef')
check('all transfers drained',not t.active and not t.events)
r={'passed':len(checks),'checks':checks,'scope':'Controlled temporal visibility, source changes, completion, dynamic scatter/gather and modulo tests','payload':t.report()['timestamped_payload']}
pathlib.Path('outputs/Digitone-timestamped-DMA-visibility-checks.json').write_text(json.dumps(r,indent=2));print(json.dumps({'passed':len(checks),'checks':checks}))
