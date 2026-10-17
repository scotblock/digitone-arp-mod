"""Native inherited reset refusals with the complete E08C storage monitored.

These are stopped native entry calls with explicit admission fixtures, not
concurrent interrupts or a physical reset. No replacement code is installed.
"""
from pathlib import Path
source=Path('work/test-E08C-packaged-panel-playback.py').read_text().split('\ns = Session(')[0]
exec(compile(source,'E08C-reset-session-definitions','exec'))
from emu.harness import call
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_D0,UC_M68K_REG_PC

result={'PC_only':True,'cases':[],'helpers_host_loaded':False,
        'limits':['Native stopped entry calls use explicit admission-state fixtures and no asynchronous overlap.',
                  'Whole diagnostic entry remains deliberately disabled. Warm pool/setup entries must refuse before storage changes.',
                  'These checks do not certify unknown interior/computed bypasses, warm copier replay or physical reset behavior.']}
tests=[('diagnostic_'+hex(p),0x4009c6d0,[],p) for p in [0,0x434f4c44,0x494e4954,0x4c495645,0x4641494c]]
tests += [(name,pc,args,0x4c495645) for name,pc,args in [('warm_setup',0x4009d0d8,[]),
          ('pool_wrapper',0x4009c5a0,[]),('pool_initializer',0x400ffed0,[158]),('test_exit',0x4009d0ea,[])]]
for name,entry,args,admission in tests:
    session=None
    row={'name':name,'entry':hex(entry),'admission_fixture':hex(admission),'writes':[]}
    result['cases'].append(row)
    try:
        # The generic package installer only adapts decoded ISA and verifies
        # bytes. It neither writes helper code nor calls its initializer.
        session=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,on_machine=install)
        u=session.m.uc;stack=0x47fdff00;session.m.ensure(stack)
        u.mem_write(0x47be2840,struct.pack('>I',admission))
        spans=[(0x47be0000,len(payload)),(0x419ebe2c,9216),(0x419f0d70,8),
               (0x402a0e50,4),(0x40236788,4),(0x41392fa4,4)]
        fingerprint=lambda:hashlib.sha256(b''.join(bytes(u.mem_read(a,n)) for a,n in spans)).hexdigest()
        before=fingerprint()
        def written(u,access,a,n,value,d):
            row['writes'].append({'address':hex(a),'size':n,'value':value,'pc':hex(u.reg_read(UC_M68K_REG_PC))})
        for a,n in spans:u.hook_add(UC_HOOK_MEM_WRITE,written,begin=a,end=a+n-1)
        u.reg_write(UC_M68K_REG_D0,0x76543210)
        value=call(session.m,entry,args,stack_top=stack,limit=100000)
        assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and value==0x76543210
        assert not row['writes'] and fingerprint()==before
        row.update(passed=True,balanced_return=True,D0_preserved=True,
                   whole_payload_M1_state_and_arena_unchanged=True)
    except Exception:
        row.update(passed=False,failure=traceback.format_exc());print(row['failure'],flush=True)
    finally:
        if session:session.close()
    print(name,row.get('passed'),flush=True)
result['passed']=all(row['passed'] for row in result['cases'])
Path('outputs/Digitone-E08C-reset-refusal.json').write_text(json.dumps(result,indent=2))
if not result['passed']:raise SystemExit(1)
