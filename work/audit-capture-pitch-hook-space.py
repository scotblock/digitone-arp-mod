exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json,hashlib
r={}
anchors={0x40093ef4:'254400082544003c',0x4009df9a:'2f037a07202b0028',0x400f0626:'40c046fc2700',0x4009de8c:'4eb94009755e',0x4009df52:'4eb94009755e',0x4009de98:'17400018',0x4009df5e:'17400018'}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h
r['verified_hook_anchors']={hex(a):h for a,h in anchors.items()}
r['larger_intervals_screened']=[{'range':'401fd47c..401fdc8c','size':2064,'finding':'401fdc88 is explicitly loaded by stock routines at 40098838 and 40098d4a. Their companion table address is 401fcc8c. This is not an unreferenced code cave; the zero run cannot be treated as available wholesale.'},{'range':'40209f1c..4020a32c','size':1040,'finding':'Both bounds are passed as resource arguments at 401137bc/401137c2. Existing ownership; do not use.'},{'range':'4023c302..4023c670','size':878,'finding':'Pointers at 4023c250/254/258 target 4023c536/59e/606 inside it. Existing ownership; do not use.'},{'range':'401fbf8c..401fc38c','size':1024,'finding':'No even-aligned absolute pointer into the interval in this screen. Zero run follows floating-point data; indexed use remains unresolved. No ownership established.'}]
r['disassembly']={hex(lo):[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)] for lo,hi in [(0x4009882c,0x40098850),(0x40098d44,0x40098d5c),(0x401137bc,0x401137d8)]}
r['sha256_main']=hashlib.sha256(b).hexdigest();r['firmware_modified']=False
pathlib.Path('outputs/Digitone-capture-pitch-hooks-and-space-audit.json').write_text(json.dumps(r,indent=2));print('PASS',len(anchors),'anchors; screened four larger intervals')
