"""Native panel controls for the PC-only M1 synth-style editor overlay."""
from pathlib import Path
import json,os,sys,shutil,traceback,struct,hashlib
prefix=Path('work/generated-E10-package-workflow.py').read_text(encoding='utf-8').split('source_paths=paths;root=')[0]
exec(compile(prefix,'E11-packaged-base-definitions','exec'))
from emu import sparse,cfisa
# Only the instruction validator is imported; its old experiment is not run.
audit={};exec(compile(Path('work/audit-E04-startup-ISA.py').read_text(encoding='utf-8').split('\nregions=')[0],'E11-ISA-rules','exec'),audit)
proof=json.loads(Path('outputs/Digitone-E10-PC-package-workflow-patterns.json').read_text(encoding='utf-8'));assert proof['passed']
config=json.loads(Path('work/os144/PC_ONLY-E11-synth-style-editor.json').read_text(encoding='utf-8'));code=Path('work/os144/PC_ONLY-E11-synth-style-editor.bin').read_bytes()
source_paths=paths;root=Path('work/E11-synth-style-editor').resolve();root.mkdir(exist_ok=True);paths=bs.FirmwarePaths(str(root),syx.name,source_paths.devices_dir)
shutil.copytree(source_paths.sections,paths.sections,dirs_exist_ok=True);shutil.copytree(source_paths.overlay,paths.overlay,dirs_exist_ok=True);shutil.copyfile(syx,paths.syx)
with open(proof['private_card'],'rb') as src,open(paths.card,'wb') as dst:
 sparse.make_sparse(dst);sparse.extend(dst,Path(proof['private_card']).stat().st_size)
 while chunk:=src.read(1024*1024):
  if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
os.environ.update(paths.env());X=native['E10']['state'];BANK=native['E10']['bank'];PM=native['persistence']['meta'];BM=native['binding']['meta']
base_install=install;payload=bytearray(payload)
out.update(passed=False,PC_only=True,overlay_installed_by_host=True,settings_host_written=False,steps=[],checks=[],failure=None)
def install(s):
 base_install(s)
 for page in range(config['base'],config['base']+len(code),4096):s.m.ensure(page)
 s.m.uc.mem_write(config['base'],code)
 for region in config['regions']:
  part=code[region['base']-config['base']:region['base']-config['base']+region['bytes']];offset=0
  while offset<len(part):
   ins=cfisa.decode(lambda n:int.from_bytes(part[offset+n:offset+n+2],'big'),region['base']+offset)
   assert ins.length>0 and offset+ins.length<=len(part) and not ins.flags&(cfisa.ILLEGAL|cfisa.LINEF|cfisa.FPU) and not audit['move_restriction'](int.from_bytes(part[offset:offset+2],'big')),(region,offset,ins)
   offset+=ins.length
  s.m.install_isa_patches_scoped(part,region['base'])
 for patch in config['patches']:
  assert bytes(s.m.uc.mem_read(patch['site'],6)).hex()==patch['before']
  replacement=bytes.fromhex(patch['after']);s.m.uc.mem_write(patch['site'],replacement);off=patch['site']-native['base'];payload[off:off+6]=replacement
s=Session(proof['checkpoints']['reloaded-two-patterns'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
def tap(key,wait=120):s.tap(s.code(key),hold_ms=80,after_ms=wait)
def combo(key):s.press(s.code('FUNC'));s.run_ms(80);tap(key);s.release(s.code('FUNC'));s.run_ms(150)
def choose(n):s.press(s.code('PTN'));s.run_ms(80);tap(str(n),80);s.release(s.code('PTN'));s.run_ms(350)
def owner():return rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x1008)
def fields():return [rd(s.m.uc,X+i) for i in [4,8,16,20,24]]+[bytes(s.m.uc.mem_read(X+32,16)).hex()]
def record(slot):
 r=bytes(s.m.uc.mem_read(BANK+32*slot,32));assert r[:4]==b'MS10' and sum(r[:28])==int.from_bytes(r[28:],'big');return r
def mark(label):
 out['steps'].append(dict(label=label,fields=fields(),slot=rd(s.m.uc,BM+8),owner=hex(owner()),bound_owner=hex(rd(s.m.uc,X+28))))
 if s.frames:panel.write_png(s.frames[-1][1],'outputs/E11-'+label+'.png',4)
 print(label,fields(),flush=True)
try:
 if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
  t=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);t.now=s.pits.now;s.pits.sources=s.pits.sources+(t,)
 s.run_ms(300);tap('STOP')
 for _ in range(3):tap('NO',80)
 if rd(s.m.uc,rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x40)+8)<4:tap('MIDI')
 tap('T1');choose(3);tap('SYN1');combo('SYN2')
 if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=150)
 assert rd(s.m.uc,X+56)==1 and rd(s.m.uc,X+28)==owner()
 before=bytes(s.m.uc.mem_read(BANK,4096));mark('opened')
 # E edits offset, F length; cursor arrows and Up/Down mirror the synth workflow.
 for _ in range(16):
  if rd(s.m.uc,X+16)==0:break
  tap('LEFT',60)
 old=bytes(s.m.uc.mem_read(X+32,16));s.turn(5,16,after_ms=150)
 assert s.m.uc.mem_read(X+32,1)[0]==old[0]+1 and rd(s.m.uc,X+16)==0
 tap('RIGHT');assert rd(s.m.uc,X+16)==1
 s.turn(5,-16,after_ms=150);assert s.m.uc.mem_read(X+33,1)[0]==255
 tap('DOWN');assert rd(s.m.uc,X+20)&2==0
 r=record(2);tap('DOWN');assert record(2)==r,'Down must remain a rest, not toggle it'
 tap('UP');assert rd(s.m.uc,X+20)&2
 tap('UP');assert rd(s.m.uc,X+20)&2
 mark('arrows_E_offset');out['checks'].append('Native Left/Right select; E edits only the selected offset; Up/Down are idempotent enable/rest.')
 oldlen=rd(s.m.uc,X+8);s.turn(6,-16,after_ms=150);assert rd(s.m.uc,X+8)==oldlen-1
 old=fields();s.turn(3,16,after_ms=100);assert fields()==old,'C is unused on the step page'
 for _ in range(16):
  if rd(s.m.uc,X+8)==4:break
  s.turn(6,-16,after_ms=80)
 for _ in range(16):
  if rd(s.m.uc,X+16)==0:break
  tap('LEFT',60)
 for n in range(4):
  current=int.from_bytes(s.m.uc.mem_read(X+32+n,1),'big',signed=True)
  while current!=n:
   s.turn(5,16 if current<n else -16,after_ms=80);current+=1 if current<n else -1
  tap('UP',80)
  if n==2:tap('DOWN',80)
  if n<3:tap('RIGHT',80)
 s.turn(8,16,after_ms=150)
 assert rd(s.m.uc,X+8)==4 and bytes(s.m.uc.mem_read(X+32,4))==bytes([0,1,2,3]) and rd(s.m.uc,X+20)==0xfffb
 mark('C_D_rest_F_program');saved=record(2)
 assert saved[6]==4 and saved[12:16]==bytes([0,1,2,3]) and int.from_bytes(saved[10:12],'big')==0xfffb
 mirror=0x40555ff4+0x240200+2*0xa00+0x940;assert bytes(s.m.uc.mem_read(mirror,32))==saved
 out['checks'].append('F sets length; programmed 0/1/2/3 with third-step rest is checksummed and mirrored through unchanged E10 persistence.')
 # Right boundary clamps; shortening the sequence clamps its edit cursor.
 tap('RIGHT');assert rd(s.m.uc,X+16)==3
 s.turn(6,-16,after_ms=100);assert rd(s.m.uc,X+8)==3 and rd(s.m.uc,X+16)==2
 s.turn(6,16,after_ms=100);assert record(2)==saved
 # Pattern recall through native menus retains the new edits and original other patterns.
 tap('NO');choose(4);tap('SYN1');combo('SYN2')
 if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=100)
 assert record(3)==before[96:128]
 tap('NO');choose(3);tap('SYN1');combo('SYN2')
 if not rd(s.m.uc,X+56):s.turn(4,16,after_ms=100)
 assert record(2)==saved and bytes(s.m.uc.mem_read(X+32,4))==bytes([0,1,2,3]);mark('pattern_recalled')
 out['checks'].append('Selected-step bounds/length clamp and native pattern recall preserve the expected program.')
 s.turn(4,-16,after_ms=120);assert rd(s.m.uc,X+56)==0;tap('NO');tap('T2');combo('SYN2');s.turn(5,16,after_ms=120);tap('LEFT');tap('DOWN');tap('NO')
 assert bytes(s.m.uc.mem_read(BANK,64))==before[:64] and record(3)==before[96:128] and record(2)==saved
 out['checks'].append('M2 keeps its stock page and does not edit the M1 bank; original A01/A02/A04 records remain unchanged.')
 preserved(s)
 for r in config['regions']:assert bytes(s.m.uc.mem_read(r['base'],r['bytes']))==code[r['base']-config['base']:r['base']-config['base']+r['bytes']]
 assert s.halted is None
 out.update(passed=True,strict_ColdFire_decode_passed=True,additional_state_bytes=0,E10_format_preserved=True,native_panel_events=True,program_record=saved.hex(),firmware_container_created=False,hardware_ready=False)
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 s.close();out['limits']=config['limits'];Path('outputs/Digitone-E11-PC-synth-style-editor.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
if not out['passed']:raise SystemExit(1)
