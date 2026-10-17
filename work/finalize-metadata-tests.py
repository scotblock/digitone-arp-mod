p='work/test-metadata-helper-instructions.py'
s=open(p).read().replace("result={'passed':len(checks)","total=len(m.steps)\nresult={'passed':len(checks)")
open(p,'w').write(s)
