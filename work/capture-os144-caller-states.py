from pathlib import Path
source=Path('work/test-os144-stock-sustain-transition.py').read_text().split("exec(compile(s,'stock-sustain-transition','exec'))")[0]
exec(compile(source,'build-stock-capture','exec'))
s=s.replace('Digitone-OS1.44-stock-sustain-transition.json','Digitone-OS1.44-caller-state-capture.json')
needle="s.at(sites['allocated_return'],alloc)"
assert needle in s
s=s.replace(needle,"""from emu import snapshot
 seen=set()
 def capture_caller(uc,pc,n,d):
  event=uc.reg_read(UC_M68K_REG_A3);fields=list(struct.unpack('>18I',uc.mem_read(event,72)))
  key=(fields[2],fields[0],bool(fields[14]),bool(fields[10]&(1<<19)))
  if key in seen or len(seen)>=10:return
  seen.add(key);path=Path('work/os144')/('caller-'+str(len(seen))+'.snap')
  metadata={'event':hex(event),'fields':fields,'ms':s.now_ms(),'entry':hex(pc),'stack':hex(uc.reg_read(UC_M68K_REG_A7)),**state(uc)}
  saved=snapshot.save(s.m,str(path),extra=metadata)
  r.setdefault('caller_states',[]).append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'save':saved,**metadata})
  print('captured',len(seen),key,round(s.now_ms(),3),flush=True)
 s.at(0x4009e668,capture_caller)
 """+needle)
exec(compile(s,'stock-caller-capture','exec'))
