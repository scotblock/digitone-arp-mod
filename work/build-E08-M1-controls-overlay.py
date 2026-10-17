"""Disposable native UI overlay. Not integrated into a firmware package."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
native=json.loads(Path('work/os144/E08-PC-install-layout.json').read_text());S=native['state'];B=0x47be5e00
SEL=B;HANDLE=B+0x80;OPEN=B+0x100;DRAW=B+0x200;TURN=B+0x500;KEY=B+0x700;ENTRY=B+0x800;CONSUMER=B+0xa00;STR=B+0xc00
READ=0x47be5800;WRITE=READ+0x100;VALID=0x47be5d00
main=Path('work/os144/E08-PC-layout-main.bin').read_bytes();blob=bytearray(8192);regions=[];hooks=[]
def absop(a,op,v):absolute(a,op,v)
def js(a,v):absop(a,'4eb9',v)
def jmp(a,v):absop(a,'4ef9',v)
def ui_save(a):save(a);assert a.code[-4:]==bytes.fromhex('46fc2700');a.code[-4:]=bytes.fromhex('4e714e71')
def add(name,addr,a,limit):
 code=a.done();assert len(code)<=limit,(name,len(code),limit);blob[addr-B:addr-B+len(code)]=code;regions.append({'name':name,'base':addr,'bytes':len(code)})
def hook(site,target,length=8):
 original=main[site-0x40000400:site-0x40000400+length]
 hooks.append({'site':site,'target':target,'length':length,'original':original.hex(),'replacement':(bytes.fromhex('4ef9')+struct.pack('>I',target)+bytes.fromhex('4e71')*((length-6)//2)).hex()})
def conditional(a,site):
 ui_save(a);js(a,SEL);a.emit('0c8000000004');a.branch('6600','stock')
def stock_tail(a,site,length=8):
 a.label('stock');restore(a);a.emit(main[site-0x40000400:site-0x40000400+length].hex());jmp(a,site+length)
def page_conditional(a):
 ui_save(a);a.emit('206f0044202802c80c804d314352');a.branch('6600','stock')
def done_void(a):restore(a);a.emit('4e75')
# Global UI selection and MIDI-specific handle: no synth getter.
a=Asm();js(a,0x40149fba);a.emit('0680000000302f00');js(a,0x4002c6ba);a.emit('588f4e75');add('selected_track',SEL,a,128)
a=Asm();js(a,0x40149fba);a.emit('06800000025042a72f00');js(a,0x4001dd1a);a.emit('508f4e75');add('M1_handle',HANDLE,a,128)
# M1 FUNC+SYN2 reaches this modifier branch and opens the stock view shell
# with custom handlers. Bare SYN2 is consumed by the outer MIDI page selector.
a=Asm();ui_save(a);a.emit('202f00300c8000000016');a.branch('6600','original');js(a,SEL);a.emit('0c8000000004');a.branch('6600','original');restore(a);jmp(a,0x4003fc42)
a.label('original');restore(a);a.emit('4a03');a.branch('6600','chord');a.emit('42a7486cfff2');jmp(a,0x4003fb92);a.label('chord');jmp(a,0x4003fb9c);add('M1_SYN2_open',OPEN,a,256);hook(0x4003fb8a,OPEN)
texts={};cursor=STR
for name,text in [('title','M1 MIDI ARP'),('mode','A MODE'),('rate','B RATE'),('gate','C GATE'),('value','%s'),('percent','%d%%'),('off','OFF'),('up','UP'),('footer','NO: BACK')]+[(f'r{i}',t) for i,t in enumerate(native['rate_labels'])]:
 data=text.encode()+b'\0';texts[name]=cursor;blob[cursor-B:cursor-B+len(data)]=data;cursor+=len(data)
cursor=(cursor+3)&~3;table=cursor
for i in range(8):blob[cursor-B:cursor-B+4]=struct.pack('>I',texts[f'r{i}']);cursor+=4
def draw(a,text,y,arg=None,x=64):
 if arg:a.emit(arg)
 absop(a,'4879',texts[text]);a.emit('48780002487800'+f'{y:02x}'+'487800'+f'{x:02x}');absop(a,'4879',0x418e934c);a.emit('2f0c');js(a,0x400de120);a.emit('4fef'+('001c' if arg else '0018'))
a=Asm();page_conditional(a);a.emit('286f0048');js(a,HANDLE);a.emit('2f00');js(a,READ);a.emit('588f2400');draw(a,'title',58)
a.emit('2202028100000400');a.branch('6700','off');absop(a,'263c',texts['up']);a.branch('6000','mode');a.label('off');absop(a,'263c',texts['off']);a.label('mode');draw(a,'mode',46,x=26);draw(a,'value',46,'2f03',x=96)
a.emit('2602ee8b028300000007');absop(a,'41f9',table);a.emit('26303c00');draw(a,'rate',32,x=26);draw(a,'value',32,'2f03',x=96);a.emit('260202830000007f');draw(a,'gate',18,x=26);draw(a,'percent',18,'2f03',x=96);draw(a,'footer',2);done_void(a);stock_tail(a,0x40051390);add('M1_controls_render',DRAW,a,768);hook(0x40051390,DRAW)
# Entry skips stock synth arp LED/mode accessor for M1.
a=Asm();ui_save(a);js(a,SEL);a.emit('0c8000000004');a.branch('6500','stock');done_void(a);stock_tail(a,0x40051f00);add('M1_controls_entry',ENTRY,a,256);hook(0x40051f00,ENTRY)
# Encoder events arrive in the native view format (+c id, +10 signed delta).
a=Asm();page_conditional(a);js(a,SEL);a.emit('0c8000000004');a.branch('6600','finished');a.emit('246f0048202a000c0c8000000001');a.branch('6500','finished');a.emit('0c8000000003');a.branch('6200','finished');a.emit('262a0010');a.branch('6700','finished');a.emit('2a00');js(a,HANDLE);a.emit('28402f00');js(a,READ);a.emit('588f26002200028100000400e089e4892400ee8a02820000000702830000007f0c8500000001');a.branch('6700','mode');a.emit('0c8500000002');a.branch('6700','rate');a.emit('d6aa00104a83');a.branch('6e00','gate_high');a.emit('7601');a.label('gate_high');a.emit('0c8300000063');a.branch('6f00','write');a.emit('7663');a.branch('6000','write')
a.label('mode');a.emit('4aaa0010');a.branch('6e00','up');a.emit('7200');a.branch('6000','write');a.label('up');a.emit('7201');a.branch('6000','write')
a.label('rate');a.emit('4aaa0010');a.branch('6e00','faster');a.emit('5382');a.branch('6000','clamp_rate');a.label('faster');a.emit('5282');a.label('clamp_rate');a.emit('4a82');a.branch('6c00','rate_hi');a.emit('7400');a.label('rate_hi');a.emit('0c8200000007');a.branch('6f00','write');a.emit('7407')
a.label('write');a.emit('2f032f022f012f0c');js(a,WRITE);a.emit('4fef00104a80');a.branch('6700','finished');a.emit('42a72f0c');js(a,0x4014eff8);a.emit('508f2f0c');js(a,READ);a.emit('588f');absop(a,'23c0',S+324);a.emit('7002');absop(a,'23c0',S+320)
a.emit('2f2f0044');js(a,0x400e539e);a.emit('588f');a.label('finished');a.emit('70012f400000');done_void(a);stock_tail(a,0x40051928);add('M1_controls_turn',TURN,a,512);hook(0x40051928,TURN)
# Only NO/page buttons close this MIDI page; no synth arp shortcuts/copy.
a=Asm();page_conditional(a);a.emit('246f0044206f00482228001008010000');a.branch('6700','pass');a.emit('2028000c0c800000000e');a.branch('6700','close');a.emit('0c8000000014');a.branch('6500','pass');a.emit('0c8000000019');a.branch('6300','close');a.emit('0c800000002a');a.branch('6500','pass');a.emit('0c800000002d');a.branch('6200','pass');a.label('close');a.emit('20522f0a206800284e90588f');a.label('pass');a.emit('70002f400000');done_void(a);stock_tail(a,0x400522be);add('M1_controls_key',KEY,a,256);hook(0x400522be,KEY)
# Native MIDI consumer applies the tagged mode/rate/gate together, masked.
a=Asm();save(a);a.emit('20120c8000000002');a.branch('6600','pending');a.emit('206a00044a88');a.branch('6700','pending');a.emit('70003028066c2f00');js(a,VALID);a.emit('588f4a80');a.branch('6600','context_valid');a.emit('203c0000a932');a.label('context_valid');absop(a,'23c0',S+324);a.emit('7002');absop(a,'23c0',S+320);a.label('pending');absop(a,'2039',S+320);a.emit('0c8000000002');a.branch('6600','old');absop(a,'2f39',S+324);js(a,VALID);a.emit('588f4a80');a.branch('6700','clear');a.emit('2800220002810000007f2f01ee880280000000072f00');js(a,native['entries']['configure']);a.emit('508f4a80');a.branch('6700','clear');a.emit('2004028000000400e088e488');absop(a,'23c0',S+4);a.branch('6000','clear')
a.label('old');a.emit('4a80');a.branch('6700','ready');absop(a,'2f39',S+316);absop(a,'2f39',S+312);js(a,native['entries']['configure']);a.emit('508f');a.label('clear');absop(a,'42b9',S+320);a.label('ready');a.emit('2f0a');js(a,native['entries']['dispatch']);a.emit('588f2f400028');restore(a);a.emit('2012bc80');a.branch('6600','other');jmp(a,0x400f40ba);a.label('other');jmp(a,0x400f4126);add('M1_settings_consumer',CONSUMER,a,512)
old=bytes.fromhex('4ef9')+struct.pack('>I',native['entries']['consumer']);hooks.append({'site':0x400f40b4,'target':CONSUMER,'length':6,'original':old.hex(),'replacement':(bytes.fromhex('4ef9')+struct.pack('>I',CONSUMER)).hex()})
# Tag the allocated view after its native constructor, before publication.
a=Asm();ui_save(a);a.emit('202f00300c8000000016');a.branch('6600','end');a.emit('206f00084a88');a.branch('6700','end');a.emit('203c4d314352214002c8');a.label('end');restore(a);a.emit('2f02240e0682fffffff0');jmp(a,0x4003fc60);add('mark_M1_view',B+0xe80,a,128);hook(0x4003fc56,B+0xe80,10)
# The stock countdown must not change the MIDI-view identity tag.
a=Asm();page_conditional(a);done_void(a);stock_tail(a,0x40052438,10);add('M1_view_tick',B+0xf20,a,128);hook(0x40052438,B+0xf20,10)
# Synth arp copy/clear/paste callbacks must not run for the tagged MIDI view.
for i,site in enumerate([0x4005200c,0x4005210e,0x400521e8]):
 a=Asm();page_conditional(a);a.emit('70002f400000');done_void(a);stock_tail(a,site);addr=B+0xd00+i*0x80;add('refuse_synth_shortcut_'+str(i),addr,a,128);hook(site,addr)
# Observe the already-initialized UI root's current M1 data. Never call its
# lazy constructor from this hook. Publish only when data identity/word changes.
a=Asm();save(a);absop(a,'2039',S);a.emit('0c804d314131');a.branch('6600','end');absop(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','end');absop(a,'2079',0x419f0de0);a.emit('4a88');a.branch('6700','end');a.emit('d1fc00000ff820100c8040193b90');a.branch('6600','end');a.emit('226800104a89');a.branch('6700','end');a.emit('70003029009e2f00');js(a,VALID);a.emit('588f4a80');a.branch('6600','valid');a.emit('203c0000a932');a.label('valid');a.emit('28002009');absop(a,'b0b9',S+328);a.branch('6600','publish');a.emit('2004');absop(a,'b0b9',S+332);a.branch('6700','end');a.label('publish');a.emit('2009');absop(a,'23c0',S+328);absop(a,'23c4',S+332);absop(a,'23c4',S+324);a.emit('7002');absop(a,'23c0',S+320);a.label('end');restore(a);a.emit(main[0x4014a056-0x40000400:0x4014a05e-0x40000400].hex());jmp(a,0x4014a05e);add('observe_M1_binding',B+0x1080,a,256);hook(0x4014a056,B+0x1080)
Path('work/os144/E08-PC-M1-controls.bin').write_bytes(blob)
c={'PC_only':True,'base':B,'bytes':len(blob),'regions':regions,'data_range':[STR,cursor],'hooks':hooks,'state':S,'integrated_into_firmware':False,'controls':['MODE OFF/UP','RATE eight divisions','GATE 1..99 percent'],'storage_candidate':{'runtime_word':0x9e,'serialized_word':0xa6}}
Path('work/os144/E08-PC-M1-controls-layout.json').write_text(json.dumps(c,indent=2));print('Native MIDI controls',sum(r['bytes'] for r in regions),'bytes')
