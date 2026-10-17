from pathlib import Path
p=Path('work/build-PC-release-reset-overlay.py');s=p.read_text();old="site=0x4008b88a;hooks.append({'name':'command_exit_cleanup','site':site,'length':6,'stock':main[site-0x40000400:site-0x40000400+6].hex(),'replacement':'4ef94008b86a'})"
new="""a=Asm();a.emit('4879401e2da2');absop(a,'4eb9',0x4000594c);absop(a,'4ef9',0x4008cbe6)
addr=BASE+sum(map(len,parts));code=a.done();parts.append(code);layout['command_exit_cleanup']={'address':addr,'size':len(code)}
site=0x4008b88a;hooks.append({'name':'command_exit_cleanup','site':site,'length':6,'stock':main[site-0x40000400:site-0x40000400+6].hex(),'replacement':'4ef9'+struct.pack('>I',addr).hex()})"""
assert old in s;p.write_text(s.replace(old,new))
