"""Unchanged allocator/memcpy/memset in a sparse, post-clear PC fixture."""
exec(open('work/try-full-early-allocator.py').read().split('m=AllocMachine();')[0])
import json,hashlib
RANGES.extend([(0x400ec23c,0x400ec2f0)])
heaplo,heaphi=0x419a38c0,0x429a38c0
def cold():
 m=AllocMachine();m.sr=0x2700;m.map(0x30000000,0x4000);m.map(0x401fe590,0x20)
 for j in range(0x20):m.write(0x401fe590+j,1,b[0x401fe590-base+j])
 return m
checks=[];cases=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
for request in [0x14c70,0x15c80]:
 m=cold();sp=m.reg['a7'];result=m.run(0x400dab8c,(request,));steps=len(m.steps)
 check(f'{request:x} actual cold allocation returns heap base',result==heaplo)
 check(f'{request:x} actual initialization flag published',m.read(0x401fe590,4)==1)
 bitmap_index=0x20000//16-1
 check(f'{request:x} actual bitmap marks 128KB block end',bool(m.read(0x41925eb8+bitmap_index//8,1)&(1<<(bitmap_index%8))))
 check(f'{request:x} startup current-thread pointer remains zero',m.read(0x429a39a8,4)==0)
 check(f'{request:x} no scheduler trap or allocator stub',not any(pc in m.steps for pc in [0x40001a9e,0x40001bcc,0x400dae08,0x400dae14]))
 second=m.run(0x400dab8c,(request,))
 check(f'{request:x} warm allocation is next nonoverlapping block',second==heaplo+0x20000)
 check(f'{request:x} allocation-call counter equals two',m.read(0x401fe5a8,4)==2)
 check(f'{request:x} actual allocator writes exclude appended staging',all(a+n<=base+len(b) or a>=base+len(b)+4096 for a,n,v in m.writes))
 check(f'{request:x} stack and interrupt mask preserved',m.reg['a7']==sp and m.sr&0xff00==0x2700)
 cases.append({'request':hex(request),'first':hex(result),'second':hex(second),'cold_instructions':steps,'warm_instructions':len(m.steps)-steps})
m=cold();whole=m.run(0x400dab8c,(0x1000000,));before=len(m.steps);failed=m.run(0x400dab8c,(0x15c80,))
check('whole heap stock allocation succeeds',whole==heaplo)
check('stock allocator returns null on subsequent exhaustion',failed==0)
check('stock allocation-call counter includes exhausted attempt',m.read(0x401fe5a8,4)==2)
cases.append({'name':'full heap then enlarged request','whole_heap_pointer':hex(whole),'failed_pointer':failed,'failure_instructions':len(m.steps)-before})
# Source is synthetic RAM fixture data; bytes are never appended to firmware.
source=base+len(b);stagebytes=0x1000;copies=[]
for length in [0,15,16,17,1678,4096]:
 m=cold();owner=m.run(0x400dab8c,(0x15c80,));dest=owner+0x14c80
 m.map(source-16,stagebytes+32)
 payload=bytes((j*73+19)&255 for j in range(stagebytes))
 for j,value in enumerate(payload):m.write(source+j,1,value)
 for a in [dest-1,dest+length,source-1,source+stagebytes]:m.write(a,1,0xa5)
 start=len(m.steps);ret=m.run(0x400ec23c,(dest,source,length))
 check(f'copy {length}: actual stock memcpy returns destination',ret==dest)
 check(f'copy {length}: exact bytes copied',bytes(m.read(dest+j,1) for j in range(length))==payload[:length])
 check(f'copy {length}: destination guards preserved',m.read(dest-1,1)==0xa5 and m.read(dest+length,1)==0xa5)
 check(f'copy {length}: source remains intact',bytes(m.read(source+j,1) for j in range(stagebytes))==payload)
 copied_steps=len(m.steps)-start;start=len(m.steps)
 m.run(0x400ec284,(source,0,stagebytes))
 check(f'copy {length}: actual stock memset restores staging zeroes',all(m.read(source+j,1)==0 for j in range(stagebytes)))
 check(f'copy {length}: source erase excludes guards',m.read(source-1,1)==0xa5 and m.read(source+stagebytes,1)==0xa5)
 check(f'copy {length}: erased source does not change destination',bytes(m.read(dest+j,1) for j in range(length))==payload[:length])
 copies.append({'bytes':length,'destination':hex(dest),'copy_instructions':copied_steps,'source_erase_instructions':len(m.steps)-start})
# Audit the existing loop's write footprint, rather than executing millions of stores.
clearlo,clearhi=0x40242000,0x431dc690
check('staging interval has 16-byte aligned boundaries',source%16==0 and (source+stagebytes)%16==0)
check('stock startup clear covers every staging byte',clearlo<=source<source+stagebytes<=clearhi)
partitions=[(clearlo,source),(source,source+stagebytes),(source+stagebytes,clearhi)]
check('preserve-then-erase partitions reconstruct exact stock clear',all(lo%16==0 and hi%16==0 for lo,hi in partitions) and sum(hi-lo for lo,hi in partitions)==clearhi-clearlo)
boot=pathlib.Path('work/section-2.bin').read_bytes();bootbase=0x02000800
for addr,h in [(0x02000a92,'203c0008c0004e7b0002'),(0x0200783a,'203c000cc1004e7b0002'),(0x40000554,'203ca50ce1004e7b0002')]:
 data,start=(b,base) if addr>=base else (boot,bootbase)
 check(f'cache handoff anchor {addr:x}',data[addr-start:addr-start+len(bytes.fromhex(h))].hex()==h)
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
check('original SysEx unchanged',hashlib.sha256(syx.read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
check('decoded image unchanged',hashlib.sha256(b).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
r={'firmware_modified':False,'checks':checks,'allocator_cases':cases,'copy_cases':copies,'stage':{'start':hex(source),'end_exclusive':hex(source+stagebytes),'bytes':stagebytes,'original_clear_partitions':[[hex(lo),hex(hi)] for lo,hi in partitions]},'execution_scope':'Actual stock allocator and dependencies, memcpy and memset. Sparse post-clear RAM fixture, supervisor SR=2700, zero current-thread pointer. No heap-return substitution; no hardware or cache emulation. Copy bytes are synthetic; source preservation itself is an interval audit, not an installed hook.','remaining':['actual loader acceptance and bounds for extended main payload','resident bootstrap fit and callable route','execute proposed split-clear/bootstrap ordering','relocation and full relocated helper behavior','cold handoff cache/ACR state and alternate entry paths','failure fallback and owner/readiness publication']}
pathlib.Path('outputs/Digitone-early-allocator-and-source-copy-results.json').write_text(json.dumps(r,indent=2))
print('PASS',len(checks),'checks;',len(cases),'allocator cases;',len(copies),'stock copy/erase cases; firmware unchanged')
