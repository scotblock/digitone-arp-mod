p='work/test-resident-caller-helpers.py';s=open(p).read();s=s.replace(" check('actual caller produces expected metadata'", " print('DEBUG',kind,ret,hex(m.read(REC+4,4)),m.read(REC+8,4),hex(expected),[n for n,a in names.items() if a in m.steps])\n check('actual caller produces expected metadata'")
open(p,'w').write(s)
