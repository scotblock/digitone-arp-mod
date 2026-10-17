"""Build an isolated RAM lookup quantizer; never repack firmware."""
import pathlib,json,hashlib,sys
class Asm:
 def __init__(self):self.code=bytearray();self.labels={};self.fix=[]
 def emit(self,h):self.code.extend(bytes.fromhex(h))
 def label(self,n):self.labels[n]=len(self.code)
 def branch(self,op,n):p=len(self.code);wide=p<32;self.emit(op[:2]+('000000' if wide else '00'));self.fix.append((p,n,wide))
 def done(self):
  for p,n,wide in self.fix:
   delta=self.labels[n]-p-2
   if wide:self.code[p+2:p+4]=delta.to_bytes(2,'big',signed=True)
   else:
    assert -128<=delta<=127 and delta!=0,(p,n,delta)
    self.code[p+1]=delta&255
  return bytes(self.code)
RAM=0x47be0000
blob=bytearray(pathlib.Path('work/native-overlay-code.bin').read_bytes())
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
rows={x['raw_scale']:x['pitch_classes'] for x in json.loads(pathlib.Path('outputs/Digitone-OS1.42-scale-map.json').read_text())['scales']}
table=bytes((next(d for d in range(12) if (p-d)%12 in rows[s])<<4)|next(d for d in range(12) if (p+d)%12 in rows[s]) for s in range(35) for p in range(12))
TABLE=RAM+(len(blob)+15)//16*16
a=Asm();a.emit('4fefffe048d70cfc242f0024222f0028')
a.emit('0c8200000080');a.branch('6400','fallback')
a.emit('4a81');a.branch('6a00','fallback');a.emit('200102807fff8000');a.branch('6600','fallback')
a.emit('260102830000007f2801ee8c02840000003f0c8400000024');a.branch('6400','fallback')
a.emit('4a84');a.branch('6700','fallback');a.emit('538420029083')
a.label('negative');a.emit('4a80');a.branch('6a00','positive');a.emit('06800000000c');a.branch('6000','negative')
a.label('positive');a.emit('0c800000000c');a.branch('6500','lookup');a.emit('04800000000c');a.branch('6000','positive')
a.label('lookup');a.emit('2c04dc84dc84e58ed086207c'+TABLE.to_bytes(4,'big').hex()+'d1c07a001a102c05e88e02850000000f2e029e862002d085')
a.emit('4a87');a.branch('6b00','end');a.emit('0c8000000080');a.branch('6400','lower');a.emit('bc85');a.branch('6200','end')
a.label('lower');a.emit('2007');a.branch('6000','end');a.label('fallback');a.emit('2002')
a.label('end');a.emit('4cd70cfc4fef00204e75');code=a.done()
site=layout['quantize'];off=site['address']-RAM
assert len(code)<=site['size'],(len(code),site['size'])
blob[off:off+site['size']]=code+bytes.fromhex('4e71')*((site['size']-len(code))//2)
blob.extend(bytes(TABLE-RAM-len(blob)));blob.extend(table)
assert RAM+len(blob)<0x47be1000
pathlib.Path('work/fast-pitch-overlay.bin').write_bytes(blob)
pathlib.Path('work/fast-pitch-layout.json').write_text(json.dumps(layout))
info={'quantizer_old_bytes':site['size'],'quantizer_new_bytes':len(code),'table_address':hex(TABLE),'table_bytes':len(table),'overlay_bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'firmware_modified':False}
pathlib.Path('work/fast-pitch-build.json').write_text(json.dumps(info,indent=2));print(info)
