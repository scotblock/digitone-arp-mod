"""Actual native held-note handoff between the panel-created saved patterns."""
from pathlib import Path
import json,os,shutil,struct,traceback
definitions=Path('work/test-PC-E10-bound-panel-patterns.py').read_text(encoding='utf-8').split('source_paths=paths;root=')[0]
exec(compile(definitions,'E10-bound-handoff-definitions','exec'))
proof=json.loads(Path('outputs/Digitone-E10-PC-bound-panel-patterns.json').read_text());assert proof['passed'] and proof['post_reload_pattern_recall']
source_paths=paths;root=Path('work/E10-bound-running-handoff').resolve();root.mkdir(exist_ok=True)
paths=bs.FirmwarePaths(str(root),syx.name,source_paths.devices_dir)
shutil.copytree(source_paths.sections,paths.sections,dirs_exist_ok=True);shutil.copytree(source_paths.overlay,paths.overlay,dirs_exist_ok=True);shutil.copyfile(syx,paths.syx)
with open(proof['private_card'],'rb') as src,open(paths.card,'wb') as dst:
 sparse.make_sparse(dst);sparse.extend(dst,Path(proof['private_card']).stat().st_size)
 while chunk:=src.read(1024*1024):
  if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
os.environ.update(paths.env());X=native['E10']['state'];BANK=native['E10']['bank'];BM=native['binding']['meta'];PM=native['persistence']['meta']
out.update(steps=[],consumed_recalls=[],bank_host_written=False,settings_host_written=False)
base_install=install
def install(s):
 base_install(s)
 def recalled(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7)
  if rd(u,sp+8)==0:out['consumed_recalls'].append(dict(phase=phase,owner=hex(rd(u,sp+4)),held=rd(u,S+16),arena=rd(u,S+280)))
 s.at(native['binding']['entries']['recall'],recalled)
s=Session(proof['checkpoints']['reloaded-two-patterns'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
def tap(key,wait=120):s.tap(s.code(key),hold_ms=80,after_ms=wait)
def combo(key):
 s.press(s.code('FUNC'));s.run_ms(80);tap(key);s.release(s.code('FUNC'));s.run_ms(120)
def owner():return rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x1008)
def fields():return [rd(s.m.uc,X+i) for i in [4,8,20,24]]+[bytes(s.m.uc.mem_read(X+32,16)).hex()]
def choose(number):
 s.press(s.code('PTN'));s.run_ms(80);tap(str(number),80);s.release(s.code('PTN'));s.run_ms(150)
def mark(label):
 row=dict(label=label,ms=s.now_ms(),UI_owner=hex(owner()),consumed_owner=hex(rd(s.m.uc,S+336)),step_owner=hex(rd(s.m.uc,X+28)),slot=rd(s.m.uc,BM+8),fields=fields(),held=[rd(s.m.uc,S+i) for i in [8,12,16,280]])
 row['arp_config']=[rd(s.m.uc,S+i) for i in [4,304,308,320]];row['settings_word']=int.from_bytes(s.m.uc.mem_read(owner()+158,2),'big')
 if s.frames:panel.write_png(s.frames[-1][1],'outputs/E10-bound-handoff-'+label+'.png',4)
 out['steps'].append(row);print(label,row,flush=True)
try:
 if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
  t=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);t.now=s.pits.now;s.pits.sources=s.pits.sources+(t,)
 before=bytes(s.m.uc.mem_read(BANK,64))
 # Main arp mode/rate/gate remain independent saved native M1 parameters.
 owners={}
 for slot in [2,1]:
  phase='configure_'+str(slot);tap('NO');choose(slot);tap('SYN1');combo('A');combo('SYN2')
  if rd(s.m.uc,X+56):s.turn(4,-16,after_ms=120)
  s.turn(1,16,after_ms=150);s.turn(2,16,after_ms=150)
  # Read actual normalized state; a queued encoder request alone is not proof
  # of mode admission after the native pattern/UI rebinding notifications.
  if not int.from_bytes(s.m.uc.mem_read(owner()+158,2),'big')&0x400:
   s.turn(1,16,after_ms=300)
  owners[slot]=owner();mark('configured_'+str(slot));assert rd(s.m.uc,S+4)==1;tap('NO')
 assert bytes(s.m.uc.mem_read(BANK,64))==before
 mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
 gate=rd(s.m.uc,0x41368d64);s.m.uc.mem_write(0x41368d64,struct.pack('>I',gate|3));out['input_gate_fixture']=dict(before=gate,after=gate|3)
 channel=rd(s.m.uc,0x41368d2c)&15
 def send(data):
  for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*.00032,byte)
  mi.received+=len(data);s.run_ms(60)
 chord=sum(([0x90|channel,n,100] for n in [60,64,67]),[])
 release=sum(([0x80|channel,n,0] for n in [60,64,67]),[])
 phase='A01_held';tap('PLAY');send(chord);s.run_ms(200);mark('A01_held')
 assert rd(s.m.uc,S+16)==3 and rd(s.m.uc,X+28)==owners[1] and fields()==proof['expected_fields'][0]
 old_backing=rd(s.m.uc,0x4138f214);phase='request_A02';choose(2);mark('A02_requested')
 phase='handoff_A02'
 for _ in range(28):
  s.run_ms(250)
  if rd(s.m.uc,S+336)==owners[2] and rd(s.m.uc,X+28)==owners[2] and rd(s.m.uc,0x4138f214)!=old_backing:break
 mark('A02_consumed')
 assert rd(s.m.uc,S+336)==owners[2] and rd(s.m.uc,X+28)==owners[2]
 assert rd(s.m.uc,0x4138f214)!=old_backing and fields()==proof['expected_fields'][1]
 assert rd(s.m.uc,S+16)==3 and any(r['phase']=='handoff_A02' and r['owner']==hex(owners[2]) for r in out['consumed_recalls'])
 out['confirmed_held_handoff']=True
 s.run_ms(400);phase='release';send(release);s.run_ms(300);tap('STOP');mark('released_stop')
 assert [rd(s.m.uc,S+i) for i in [8,16,280]]==[0,0,0]
 assert bytes(s.m.uc.mem_read(BANK,64))==before and s.halted is None
 preserved(s);out.update(passed=True,bank_preserved=True,matching_fields_after_consumed_handoff=True)
except Exception:
 out.update(passed=False,failure=traceback.format_exc());print(out['failure'],flush=True)
finally:
 s.close();out['limits']=['Actual native PTN selection, backing replacement and consumed-owner recall; no code/bank/settings host writes. Input gate is the inherited emulator MIDI fixture.','One held-chord handoff and release/Stop. Physical timing, exceptional resets, copy/clear/undo and broader transition coverage remain separate.']
 Path('outputs/Digitone-E10-PC-bound-running-handoff.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
if not out.get('passed'):raise SystemExit(1)
