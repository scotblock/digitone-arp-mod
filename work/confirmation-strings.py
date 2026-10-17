exec(open('work/receiver-route-refs.py').read().split('for a in [')[0])
for a in [0x401e2625,0x401e2632,0x401e260a,0x401e261b]:print(hex(a),b[a-base:b.index(0,a-base)].decode(errors='replace'))
