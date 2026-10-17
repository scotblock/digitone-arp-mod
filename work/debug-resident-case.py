p='work/test-resident-caller-helpers.py';s=open(p).read().replace(" check('actual caller produces expected metadata'", " if m.read(REC+4,4)!=expected or m.read(REC+8,4)!=0:print('FAILED CASE',kind,ret,hex(m.read(REC+4,4)),m.read(REC+8,4),hex(expected),[n for n,a in names.items() if a in m.steps])\n check('actual caller produces expected metadata'")
open(p,'w').write(s)
