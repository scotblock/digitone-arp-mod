exec(open('work/receiver-route-refs.py').read().split('for a in [')[0])
for a in range(0x401ce170,0x401ce1ea,4):print(hex(a),b[a-base:a-base+4].hex())
