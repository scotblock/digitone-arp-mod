import pathlib,struct,hashlib,hmac,json,re,collections
p=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
b=p.read_bytes(); msgs=[]; pos=0
while pos<len(b):
 assert b[pos]==240
 end=b.index(247,pos+1); msgs.append(b[pos+1:end]);pos=end+1
data=[m for m in msgs if m[5]==126]; base=msgs[0][7]
assert all(len(m)==126 and max(m)<128 for m in data)
checks=[(base+sum(m[6+i]^(base+i) for i in range(119)))&127==m[125] for m in data]
seq=[((m[6]<<7)|m[7])*128+m[8] for m in data]
dec=bytearray()
for m in data:
 pay=m[9:125]
 for k in range(0,len(pay),8):
  for n,v in enumerate(pay[k+1:k+8]): dec.append(v|(((pay[k]>>(6-n))&1)<<7))
u=lambda x:struct.unpack('>I',x)[0]
size,stored=struct.unpack('>II',dec[:8]);c=bytes(dec[8:8+size])
result={'file_bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'messages':len(msgs),'data_packets':len(data),'markers':[m.hex() for m in msgs if m[5]==127],'packet_checks_pass':sum(checks),'sequence_contiguous':all(y==x+1 for x,y in zip(seq,seq[1:])),'decoded_bytes':len(dec),'container_bytes':size,'padding_bytes':len(dec)-8-size,'padding_zero':not any(dec[8+size:]),'content_checksum_stored':hex(stored),'content_checksum_calculated':hex(sum((i+1)^w[0] for i,w in enumerate(struct.iter_unpack('>I',c)))&0xffffffff),'header_hex':c[:32].hex(),'sections':[]}
def unpack(src):
 idx=8;tag=0;out=bytearray();last=1
 def byte():
  nonlocal idx
  v=src[idx];idx+=1;return v
 def bit():
  nonlocal tag
  tag<<=1
  if tag&255==0:
   v=byte();tag=(v<<1)|1;return v>>7
  return (tag>>8)&1
 def gamma():
  v=1
  for _ in range(32):
   v=v*2+bit()
   if bit():return v
  raise ValueError('gamma')
 ended=False
 try:
  while True:
   if bit():out.append(byte());continue
   g=gamma()
   if g==2:off=last
   else:
    off=(g<<8)+byte()
    if off==767:ended=True;break
    off-=767;last=off
   sl=2*bit()+bit();L=sl if sl else gamma()+2
   if off>3328:L+=1
   assert 0<off<=len(out) and len(out)<32000000
   for _ in range(L+1):out.append(out[-off])
 except IndexError:pass
 return bytes(out),ended,idx
raws=[]
for i in range(u(c[28:32])):
 sid,off,clen,dest=struct.unpack('>IIII',c[32+i*16:48+i*16]);src=c[off:off+clen]
 s={'id':sid,'offset':hex(off),'stored_bytes':clen,'destination':hex(dest),'prefix':src[:16].hex()}
 try:
  raw,ended,consumed=unpack(src)
  s.update(raw_bytes=len(raw),explicit_end=ended,consumed=consumed,stream_size=u(src[:4]),stream_sum_stored=hex(u(src[4:8])),stream_sum_calculated=hex(sum(src[8:8+u(src[:4])])&0xffffffff),raw_prefix=raw[:48].hex(),raw_sha256=hashlib.sha256(raw).hexdigest())
  strings=[x.decode('ascii') for x in re.findall(rb'[\x20-\x7e]{6,}',raw)]
  s['interesting_strings']=[x for x in strings if re.search(r'arp|scale|digitone|bootstrap|startup|coldfire|mcf|upgrade',x,re.I)][:65]
  pathlib.Path(f'work/section-{sid}.bin').write_bytes(raw);raws.append(raw)
 except (AssertionError,ValueError):
  s['codec']='raw or unsupported';raws.append(src)
  s['strings']=[x.decode('ascii') for x in re.findall(rb'[\x20-\x7e]{6,}',src) if re.search(rb'upgrade|digitone|startup',x,re.I)][:15]
 result['sections'].append(s)
for raw in raws:
 for match in re.finditer(bytes.fromhex('bef9a3f7c67178f2'),raw):
  start=match.end();end=raw.find(b'\0',start);s=raw[start:end]
  if 0<len(s)<=128 and all(32<=v<127 for v in s):
   const=raw[end+1:end+33]
   key=bytes(x^y^z for x,y,z in zip(hashlib.sha256(s).digest(),hashlib.sha256(s[::-1]).digest(),const))
   if hmac.new(key,c[:-32],hashlib.sha256).digest()==c[-32:]:result['hmac_sha256_verified']=True
result.setdefault('hmac_sha256_verified',False)
assert hashlib.sha256(p.read_bytes()).hexdigest()==result['sha256']
pathlib.Path('work/inspection.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
