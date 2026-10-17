exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
end=0x40017248-base
for off in range(end-8000,end,2):
 if b[off:off+2]==bytes.fromhex('4e56') or (b[off:off+3]==bytes.fromhex('4fefff') and b[off+4:off+6]==bytes.fromhex('48d7')):print(hex(base+off),b[off:off+8].hex())
