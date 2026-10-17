"""Disposable RAM overlay. Does not modify or package E06 firmware."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
STATE=0x47be5c00;RECS=STATE+32;MARKERS=STATE+16;BASE=0x47be5000
TX=BASE;SERVICE=BASE+0x100;OFF=BASE+0x200;ON=BASE+0x300;PUMP=BASE+0x500;MARK=BASE+0x600;START=BASE+0x700;REL1=BASE+0x800;REL2=BASE+0x880;POLL=BASE+0x900;CLEAR=BASE+0x980
parts=[];regions=[]
def add(name,addr,a,limit):
 code=a.done();assert len(code)<=limit,(name,len(code),limit);parts.append((addr,code));regions.append({'name':name,'base':addr,'bytes':len(code)})
def saveall(a):a.emit('4fefffc048d77fff40c03f40003c46fc2700')
def restoreall(a):a.emit('302f003c46c04cd77fff4fef0040')
# tx(status,note,velocity): interrupt-masked caller; preflight prevents the stock
# DIN ring writer's busy-wait. Physical DMA can advance, which only frees space.
a=Asm();a.emit('4fefffd848d70cfc242f002c262f0030282f0034')
a.emit('2039405285a4');a.branch('6700','no');a.emit('0c8300000080');a.branch('6400','no');a.emit('0c8400000080');a.branch('6400','no')
a.emit('2039405285b090b9405285bc73f9fc0454b475f9fc0454bc9282d081028000000fff223c00001000928092b9405285b80c8100000003');a.branch('6d00','no')
a.emit('242f002c1f4200201f4300211f440022486f002048780003');absolute(a,'4eb9',0x40002a3a);a.emit('508f7001');a.branch('6000','end');a.label('no');a.emit('7000');a.label('end');a.emit('4cd70cfc4fef00284e75');add('DIN_try_send',TX,a,256)
# service(record): release only the last shared voice of a channel/note pair;
# retain pending note-off when the output ring has no room.
a=Asm();a.emit('4fefffe048d70cfc246f0024203947be5c000c8053414d31');a.branch('6600','end');a.emit('200a0480'+struct.pack('>I',RECS).hex()+'0c8000000080');a.branch('6400','end');a.emit('02800000000f');a.branch('6600','end');a.emit('4a92');a.branch('6700','end');a.emit('4aaa0008');a.branch('6700','end')
a.emit('262a0004');absolute(a,'47f9',RECS);a.emit('7408');a.label('scan');a.emit('b7ca');a.branch('6700','next');a.emit('4a93');a.branch('6700','next');a.emit('b6ab0004');a.branch('6700','clear');a.label('next');a.emit('47eb00105382');a.branch('6600','scan')
a.emit('2003e08802800000000f0080000000800283000000ff42a72f032f00');absolute(a,'4eb9',TX);a.emit('4fef000c4a80');a.branch('6700','end');a.label('clear');a.emit('429242aa0008');a.label('end');a.emit('4cd70cfc4fef00204e75');add('service_release',SERVICE,a,256)
# release(voice): all caller state, including SR, survives.
a=Asm();saveall(a);a.emit('203947be5c000c8053414d31');a.branch('6600','end');a.emit('202f00440c8000000008');a.branch('6400','end');a.emit('e988');absolute(a,'45f9',RECS);a.emit('d5c04a92');a.branch('6700','end');a.emit('7001254000082f0a');absolute(a,'4eb9',SERVICE);a.emit('588f');a.label('end');restoreall(a);a.emit('4e75');add('release_voice',OFF,a,256)
# start(voice,track,event,note,velocity): close previous ownership first; note-on
# is published only after output acceptance. Shared/unison voices emit one pair.
a=Asm();saveall(a);a.emit('203947be5c000c8053414d31');a.branch('6600','end');a.emit('202f00440c8000000008');a.branch('6400','end');a.emit('e988');absolute(a,'47f9',RECS);a.emit('d7c04a93');a.branch('6700','eligible');a.emit('7001274000082f0b');absolute(a,'4eb9',SERVICE);a.emit('588f4a93');a.branch('6600','drop')
a.label('eligible');a.emit('203947be5c000c8053414d31');a.branch('6600','end');a.emit('4ab947be5c04');a.branch('6700','end');a.emit('2039419c5df4028000000001');a.branch('6700','end')
a.emit('222f00480c8100000004');a.branch('6400','end');absolute(a,'41f9',MARKERS);a.emit('24301c00b4af004c');a.branch('6600','end');absolute(a,'41f9',0x41368d30);a.emit('2c301c000c8600000010');a.branch('6400','end');a.emit('e18e262f00500c8300000080');a.branch('6400','end');a.emit('282f00540c8400000001');a.branch('6d00','end');a.emit('0c8400000080');a.branch('6400','end');a.emit('8c83');absolute(a,'45f9',RECS);a.emit('7a08')
a.label('scan');a.emit('4a92');a.branch('6700','next');a.emit('bcaA0004'.lower());a.branch('6700','store');a.label('next');a.emit('45ea00105385');a.branch('6600','scan')
a.emit('2006e0880080000000902f042f032f00');absolute(a,'4eb9',TX);a.emit('4fef000c4a80');a.branch('6700','drop');a.label('store');a.emit('700126802746000442ab0008');a.emit('202f004c2740000c');a.branch('6000','end');a.label('drop');a.emit('52b947be5c08');a.label('end');restoreall(a);a.emit('4e75');add('start_voice',ON,a,512)
# Pump pending releases whenever the stock MIDI task reaches its output stage.
a=Asm();saveall(a);absolute(a,'45f9',RECS);a.emit('7c08');a.label('loop');a.emit('2f0a');absolute(a,'4eb9',SERVICE);a.emit('588f45ea00105386');a.branch('6600','loop');restoreall(a);a.emit('4e75');add('pump_releases',PUMP,a,256)
# Called from inside E06's 80-byte tail frame; its inherited 36-byte arp frame
# holds caller A3 at +108 and original track at +120, before this call/save.
a=Asm();saveall(a);a.emit('20174a80');a.branch('6b00','end');a.emit('202f00bc0c8000000004');a.branch('6400','end');absolute(a,'41f9',MARKERS);a.emit('222f00b021810c00');a.label('end');restoreall(a);a.emit('4e75');add('mark_arp_event',MARK,a,256)
a=Asm();a.emit('202effa43481');saveall(a);a.emit('2017484002800000ffff220071ab00102f002f012f0b2f02202eff802f00');absolute(a,'4eb9',ON);a.emit('4fef0014');restoreall(a);absolute(a,'4ef9',0x4009e936);add('accepted_voice_hook',START,a,256)
a=Asm();a.emit('1181b8021181b803');saveall(a);a.emit('2f17');absolute(a,'4eb9',OFF);a.emit('588f');restoreall(a);absolute(a,'4ef9',0x4009f0ce);add('allocator_release_hook',REL1,a,128)
a=Asm();saveall(a);a.emit('2f2f0054');absolute(a,'4eb9',OFF);a.emit('588f');restoreall(a);a.emit('79280006d8b941393710');absolute(a,'4ef9',0x4009fa60);add('gate_release_hook',REL2,a,128)
a=Asm();absolute(a,'4eb9',PUMP);a.emit('1039419b14ec');absolute(a,'4ef9',0x400f4c84);add('MIDI_task_pump_hook',POLL,a,128)
a=Asm();saveall(a)
for i in range(4):absolute(a,'42b9',MARKERS+i*4)
restoreall(a);a.emit('242b00442f0b');absolute(a,'4ef9',0x4009d7de);add('retire_event_marker',CLEAR,a,128)
# Rebuild only a disposable copy of the E06 tail helper, without writing its
# image/payload files. The extra call preserves the original result and frame.
src=Path('work/build-E06-degree-overlay.py').read_text().split('oldpayload=')[0]
src=src.replace("a.label('restore');a.emit('242f0008", "a.label('restore');absolute(a,'4eb9',"+str(MARK)+");a.emit('242f0008")
ns={};exec(src,ns);tail=ns['hook'];assert len(tail)<256
blob=bytearray(0xb00)
for addr,code in parts:blob[addr-BASE:addr-BASE+len(code)]=code
Path('work/os144/PC_ONLY-synth-arp-MIDI-code.bin').write_bytes(blob);Path('work/os144/PC_ONLY-synth-arp-MIDI-tail.bin').write_bytes(tail)
main=Path('work/os144/E06-PC-main.bin').read_bytes();hooks=[]
for site,length,target in [(0x4009e930,6,START),(0x4009f0c6,8,REL1),(0x4009fa56,10,REL2),(0x400f4c7e,6,POLL),(0x4009d7d8,6,CLEAR)]:hooks.append({'site':site,'length':length,'target':target,'previous':main[site-0x40000400:site-0x40000400+length].hex(),'replacement':'4ef9'+struct.pack('>I',target).hex()+'4e71'*((length-6)//2)})
cfg={'PC_only':True,'firmware_modified':False,'base':BASE,'bytes':len(blob),'state':STATE,'state_bytes':160,'records':RECS,'markers':MARKERS,'regions':regions,'hooks':hooks,'tail':{'base':0x47be0c00,'bytes':len(tail)},'route':'DIN only; configured synth-track channels; MIDI output selection permits new note-on, stored destination releases remain drainable','initialization':'Host installs code and clears/seeds private state in this disposable PC overlay; native startup copying is not yet implemented','limits':['New executable/private RAM placement is not owned/certified for hardware.','USB output and reset/shutdown cleanup remain outside this prototype.','Ring preflight is based on stock driver arithmetic; physical DMA timing remains unverified.']}
Path('work/os144/PC_ONLY-synth-arp-MIDI-layout.json').write_text(json.dumps(cfg,indent=2));print('PC MIDI code bytes',sum(r['bytes'] for r in regions),'state',cfg['state_bytes'],'tail',len(tail))
