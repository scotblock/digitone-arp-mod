"""Native atomic settings publication API for the future device editor."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
n=json.loads(Path('work/os144/E09A-PC-install-layout.json').read_text())
c=json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text());S=n['state'];X=c['state'];B=0x47be9200
def absop(a,op,v):absolute(a,op,v)
a=Asm();save(a)
# publish(owner, length, enabled-mask, root/scale word, offsets[16], enabled)
a.emit('242f0044262f0048282f004c2a2f0050246f00542c2f0058')
absop(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','deny')
absop(a,'2039',X);a.emit('0c804d535131');a.branch('6600','deny')
a.emit('0c8240000000');a.branch('6500','deny');a.emit('0c8247ffff5c');a.branch('6200','deny')
absop(a,'2079',0x419f0de0);a.emit('4a88');a.branch('6700','deny');a.emit('d1fc00000ff820100c8040193b90');a.branch('6600','deny');a.emit('20280010b082');a.branch('6600','deny')
a.emit('0c8300000001');a.branch('6500','deny');a.emit('0c8300000010');a.branch('6200','deny')
a.emit('20040280ffff0000');a.branch('6600','deny');a.emit('0c8600000001');a.branch('6200','deny')
a.emit('4a85');a.branch('6a00','deny');a.emit('200502807fffe000');a.branch('6600','deny');a.emit('200502800000007f0c800000000b');a.branch('6200','deny')
a.emit('2005ee8802800000003f0c8000000023');a.branch('6200','deny')
a.emit('200a0c8040000000');a.branch('6500','deny');a.emit('0c8047fffff0');a.branch('6200','deny')
# Before any mutation, validate the complete byte sequence.
a.emit('204a720f');a.label('validate')
a.emit('70001018488048c00c80ffffffe8');a.branch('6d00','deny');a.emit('0c8000000018');a.branch('6e00','deny')
a.emit('5381');a.branch('6a00','validate')
# Any outstanding playback/arena requires the same existing playback owner.
for offset in [8,16,280]:
 absop(a,'4ab9',S+offset);a.branch('6600','owned')
a.branch('6000','write')
a.label('owned');a.emit('2002');absop(a,'b0b9',S+336);a.branch('6600','deny');absop(a,'b0b9',X+28);a.branch('6600','deny')
a.label('write')
for op,off in [('23c6',4),('23c3',8),('23c4',20),('23c5',24),('23c2',28)]:absop(a,op,X+off)
a.emit('204a');absop(a,'43f9',X+32);a.emit('720f');a.label('copy');a.emit('101812c05381');a.branch('6a00','copy')
absop(a,'2039',X+12);a.emit('b083');a.branch('6500','edit');absop(a,'42b9',X+12)
a.label('edit');absop(a,'2039',X+16);a.emit('b083');a.branch('6500','ok');a.emit('20035380');absop(a,'23c0',X+16)
a.label('ok');a.emit('7001');a.branch('6000','return')
a.label('deny');a.emit('7000')
a.label('return');a.emit('2f400000');restore(a);a.emit('4e75');code=a.done()
Path('work/os144/PC_ONLY-E10-step-publication.bin').write_bytes(code)
Path('work/os144/PC_ONLY-E10-step-publication.json').write_text(json.dumps({'PC_only':True,'base':B,'bytes':len(code),'ABI':'publish(owner,length,mask,root_scale_word,offsets16,enabled)','state':X,'limits':['API only; no panel callbacks, saving, startup or hardware storage integration.']},indent=2))
print('Native complete-settings publisher',len(code),'bytes')
