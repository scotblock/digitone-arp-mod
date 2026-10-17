"""PC memory identity only. Does not model hardware cache coherence."""
def canonical(a):
 return 0x40000000+(a-0x40000000)%0x08000000 if 0x40000000<=a<0x80000000 else a
def install_aliases(cls):
 if getattr(cls,'alias_model_installed',False):return
 oldmap,oldread,oldwrite=cls.map,cls.read,cls.write
 def mapped(self,a,n):
  assert n==0 or canonical(a+n-1)==canonical(a)+n-1,'mapping crosses physical wrap'
  return oldmap(self,canonical(a),n)
 def read(self,a,n):
  assert canonical(a+n-1)==canonical(a)+n-1,'read crosses physical wrap'
  return oldread(self,canonical(a),n)
 def write(self,a,n,v):
  assert canonical(a+n-1)==canonical(a)+n-1,'write crosses physical wrap'
  return oldwrite(self,canonical(a),n,v)
 cls.map=mapped;cls.read=read;cls.write=write;cls.alias_model_installed=True
