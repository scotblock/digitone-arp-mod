"""Native ownership guards, separate PC-only controls blob; E08C stays intact."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
n=json.loads(Path('work/os144/E08C-PC-install-layout.json').read_text());S=n['state']
PUBLISH=0x47be7000;SELECT=0x47be7180;SOURCE=0x47be7280
OWNER=S+336;REQUEST_OWNER=S+340
source=Path('work/build-E08-M1-controls-overlay.py').read_text()

# Replace direct, unprotected publication after the native write/dirty calls.
old="a.emit('588f');absop(a,'23c0',S+324);a.emit('7002');absop(a,'23c0',S+320)"
new="a.emit('588f487800012f002f2c0010');js(a,0x47be7000);a.emit('4fef000c')"
assert source.count(old)==1;source=source.replace(old,new)

# The consumer owns context admission. A valid note-on may supply its own
# parameter block, as stock does. Releases and invalid/unselected sources do
# not take ownership. Context/source selection supersedes stale UI requests.
start=source.index('# Native MIDI consumer applies')
end=source.index('old=bytes.fromhex',start)
consumer=r'''
# Owner-checked native consumer; runs with all registers saved and IPL masked.
a=Asm();save(a);absop(a,'2039',S);a.emit('0c804d314131');a.branch('6600','original');absop(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','original');a.emit('20120c8000000002');a.branch('6600','source_owner')
a.emit('202a00044a80');a.branch('6700','revoke');a.emit('0680000005ce2f00');js(a,0x47be7180);a.emit('588f4a80');a.branch('6600','pending')
a.label('revoke')
for off in [4,8,320,324,328,332,336,340]:absop(a,'42b9',S+off)
js(a,native['entries']['clear']);a.branch('6000','pending')
a.label('source_owner');a.emit('2f0a');js(a,0x47be7280);a.emit('588f4a80');a.branch('6700','pending');a.emit('2f00');js(a,0x47be7180);a.emit('588f')
a.label('pending');absop(a,'2039',S+320);a.emit('0c8000000002');a.branch('6600','clear')
absop(a,'2039',S+340);a.emit('4a80');a.branch('6700','clear');absop(a,'b0b9',S+336);a.branch('6600','clear')
absop(a,'2f39',S+324);js(a,VALID);a.emit('588f4a80');a.branch('6700','clear');a.emit('2800220002810000007f2f01ee880280000000072f00');js(a,native['entries']['configure']);a.emit('508f4a80');a.branch('6700','clear');a.emit('2004028000000400e088e488');absop(a,'23c0',S+4)
a.label('clear');absop(a,'42b9',S+320);a.emit('2f0a');js(a,native['entries']['dispatch']);a.emit('588f2f400028');a.label('original');restore(a);a.emit('2012bc80');a.branch('6600','other');jmp(a,0x400f40ba);a.label('other');jmp(a,0x400f4126);add('M1_settings_consumer',CONSUMER,a,512)
'''
source=source[:start]+consumer+source[end:]

# Automatic rebinding is only admitted when transport, held set and arena are
# quiescent. A short native publisher repeats these checks atomically. Cookies
# update only after successful admission, so a deferred binding retries later.
start=source.index('# Observe the already-initialized UI root')
end=source.index("Path('work/os144/E08-PC-M1-controls.bin')",start)
observer=r'''
a=Asm();save(a);absop(a,'2039',S);a.emit('0c804d314131');a.branch('6600','end');absop(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','end')
absop(a,'2079',S+40);a.emit('4a88');a.branch('6700','end');a.emit('20100c8000000001');a.branch('6700','end')
for off in [8,16,280]:absop(a,'4ab9',S+off);a.branch('6600','end')
absop(a,'2079',0x419f0de0);a.emit('4a88');a.branch('6700','end');a.emit('d1fc00000ff820100c8040193b90');a.branch('6600','end');a.emit('226800104a89');a.branch('6700','end');a.emit('70003029009e2f00');js(a,VALID);a.emit('588f4a80');a.branch('6600','valid');a.emit('203c0000a932');a.label('valid');a.emit('28002009');absop(a,'b0b9',S+328);a.branch('6600','publish');a.emit('2004');absop(a,'b0b9',S+332);a.branch('6700','end')
a.label('publish');a.emit('42a72f042f09');js(a,0x47be7000);a.emit('4fef000c4a80');a.branch('6700','end');a.emit('2009');absop(a,'23c0',S+328);absop(a,'23c4',S+332)
a.label('end');restore(a);a.emit(main[0x4014a056-0x40000400:0x4014a05e-0x40000400].hex());jmp(a,0x4014a05e);add('observe_M1_binding',B+0x1080,a,384)
'''
source=source[:start]+observer+source[end:]

# Assemble the added helpers through the same assembler/environment. Insert
# before file output so all executable regions are in the layout manifest.
helpers=r'''
# publish(data, word, origin[0=automatic,1=panel]) -> admitted.
a=Asm();save(a);absop(a,'2039',S);a.emit('0c804d314131');a.branch('6600','deny');absop(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','deny')
a.emit('242f0044262f0048282f004c0c8400000001');a.branch('6200','deny');a.emit('0c8240000000');a.branch('6500','deny');a.emit('0c8247ffff5c');a.branch('6200','deny');a.emit('2f03');js(a,VALID);a.emit('588f4a80');a.branch('6700','deny')
# Revalidate the currently bound UI record and its normalized value inside the
# same critical section. A preempted/stale read cannot be stamped as a new edit.
absop(a,'2079',0x419f0de0);a.emit('4a88');a.branch('6700','deny');a.emit('d1fc00000ff820100c8040193b90');a.branch('6600','deny');a.emit('226800102009b082');a.branch('6600','deny');a.emit('70003029009e2f00');js(a,VALID);a.emit('588f4a80');a.branch('6600','current_valid');a.emit('203c0000a932');a.label('current_valid');a.emit('b083');a.branch('6600','deny')
absop(a,'2079',S+40);a.emit('4a88');a.branch('6700','owned');a.emit('20100c8000000001');a.branch('6700','owned')
for off in [8,16,280]:absop(a,'4ab9',S+off);a.branch('6600','owned')
absop(a,'23c2',S+336);a.branch('6000','publish')
a.label('owned');a.emit('4a84');a.branch('6700','deny');a.emit('2002');absop(a,'b0b9',S+336);a.branch('6600','deny')
a.label('publish');absop(a,'23c3',S+324);absop(a,'23c2',S+340);a.emit('7002');absop(a,'23c0',S+320);a.emit('7001');a.branch('6000','return')
a.label('deny');a.emit('7000');a.label('return');a.emit('2f400000');done_void(a);add('publish_owned_settings',0x47be7000,a,384)

# Capture settings from a parameter record selected by the actual consumer.
# Retained owner fields are compared as identities, not dereferenced later.
a=Asm();save(a);absop(a,'2039',S);a.emit('0c804d314131');a.branch('6600','deny');absop(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','deny');a.emit('242f00440c8240000000');a.branch('6500','deny');a.emit('0c8247ffff5c');a.branch('6200','deny');a.emit('204270003028009e2f00');js(a,VALID);a.emit('588f4a80');a.branch('6600','valid');a.emit('203c0000a932')
a.label('valid');absop(a,'23c2',S+336);absop(a,'23c2',S+340);absop(a,'23c0',S+324);a.emit('7002');absop(a,'23c0',S+320);a.emit('7001');a.branch('6000','return')
a.label('deny');a.emit('7000');a.label('return');a.emit('2f400000');done_void(a);add('select_consumed_settings_owner',0x47be7180,a,256)

# Eligible M1 note-on -> explicit parameters, otherwise stock cached/default
# binding. This matches stock's +28 override/cache/KitActive source selection.
a=Asm();save(a);a.emit('206f004420100c8000000001');a.branch('6200','deny');a.emit('4aa80004');a.branch('6600','deny');a.emit('202800080c8000000001');a.branch('6600','deny');a.emit('2028000c028000000001');a.branch('6700','deny')
a.emit('262800100c8300000001');a.branch('6500','deny');a.emit('0c8300000008');a.branch('6200','deny');a.emit('2028002c0c8000000002');a.branch('6600','sequence');a.emit('0c8300000001');a.branch('6600','deny');a.branch('6000','notes')
a.label('sequence');a.emit('0c8000000001');a.branch('6600','deny');a.emit('2028001c');a.branch('6f00','deny');a.emit('0c8040000000');a.branch('6400','deny')
a.label('notes');a.emit('7400');a.label('loop');a.emit('7000103028140c8000000080');a.branch('6400','deny');a.emit('5282b483');a.branch('6500','loop')
a.emit('202800284a80');a.branch('6600','return');absop(a,'2039',0x419c5b14);a.emit('4a80');a.branch('6600','return');absop(a,'2039',0x419c5b10);a.emit('4a80');a.branch('6700','deny');a.emit('0680000005ce');a.branch('6000','return')
a.label('deny');a.emit('7000');a.label('return');a.emit('2f400000');done_void(a);add('eligible_source_settings_owner',0x47be7280,a,384)
'''
marker="Path('work/os144/E08-PC-M1-controls.bin')"
assert marker in source;source=source.replace(marker,helpers+'\n'+marker)
source=source.replace('E08-PC-M1-controls.bin','E08D-PC-M1-controls.bin').replace('E08-PC-M1-controls-layout.json','E08D-PC-M1-controls-layout.json')
exec(compile(source,'E08D-guard-builder','exec'))
c=json.loads(Path('work/os144/E08D-PC-M1-controls-layout.json').read_text())
c.update(state_bytes=344,owner_offset=336,request_owner_offset=340,
         entries={'publish':PUBLISH,'select_owner':SELECT,'source_owner':SOURCE},
         limits=['PC-only native code; no hardware certification.','Owner identity is selected on consumed contexts/eligible sources, not UI pattern selection.'])
Path('work/os144/E08D-PC-M1-controls-layout.json').write_text(json.dumps(c,indent=2))
print('Owner fields',hex(OWNER),hex(REQUEST_OWNER),'state end',hex(S+344),'arena',hex(n['arena']))
