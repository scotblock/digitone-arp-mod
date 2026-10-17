"""Synthetic hook machine-code fixtures only; stock image is read-only."""
exec(open('work/execute-identity-and-accepted-commit.py').read().split('for initial,want')[0])
F=0x50000000;AFTER=F+0x100;COMMIT=F+0x200;HELPER=F+0x300

def u32(x):return x.to_bytes(4,'big')
def preserve_call():
 # 64-byte scratch frame: 60 bytes d0-d7/a0-a6; SR word at +60.
 return bytes.fromhex('4fefffc048d77fff40c03f40003c')+bytes.fromhex('4eb9')+u32(HELPER)+bytes.fromhex('302f003c46c04cd77fff4fef0040')
fixtures={F:preserve_call()+bytes.fromhex('2ebc')+u32(AFTER)+bytes.fromhex('4ef9')+u32(0x4009719e),
 AFTER:preserve_call()+bytes.fromhex('4ef9')+u32(0x4009ddac),
 COMMIT:preserve_call()+bytes.fromhex('202b000841f941345ef8')+bytes.fromhex('4ef9')+u32(0x4009de50),
 HELPER:bytes.fromhex('203c12345678223c87654321207c11223344227c5566778846fc260f4e75')}
for a,code in fixtures.items():
 items=list(md.disasm(code,a));assert sum(i.size for i in items)==len(code) and all(i.id for i in items)

# Fetch fixtures in a separate synthetic address space, never alter b or its file.
def fixture_fetch(pc):
 for a,code in fixtures.items():
  if a<=pc<a+len(code):return code[pc-a:pc-a+16]
 return b[pc-base:pc-base+16]
RANGES.extend((a,a+len(code)) for a,code in fixtures.items())
src=source.replace('b[pc-base:pc-base+16]','fixture_fetch(pc)').replace('if pc==0xffffffff:break','if pc in (0xffffffff,0x4009ddac):break')
# For these fixtures the helper changes SR temporarily; full restoration is tested.
exec('if True:\n'+src);Machine.run=run
rtsrc=route_source.replace('b[pc-base:pc-base+16]','fixture_fetch(pc)')
exec('if True:\n'+rtsrc);Machine.route=route
checks=[];cases=[]

for initial,priority,note in [(False,2,60),(True,2,64),(True,1,64)]:
 m=create()
 if initial:setup_call(m)
 m.reg.update({f'd{i}':0x10101010+i for i in range(8)})
 m.reg.update({f'a{i}':0x20202020+i for i in range(7)})
 m.sr=0x2015;m.write(NOTES,1,note)
 metadata={'busy':False};helper_calls=[]
 def observe(pc):
  if pc!=HELPER:return
  retpc=m.read(m.reg['a7'],4);entry=F if retpc<F+0x100 else AFTER
  off=72 if entry==F else 68
  check('wrapper passes original track without extra-return displacement',m.read(m.reg['a7']+off,4)==0)
  if entry==F:metadata['busy']=True
  elif m.read(m.reg['a7']+4,4)==0:metadata['busy']=False
  helper_calls.append(entry)
 m.observe=observe
 before=m.reg.copy();ret=m.run(F,(0,1,NOTES,0,0,priority,SET,OUT,OUT+4))
 check('wrapped setup real result matches acceptance',bool(ret)==(not initial))
 check('zero result closes gate, accepted result holds gate',metadata['busy']==bool(ret))
 check('fixture preserves all original callee-saved registers',all(m.reg[r]==before[r] for r in [f'd{i}' for i in range(2,8)]+[f'a{i}' for i in range(2,7)]))
 check('fixture restores stack and original interrupt-mask bits',m.reg['a7']==before['a7'] and m.sr&0xff00==0x2000)
 check('before/after wrappers each execute helper once',helper_calls==[F,AFTER])
 cases.append({'name':'synthetic wrapper around actual setup','initial_active':initial,'priority':priority,'return':ret,'steps':len(m.steps),'helper_calls':[hex(x) for x in helper_calls]})

m=create();e=event(m);m.write(e+8,4,2);m.reg['a3']=e
m.reg.update({f'd{i}':0x11110000+i for i in range(8)})
m.reg['a0']=0x22220000;m.reg['a1']=0x33330000;m.reg['a6']=0x30001800;m.sr=0x251b
# Represents two pending arguments left by the stock retained-copy call.
m.put('-(a7)',4,e);m.put('-(a7)',4,RETAINED);before=m.reg.copy();sp=m.reg['a7'];saved_sr=m.sr
m.route(COMMIT,0x4009de50)
check('commit fixture preserves pending copy arguments and SP',m.reg['a7']==sp and m.read(sp,4)==RETAINED and m.read(sp+4,4)==e)
check('commit fixture replays displaced track load and array base',m.reg['d0']==2 and m.reg['a0']==0x41345ef8)
check('commit fixture preserves every other live register',all(m.reg[r]==v for r,v in before.items() if r not in ('d0','a0')))
# Displaced move.l of positive track sets N/Z/V/C to zero, retaining X and SR upper bits.
check('commit fixture matches displaced-instruction flags',m.sr==(saved_sr&~15))
cases.append({'name':'synthetic commit wrapper and displaced instruction replay','steps':len(m.steps),'pending_stack_bytes':8})
result={'passed':len(checks),'checks':checks,'cases':cases,'fixture_disassembly':{hex(a):[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(code,a)] for a,code in fixtures.items()},'limits':['Synthetic addresses are test fixtures, not executable space reserved in firmware','Metadata helper side effects are Python; helper machine code deliberately clobbers scratch registers/SR','No final guard/commit helper implementation or relocation performed','CPU interpreter not independently hardware validated']}
pathlib.Path('outputs/Digitone-hook-frame-fixture-results.json').write_text(json.dumps(result,indent=2));print('PASS',len(checks),'fixture checks')

