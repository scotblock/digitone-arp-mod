exec(open('work/scan-PC-removal-callers.py').read().split('refs={}')[0])
callbacks=[]
for p in range(0x400725f4-base,0x40072a70-base,2):
 if b[p:p+2]==b'\x20\x3c':
  fn=int.from_bytes(b[p+2:p+6],'big')
  if 0x400722ea<=fn<=0x400725ae:
   raw=b[fn-base:fn-base+70];idx=raw.find(b'\x41\xe8');offset=int.from_bytes(raw[idx+2:idx+4],'big');label=None;labeladdr=None
   for q in range(p+6,min(p+110,len(b)),2):
    if b[q:q+2]==b'\x48\x79':
     addr=int.from_bytes(b[q+2:q+6],'big')
     if 0x401d0000<=addr<0x401f0000:
      label=b[addr-base:addr-base+80].split(b'\0')[0].decode('ascii');labeladdr=hex(addr);break
   callbacks.append({'callback':hex(fn),'registered_at':hex(base+p),'label':label,'label_address':labeladdr,'child_offset':hex(offset),'selector':hex(0x400e54a2 if fn==0x40072560 else 0x400e47e6)})
assert len(callbacks)==11 and all(x['child_offset']!='0x2b4' for x in callbacks)
for r in callbacks:print(r)
positions=[];p=b.find(b'\x02\xb4')
while p>=0:
 if p%2==0:positions.append(hex(base+p))
 p=b.find(b'\x02\xb4',p+1)
longs=[];p=b.find(b'\0\0\x02\xb4')
while p>=0:longs.append(hex(base+p));p=b.find(b'\0\0\x02\xb4',p+1)
Path('outputs/Digitone-E04-PC-audio-selection-menu-map.json').write_text(json.dumps({'PC_only':True,'firmware':'stock 1.44','builder':'0x400725f4','constructor':'0x40072a7e','audio_constructor_call':'0x40072db8','audio_child_store':'0x40072ddc','audio_child_offset':'0x2b4','callbacks':callbacks,'audio_slot_selected_by_recovered_callbacks':False,'all_aligned_word_02b4_hits':positions,'long_000002b4_hits':longs,'limits':['Literal/offset scan and recovered builder enumeration do not exhaust computed aliases or external diagnostic entry.','No actual application request selecting the audio-test slot is identified.']},indent=2))
