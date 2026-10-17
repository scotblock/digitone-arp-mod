from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
cfg=json.loads(Path('work/os144/PC_ONLY-live-capture-layout.json').read_text());ENTRY=0x47be3400
a=Asm();a.emit('4fefffc048d77fff40c03f40003c46fc2700426f003e')
a.emit('202f00440c800000009e');a.branch('6600','disable')
for address,value in [(0x47be1000,0x47bccf04),(0x47be1004,0x534c4332),(0x47be1008,2),(0x47be100c,0xb70)]:
 absolute(a,'2039',address);absolute(a,'0c80',value);a.branch('6600','disable')
a.emit('3f7c0001003e42b947be1010')
for address,length in [(0x47be1014,0xb60),(cfg['state'],cfg['state_bytes'])]:
 absolute(a,'2f3c',length);a.emit('42a7');absolute(a,'4879',address);absolute(a,'4eb9',0x400fbb20);a.emit('4fef000c')
a.branch('6000','stock');a.label('disable');a.emit('42b947be1000')
a.label('stock');a.emit('302f003c46c02f2f0044');absolute(a,'4eb9',0x47be0642);a.emit('588f2f40000046fc27004a6f003e');a.branch('6700','return')
for address,value in [(0x47be1000,0x47bccf04),(0x47be1004,0x534c4332),(0x47be1008,2),(0x47be100c,0xb70)]:
 absolute(a,'2039',address);absolute(a,'0c80',value);a.branch('6600','disable_after')
a.emit('700123c047be10104e71');a.branch('6000','return');a.label('disable_after');a.emit('42b947be1000');a.label('return');restore(a);a.emit('4e75');fallback=a.done()
oldpayload=Path('work/os144/PC_ONLY-E04-ISA-corrected-payload.bin').read_bytes();live=Path('work/os144/PC_ONLY-live-capture-code.bin').read_bytes()
extended=bytearray(ENTRY-0x47be0000+len(fallback));extended[:len(oldpayload)]=oldpayload;extended[0x3000:0x3000+len(live)]=live;extended[0x3400:]=fallback;extended.extend(bytes((-len(extended))%4))
main=bytearray(Path('work/os144/PC_ONLY-E04-ISA-corrected-main.bin').read_bytes());base=0x40000400
assert main[0x400ffed0-base:0x400ffed6-base].hex()=='4ef947be08a4';main[0x400ffed2-base:0x400ffed6-base]=struct.pack('>I',ENTRY)
for h in cfg['hooks']:
 off=h['site']-base;assert main[off:off+h['length']].hex()==h['stock'];main[off:off+h['length']]=bytes.fromhex(h['replacement'])
assert int.from_bytes(main[0x4029c4be-base:0x4029c4c2-base],'big')==623;main[0x4029c4be-base:0x4029c4c2-base]=struct.pack('>I',len(extended)//4);main[0x4029c5b0-base:]=extended
Path('work/os144/PC_ONLY-live-storage-main.bin').write_bytes(main);Path('work/os144/PC_ONLY-live-storage-payload.bin').write_bytes(extended)
out={'PC_only':True,'packaged_firmware_modified':False,'fallback_address':ENTRY,'fallback_bytes':len(fallback),'payload_bytes':len(extended),'copy_longwords':len(extended)//4,'state':cfg['state'],'state_bytes':cfg['state_bytes'],'live':cfg,'regions':[(0x4029c4b0,110),(ENTRY,len(fallback)),(cfg['base'],cfg['bytes'])],'main_sha256':hashlib.sha256(main).hexdigest(),'payload_sha256':hashlib.sha256(extended).hexdigest()}
Path('work/os144/PC_ONLY-live-storage-layout.json').write_text(json.dumps(out,indent=2));print('PC startup extension:',len(extended),'payload bytes;',len(fallback),'reset bytes')
