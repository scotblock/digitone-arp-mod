"""Execute actual serialized configuration parser prefix through both gate stores."""
exec(open('work/execute-application-gate-writers.py').read().split('for full in (0,1):')[0])
source=source.replace("   elif m in ('add','sub','addq'", """   elif m=='subx':
    x=self.get(ops[0],n);y=self.get(ops[1],n);oldz=bool(self.sr&4);extend=1 if self.sr&16 else 0;v=y-x-extend;sign=1<<(n*8-1)
    self.put(ops[1],n,v);self.flags(v,n,bool((y^x)&(y^v)&sign),y<x+extend,True)
    if not oldz:self.sr&=~4
   elif m in ('add','sub','addq'""")
source=source.replace("'bpl','bmi','blt')", "'bpl','bmi','blt','bls','bhi')")
source=source.replace("'blt':negative}[m]", "'blt':negative,'bls':z or bool(self.sr&1),'bhi':not z and not bool(self.sr&1)}[m]")
source=source.replace('def run(self,entry,args=()):','def until(self,entry,stop):')
source=source.replace("  for v in reversed(args):self.put('-(a7)',4,v)\n  self.put('-(a7)',4,0xffffffff);pc=entry",'  pc=entry')
source=source.replace('if pc==0xffffffff:break','if pc==stop:break')
source=source.replace("  self.reg['a7']+=len(args)*4",'').replace("  assert self.reg['a7']==initial_sp",'').replace("  assert all(self.reg[r]==v for r,v in saved.items())",'')
exec('if True:\n'+source);Machine.until=until
RANGES.append((0x400094aa,0x40009d24))
SRC=0x28800000;checks=[];cases=[]
for version,receive,note in [(7,0,0),(7,3,1),(7,255,255),(6,0,0)]:
 m=writer_state();m.map(SRC,0x3000);m.write(SRC,4,version);m.write(SRC+4,2,0x3840);m.write(SRC+0x28,1,receive);m.write(SRC+0x31,1,note)
 m.write(CF+0x8c,4,2);m.write(CF+0xb0,4,1)
 p=pop(m,60);e=event(m,p);m.run(0x400f0690,(T,e));m.run(0x400f0886,(e,));qh=m.read(0x4199fe94,4)
 m.put('-(a7)',4,SRC);m.put('-(a7)',4,CF);m.put('-(a7)',4,0xffffffff)
 start=len(m.steps);stop=0x40009816 if version==7 else 0xffffffff;m.until(0x400094aa,stop);path=m.steps[start:]
 if version==7:
  check(f'{receive}/{note}: serialized receive byte clamps at 3',m.read(CF+0x8c,4)==min(receive,3))
  check(f'{receive}/{note}: serialized note byte clamps at 1',m.read(CF+0xb0,4)==min(note,1))
  check(f'{receive}/{note}: both actual stores execute',0x4000973e in path and 0x40009812 in path)
 else:
  check('wrong version rejected before gate mutation',m.read(CF+0x8c,4)==2 and m.read(CF+0xb0,4)==1 and 0x4000973e not in path and m.reg['d0']==0)
 check(f'{version}/{receive}/{note}: parser gate writes do not retire live owners',m.read(p,4)==2 and m.read(T+56,4)==p and m.read(0x4199fe94,4)==qh)
 cases.append({'version':version,'source_receive':receive,'source_note':note,'endpoint':hex(stop),'steps':[hex(x) for x in path],'gates':[m.read(CF+0x8c,4),m.read(CF+0xb0,4)],'retained_count':m.read(p,4)})
pathlib.Path('outputs/Digitone-config-parser-gate-prefix-results.json').write_text(json.dumps({'checks':checks,'cases':cases,'firmware_modified':False,'limitations':['Valid parser cases stop immediately after the second gate store; the remaining full deserializer is not executed.','Version 7 serialized data and runtime destination pointer supplied; no real project load or hardware state observed.','No assertion that parser prefix proves whole-load shutdown behavior.']},indent=2))
print(json.dumps({'checks':len(checks),'cases':len(cases),'recorded_steps':sum(len(c['steps']) for c in cases)}))
