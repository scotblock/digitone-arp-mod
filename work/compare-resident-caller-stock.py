p='work/test-resident-caller-helpers.py';s=open(p).read()
s=s.replace('def fetch(pc):\n for addr',"overlay_enabled=True\ndef fetch(pc):\n if not overlay_enabled:return b[pc-base:pc-base+16]\n for addr")
s=s.replace('from', 'from', 0)
s=s.replace('oldid),(4,oldword),(8,0),(12,0x80000000)', 'oldid),(4,oldword),(8,0),(12,0x80000000|track)')
s=s.replace('m.read(REC+12,4)==0x80000000','m.read(REC+12,4)==(0x80000000|track)')
s=s.replace('before=m.reg.copy();initialsp=', 'import copy\n baseline=copy.deepcopy(m)\n before=m.reg.copy();initialsp=')
s=s.replace(" replay={'d0':m.reg['d0'],'a0':m.reg['a0']}", """ replay={'d0':m.reg['d0'],'a0':m.reg['a0']}
 overlay_enabled=False;baseline.route(0x4009dd80,0x4009ddb0)
 if ret:baseline.route(0x4009ddb0,0x4009de50)
 else:baseline.route(0x4009ddb0,0x4009df0a)
 overlay_enabled=True
 check('wrapped caller matches stock registers and exact SR',m.reg==baseline.reg and m.sr==baseline.sr)
 check('wrapped caller leaves identical retained event bytes',all(m.mem[RETAINED+track*72+j]==baseline.mem[RETAINED+track*72+j] for j in range(72)))""")
s=s.replace(" if ret and valid_owner:\n", " if not ret and oldid and valid_owner:check('zero-result path preserves readable prior binding',m.run(names['read'],(REC,oldid,track))==oldword)\n if ret and valid_owner:\n")
# On zero return helper read clobbers regs but does not affect pending stack checks.
open(p,'w').write(s)
