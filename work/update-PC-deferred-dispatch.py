from pathlib import Path
p=Path('work/build-PC-deferred-release-overlay.py');s=p.read_text()
s=s.replace("read(a,DRAIN);cmp(a,1);a.branch('6700','stock')", "read(a,DRAIN);cmp(a,0);a.branch('6600','overflow')")
anchor="blob=b''.join(parts);hooks=[]"
extra="""a=Asm();save(a);a.emit('202f001c');cmp(a,1);a.branch('6600','original');restore(a);absolute(a,'4ef9',resume)
a.label('original');restore(a);a.emit(Path('work/os144/PC_ONLY-persistent-admission.bin').read_bytes()[68:76].hex());absolute(a,'4ef9',0x47fa004c);dispatch=add('completion_dispatch',a)
"""
s=s.replace(anchor,extra+anchor)
s=s.replace("Path('work/os144/PC_ONLY-deferred-release-overlay.bin').write_bytes(blob)","hooks.append({'name':'completion_dispatch','site':0x47fa0044,'length':8,'previous':Path('work/os144/PC_ONLY-persistent-admission.bin').read_bytes()[68:76].hex(),'replacement':'4ef9'+struct.pack('>I',dispatch).hex()+'4e71'})\nPath('work/os144/PC_ONLY-deferred-release-overlay.bin').write_bytes(blob)")
s=s.replace("Native resume API has no installed real live-transition caller; current production warm resets remain refused.","Existing native completion success dispatch now drains before LIVE; real warm closure still unimplemented/refused.")
p.write_text(s)
