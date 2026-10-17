p='work/test-metadata-helper-instructions.py'
s=open(p).read();s=s.replace("result={'passed':len(checks)","""# Ordinary additive/zero-return path preserves the prior accepted snapshot.
m.write(record+8,4,0);call('begin',record);call('commit',record,43,0x80000080,0)
check('balanced zero-result cancellation preserves prior context',call('begin',record)==1 and call('cancel',record)==1 and call('read',record,43,0)==0x80000080)
for prior_sr in [0x2000,0x240f,0x2715]:
 m.sr=prior_sr;m.run(names['begin'],(record,));m.run(names['cancel'],(record,))
 check('exact SR restoration across masks',m.sr==prior_sr)
check('source candidate unchanged',m.read(srcptr,4)==0x80006080)
result={'passed':len(checks)""")
open(p,'w').write(s)
