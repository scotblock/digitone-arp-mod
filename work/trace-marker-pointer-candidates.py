"""Conservative candidate discovery, not a globally verified code disassembly.

Linear decode is provisional. Constants are forgotten at branch boundaries;
computed stores and known bulk calls are retained for manual inspection.
Only exact constants are reported as numeric destinations. RAM loads stay
unknown; this pass cannot prove global absence of aliases.
"""
exec(open('work/disassemble.py').read().split('out=[]')[0])
import json
from capstone.m68k import *
md.skipdata=True
md.detail=True
items=list(md.disasm(b[:0x170000],base))
branches={'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs','bra','jmp'}
leaders=set()
def direct_target(i):
    if i.mnemonic.split('.')[0] not in branches|{'jsr','bsr'}:return None
    t=re.findall(r'\$([0-9a-f]+)',i.op_str)
    return int(t[0],16) if t else None
for i in items:
    if i.mnemonic.split('.')[0] in branches|{'jsr','bsr'}:
        t=direct_target(i)
        if t is not None:leaders.add(t)
        if i.mnemonic.split('.')[0] in branches:leaders.add(i.address+i.size)
bulk={0x400ec23c:'copy',0x400ec284:'clear',0x40128448:'bounded_string_copy',0x400ebc68:'zero_bytes',0x400f0954:'reverse_copy',0x400f09a4:'overlap_safe_copy',0x40102ae6:'copy_forwarding_alias'}
regs={};stack={};sp=0;history=[];calls=[];stores=[];computed=[]
def reset():
    global regs,stack,sp,history
    regs={};stack={};sp=0;history=[]
def ea(o):
    mode=o.address_mode
    if mode in {M68K_AM_ABSOLUTE_DATA_SHORT,M68K_AM_ABSOLUTE_DATA_LONG}:return o.mem.address&0xffffffff
    if mode==M68K_AM_PCI_DISP:return (cur.address+2+o.mem.disp)&0xffffffff
    if mode in {3,4,5,6,7,8}:
        r=o.mem.base_reg
        v=sp if r==M68K_REG_A7 else regs.get(r)
        if v is None:return None
        v+=o.mem.disp
        if o.mem.index_reg:
            iv=regs.get(o.mem.index_reg)
            if iv is None:return None
            # Word indices are signed 16-bit; long indices use the full word.
            if not o.mem.index_size:iv=((iv&0xffff)^0x8000)-0x8000
            v+=iv*(o.mem.scale or 1)
        return v&0xffffffff
    return None
def value(o):
    if o.type==M68K_OP_IMM:return o.imm&0xffffffff
    if o.type==M68K_OP_REG:return regs.get(o.reg)
    if o.type==M68K_OP_MEM and o.mem.base_reg==M68K_REG_A7:
        a=ea(o)
        return stack.get(a)
    return None
def regwrite(r,v):
    if v is None:regs.pop(r,None)
    else:regs[r]=v&0xffffffff
def write(o,v,size):
    global sp
    if o.type==M68K_OP_REG:
        if size!=4:regwrite(o.reg,None)
        else:regwrite(o.reg,v)
    elif o.type==M68K_OP_MEM:
        if o.address_mode==M68K_AM_REGI_ADDR_PRE_DEC and o.mem.base_reg==M68K_REG_A7:sp=(sp-size)&0xffffffff
        a=ea(o)
        if o.mem.base_reg==M68K_REG_A7 and a is not None:stack[a]=v
        if a is not None and 0x41995510<=a<0x419a5520:
            stores.append(dict(site=f'{cur.address:08x}',destination=f'{a:08x}',size=size,instruction=f'{cur.mnemonic} {cur.op_str}',overlaps_marker=a<0x4199d518 and a+size>0x4199d510,context=history[-12:]))
        if o.address_mode==M68K_AM_REGI_ADDR_POST_INC:regwrite(o.mem.base_reg,None)
for cur in items:
    if cur.address in leaders:reset()
    m=cur.mnemonic.split('.')[0]
    if cur.id==0:
        # Known unsupported ColdFire TST address-register instructions don't
        # alter registers; any other undecoded item ends this candidate trace.
        if bytes(cur.bytes) not in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)]:reset()
        continue
    ops=cur.operands
    size=4 if cur.mnemonic.endswith('.l') or m=='moveq' else 2 if cur.mnemonic.endswith('.w') else 1
    history.append(dict(address=f'{cur.address:08x}',bytes=bytes(cur.bytes).hex(),instruction=f'{cur.mnemonic} {cur.op_str}'))
    history=history[-32:]
    if m in {'jsr','bsr'}:
        t=direct_target(cur)
        if t is None and ops and ops[0].type==M68K_OP_MEM and ops[0].address_mode==3:t=regs.get(ops[0].mem.base_reg)
        if t in bulk:
            dest=stack.get(sp)
            count=stack.get((sp+(4 if t==0x400ebc68 else 8))&0xffffffff)
            status='unresolved_destination' if dest is None else 'unresolved_extent' if count is None else 'unresolved_wrapping_extent' if dest+count>0x100000000 else 'overlaps_marker' if dest<0x4199d518 and dest+count>0x4199d510 else 'constant_range_disjoint'
            calls.append(dict(site=f'{cur.address:08x}',target=f'{t:08x}',operation=bulk[t],destination=f'{dest:08x}' if dest is not None else None,count=count,status=status,context=history[-16:]))
        for r in [1,2,9,10]:regwrite(r,None)
        stack={}  # A called helper may mutate passed stack storage.
        continue
    if m in branches|{'rts','rte','rtr','link','unlk'}:reset();continue
    if m=='movem':
        # Conservatively forget register constants on register restoration.
        if ops and ops[-1].type==M68K_OP_REG_BITS:
            mask=ops[-1].register_bits
            for r in range(1,17):
                if mask&(1<<(r-1)):regwrite(r,None)
        continue
    if m in {'move','movea','moveq'} and len(ops)==2:
        v=value(ops[0])
        if ops[0].type==M68K_OP_MEM and ops[0].address_mode==4:
            if ops[0].mem.base_reg==16:sp=(sp+size)&0xffffffff
            else:regwrite(ops[0].mem.base_reg,None)
        if m=='movea' and size==2 and v is not None:v=((v&0xffff)^0x8000)-0x8000
        write(ops[1],v,4 if m in {'movea','moveq'} else size);continue
    if m=='lea' and len(ops)==2:
        v=ea(ops[0]);r=ops[1].reg
        if r==16 and ops[0].mem.base_reg==16 and ops[0].address_mode==6:sp=(sp+ops[0].mem.disp)&0xffffffff
        else:regwrite(r,v)
        if v is not None and 0x4199d50c<=v<0x4199d534:computed.append(dict(site=f'{cur.address:08x}',result=f'{v:08x}',instruction=f'{cur.mnemonic} {cur.op_str}',context=history[-12:]))
        continue
    if m=='pea' and len(ops)==1:
        sp=(sp-4)&0xffffffff;stack[sp]=ea(ops[0]);continue
    if m in {'clr','clra'} and ops:write(ops[0],0,size);continue
    if m in {'addi','addq','adda','add','subi','subq','suba','sub'} and len(ops)==2 and ops[-1].type==M68K_OP_REG:
        r=ops[-1].reg;v=value(ops[0]);old=sp if r==16 else regs.get(r)
        nv=None if old is None or v is None else (old-v if m.startswith('sub') else old+v)&0xffffffff
        if r==16:
            if nv is None:reset()
            else:sp=nv
        else:regwrite(r,nv)
        if nv is not None and 0x4199d50c<=nv<0x4199d534:computed.append(dict(site=f'{cur.address:08x}',result=f'{nv:08x}',instruction=f'{cur.mnemonic} {cur.op_str}',context=history[-12:]))
        continue
    if m in {'cmp','cmpi','cmpa','tst','btst','nop'}:continue
    # Unknown arithmetic cannot preserve a numeric pointer fact.
    if ops and ops[-1].type==M68K_OP_REG:regwrite(ops[-1].reg,None)
    elif ops and ops[-1].type==M68K_OP_MEM and m not in {'jmp'}:write(ops[-1],None,size)
    else:regs={}
result=dict(candidate_discovery_only=True,decode_end_exclusive=f'{base+0x170000:08x}',decoded_instruction_items=len(items),searched_targets={f'{a:08x}':n for a,n in bulk.items()},bulk_calls=calls,nearby_constant_stores=stores,computed_record_addresses=computed,limitations=['Linear code decoding may include data or misalignment','No propagation across branch joins','Mutable RAM pointer loads unresolved','Known callee ABI assumptions only','Six identified bulk routines plus one forwarding alias searched; inline loops and additional wrappers need separate bounds'])
pathlib.Path('work/marker-pointer-candidate-traces.json').write_text(json.dumps(result,indent=2))
from collections import Counter
print(json.dumps(dict(decoded_items=len(items),bulk_calls=len(calls),bulk_status=Counter(x['status'] for x in calls),nearby_stores=len(stores),overlapping_constant_stores=[x for x in stores if x['overlaps_marker']],computed_record_addresses=len(computed)),indent=2))
