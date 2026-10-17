"""Trace the cleanup object's last writers in PC RAM only."""
import pathlib,pickle,collections
source=pathlib.Path('work/continue-startup-decompression.py').read_text()
# Install tracing after the original response-machine definitions are loaded.
insert="""
original_write=ResponseMachine.write
def traced_write(self,address,size,value):
 if getattr(self,'trace_cleanup',False) and address<0x30002000 and address+size>0x30001e80:
  self.cleanup_writes.append((self.steps[-1] if self.steps else 0,address,size,value))
 return original_write(self,address,size,value)
ResponseMachine.write=traced_write
"""
source=source.replace("constructor=m;owner_before=t['protected'](m,owner)",insert+"\nconstructor=m;owner_before=t['protected'](m,owner)")
# Save a reusable PC-state checkpoint after validated decompression, omitting
# huge histories and dynamically bound interpreter methods.
insert="""
attrs={k:v for k,v in m.__dict__.items() if k not in ['run','advance','steps','writes','timeline']}
attrs.update(steps=m.steps[-100:],writes=[],timeline=[])
pathlib.Path('work/post-decompression-state.pkl').write_bytes(pickle.dumps({'attrs':attrs,'owner':owner,'owner_before':owner_before},protocol=5))
m.trace_cleanup=True;m.cleanup_writes=collections.deque(maxlen=3000)
"""
source=source.replace("# Resume stock epilogue and caller, with a boundary just before initializer.",insert+"\n# Resume stock epilogue and caller, with a boundary just before initializer.")
source=source.replace("results['continuation']['last_instructions']", "results['cleanup_writes']=[(hex(pc),hex(a),z,hex(v & ((1<<(8*z))-1))) for pc,a,z,v in m.cleanup_writes]\nresults['continuation']['last_instructions']")
source=source.replace("outputs/Digitone-startup-decompression-results.json","outputs/Digitone-cleanup-pointer-trace.json")
exec(compile(source,'work/continue-startup-decompression.py','exec'))
