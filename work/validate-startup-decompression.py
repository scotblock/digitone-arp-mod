import pathlib,hashlib,json
b=pathlib.Path('work/section-3.bin').read_bytes();base=0x40000400

def decode_asset(blob,output_limit=0x800000):
 if len(blob)<8:raise ValueError('truncated header')
 clen=int.from_bytes(blob[:4],'big');olen=int.from_bytes(blob[4:8],'big');p=8;buf=0;out=bytearray();last=1;tokens=[]
 def byte():
  nonlocal p
  if p>=8+clen or p>=len(blob):raise ValueError(('input bound',p,clen))
  v=blob[p];p+=1;return v
 def bit():
  nonlocal buf
  buf=(buf*2)&0xffffffff
  if buf&255:return (buf>>8)&1
  buf=byte()*2+1
  return (buf>>8)&1
 while True:
  at=p;start=len(out)
  if bit():
   if len(out)>=output_limit:raise ValueError('output bound')
   out.append(byte());tokens.append(('literal',start,len(out),p));continue
  off=1
  while True:
   off=(off*2+bit())&0xffffffff
   if bit():break
  if off!=2:
   raw=(off*256+byte())&0xffffffff
   if raw==0x2ff:break
   last=raw-0x2ff
  length=bit()*2+bit()
  if length==0:
   length=1
   while True:
    length=length*2+bit()
    if bit():break
    if length>output_limit:raise ValueError('length runaway')
   length+=2
  count=length+1+(last>0xd00)
  if last<=0 or last>len(out):raise ValueError(('backreference',last,len(out)))
  if len(out)+count>output_limit:raise ValueError(('output bound',len(out),count,olen))
  for _ in range(count):out.append(out[-last])
  tokens.append(('match',start,len(out),p,last,count))
 # Header second word is not assumed to be output length.
 return bytes(out),{'compressed_size':clen,'header_second_word':olen,'compressed_byte_sum':sum(blob[8:8+clen])&0xffffffff,'header_checksum_matches':(sum(blob[8:8+clen])&0xffffffff)==olen,'output_size':len(out),'consumed':p-8,'tokens':len(tokens),'sha256':hashlib.sha256(out).hexdigest(),'matches':sum(t[0]=='match' for t in tokens),'max_distance':max(t[4] for t in tokens if t[0]=='match')},tokens

if __name__=='__main__':
 a=0x401c40a0;blob=b[a-base:];out,info,tokens=decode_asset(blob);print(json.dumps(info));print(out[:64].hex())
