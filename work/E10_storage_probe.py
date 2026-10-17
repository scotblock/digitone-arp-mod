"""Distinct valid diagnostic records for the PC serialized-storage probes."""
def record_bytes(slot):
 if not 0<=slot<128:raise ValueError('slot')
 r=bytearray(32);r[:4]=b'MS10';r[4:10]=bytes([1,slot&1,slot%16+1,slot%12,slot%36,0]);r[10:12]=((slot*503)&65535).to_bytes(2,'big')
 r[12:28]=bytes(((slot+i)%49-24)&255 for i in range(16));r[28:]=sum(r[:28]).to_bytes(4,'big');return bytes(r)
