exec(open('work/shutdown-barrier-graphs.py').read().split('graphs=[]')[0])
import hashlib
entries=[(0x400d7d50,0x400d7dfe),(0x400d7dfe,0x400d7ecc),(0x400d7bcc,0x400d7c8a),(0x4015a5e2,0x4015a608),(0x4012f8e8,0x4012f908),(0x40001a4c,0x40001ac4),(0x40001b6e,0x40001bd6),(0x400d6baa,0x400d6bb4)]
graphs=[graph(s,e) for s,e in entries]
checks=[]
def check(n,c):assert c,n;checks.append(n)
check('exit slot resolves to callback dispatcher',struct.unpack_from('>I',b,0x401a3ba8-base+0x1c)[0]==0x400d6db6)
check('outer exit virtual call precedes node unlink',graphs[0]['instructions']['0x400d7db4']['instruction']=='jsr (a0)' and graphs[0]['instructions']['0x400d7dba']['instruction']=='jsr (a6)')
check('manager mutex acquisition uses manager plus four',graphs[0]['instructions']['0x400d7d6c']['instruction']=='pea.l $4(a3)')
check('mutex acquired before page virtual callback',graphs[0]['instructions']['0x400d7d7a']['instruction']=='jsr $4015a5e2.l')
check('mutex released after callback returns',graphs[0]['instructions']['0x400d7dec']['instruction']=='jsr $4012f8e8.l')
check('closed page condition reads only page byte30',graphs[-1]['instructions']['0x400d6bae']['instruction']=='move.b $30(a0), d0')
check('lock restores entry SR before returning',graphs[5]['instructions']['0x40001aa4']['instruction']=='move.w d2, sr')
check('contended lock uses trap and is not a global stop',graphs[5]['instructions']['0x40001a9e']['instruction']=='trap #$0')
check('unrelated audio pool literals absent in page-dispatch local graph',not any(any(x in v['instruction'] for x in ['4199fe94','4199fe98','4199d590','400f08f0','41345f08']) for g in graphs[:3] for v in g['instructions'].values()))
check('outer transition takes same mutex before processing page actions',graphs[1]['instructions']['0x400d7e2e']['instruction']=='jsr $4015a5e2.l')
check('explicit remove path also locks before virtual exit',graphs[2]['instructions']['0x400d7bfe']['instruction']=='jsr $4015a5e2.l' and graphs[2]['instructions']['0x400d7c3a']['instruction']=='jsr (a0)')
syx=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(syx.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
check('hashes unchanged',hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'])
pathlib.Path('outputs/Digitone-outer-page-transition-graphs.json').write_text(json.dumps({'firmware_modified':False,'graphs':graphs,'checks':checks,'sha256':hashes,'scope':'Local normal-return CFGs; scheduler traps may resume, exception paths not certified.'},indent=2))
print(json.dumps({'checks':len(checks),'graphs':len(graphs),'instructions':sum(len(g['instructions']) for g in graphs)}))
