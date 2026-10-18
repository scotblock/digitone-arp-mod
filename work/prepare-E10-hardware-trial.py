"""Freeze the PC-tested E10 bytes for a manual, controlled hardware trial."""
from pathlib import Path
import sys,json,hashlib,shutil,zipfile,subprocess,tempfile
ROOT=Path.cwd();repo=ROOT/'github/digitone-arp-mod'
sys.path.insert(0,str(repo/'release-tools'))
from build_patch import make_patch
from apply_patch import reconstruct
sha=lambda b:hashlib.sha256(b).hexdigest()
proof=json.loads((ROOT/'outputs/Digitone-E10-PC-package-workflow-verification.json').read_text(encoding='utf-8'))
integration=json.loads((ROOT/'outputs/Digitone-E10-PC-package-integration.json').read_text(encoding='utf-8'))
receiver=json.loads((ROOT/'outputs/Digitone-E10-startup-DIN-checks.json').read_text(encoding='utf-8'))
assert proof['passed'] and integration['passed'] and receiver['passed']
source=ROOT/'work/os144/PC_ONLY-E10-package-loader-test.syx';data=source.read_bytes()
assert sha(data)==proof['candidate_sha256']==integration['candidate_sha256']==receiver['image_sha256']
stock_path=ROOT/'outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx';stock=stock_path.read_bytes()
assert sha(stock)=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
out=ROOT/'outputs/E10-hardware-trial';out.mkdir(exist_ok=True)
name='Digitone_OS1.44E10_M1_STEPS_HARDWARE_TRIAL.syx'
def frozen(path,content):
 if path.exists():assert path.read_bytes()==content,('Refusing to replace a different trial artifact',str(path))
 else:
  with path.open('xb') as f:f.write(content)
frozen(out/name,data)
readme='''# E10 — controlled Digitone hardware trial

18 October 2026. Original Digitone / Digitone Keys, OS 1.44 only.

This is an experimental trial candidate, not a hardware-certified release. Its
bytes are identical to the E10 package that passed the PC loader, startup,
playback and edit/save/restart/recall tests. Renaming the file adds no code.
No device was contacted while preparing this folder. The startup screen may
still say 1.44; identify this build by its file/hash, not that display.

## What changes

E10 retains E09A's synth arp scale-degree behavior and synth/M1 output routing.
It adds M1's 1–16-step scale-degree offsets, rests, explicit root/scale controls
and per-pattern project storage. M2–M4 arps and direct trig-key step selection
are not implemented. Main arp MODE/RATE/GATE remain separate from the step page.
Step mode OFF retains the ordinary ascending arp.

## Before this trial

Keep a current external backup of important projects/sounds and use a disposable
project for E10 saves. You previously completed the stock update rehearsal and
successfully recovered stock after E04; no repeat rehearsal is requested here.
Have the official stock 1.44 file available before sending E10. Verify its hash
against RECOVERY.md. An OS file is not a project backup. Returning to stock is not
a promise that custom E10 settings survive stock editing/re-saving a project.

Residual risks are startup failure, stuck/wrong MIDI notes, audio faults,
corrupted project data and a failure requiring service. Physical RAM ownership,
cache execution and worst-case timing are not established by the PC tests.
Stock power handling remains the accepted inherited assumption; no new power
protocol or abrupt-loss guarantee is claimed. E04's prior successful stock
recovery does not guarantee recovery from every failure.

## Install using the rehearsed startup MIDI route

1. Close Ableton, loggers and other MIDI apps. Connect Rubix22 USB to the PC and
   **Rubix22 MIDI OUT → Digitone MIDI IN**. Disconnect Digitone USB during this
   transfer; leave audio monitoring low.
2. Hold **FUNC** while powering on; select **TRIG 4: OS UPGRADE**.
3. In Elektron Transfer open **SYSEX TRANSFER → OS Upgrade via device startup
   menu**, choose the Rubix22 MIDI interface as instructed, and select
   `Digitone_OS1.44E10_M1_STEPS_HARDWARE_TRIAL.syx` from this folder.
4. Follow Transfer/device prompts through completion. Do not interrupt erase or
   programming. The file's 1,614,496 bytes alone require about 8.6 minutes at
   standard MIDI wire speed; sender pauses/programming add time. A long transfer
   alone is not a hang. Do not use a fixed timeout to power-cycle an update.

The startup route requires physical MIDI, not device USB. Sources:
[Elektron Transfer guidance](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer),
[Digitone manual, printed page 81](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf).

## First checkpoint — boot and ordinary operation

After update completion, first confirm that the logo clears and the normal
interface appears. Check normal synth sound, RECORD/sequence entry, TRIG/SYN1/
SYN2/FLTR/AMP/LFO pages on synth and MIDI tracks, and Stop. Report this result
before expanding the test. A persistent logo, broken menus or failed RECORD is
a failed checkpoint; use RECOVERY.md rather than trying resets or another mod.

## Second checkpoint — M1 step playback

Reconnect the preferred MIDI monitoring connection after installation. Avoid
routing MIDI back to the Digitone. Select M1 and set an external receiver/Ableton
to its output channel. Check DIN and USB separately to avoid recording duplicate
messages when both paths feed the same track.

From an ordinary M1 parameter page, press **FUNC + SYN2**. Set the main arp to
UP, a moderate rate such as 1/16 and gate 50. Turn **D clockwise** to the step
page. These are the step-page encoders:

| Encoder | Setting |
| --- | --- |
| A | Root |
| B | Scale |
| C | Length, 1–16 |
| D counterclockwise | Return to main arp page |
| E | Select step |
| F | Selected step's offset, -24 to +24 scale degrees |
| G | Selected step's rest on/off |
| H | Step sequence on/off |

Choose C / Ionian, length 4, offsets **0, 1, 2, 3**, rest on step 3 only, and
step sequence ON. Holding a single C should produce **C, D, silence, F** per
cycle. Octave labels differ between applications. Release the note and press
Stop: the last note must end. Repeat using a sequencer trig long enough to
contain several arp pulses. Keep the synth arp working as before.

## Third checkpoint — pattern ownership and saving

In a second disposable pattern use C / Ionian, length 4, offsets **0, 2, 4, 6**,
no rests: a single C should produce **C, E, G, B**. Alternate the two patterns,
including during playback, and wait for the pattern change to complete. Check
that offsets/rests belong to the receiving pattern and notes end on release/Stop.

Save the project to an unused slot, reload it and check both programs. Then do
an ordinary completed shutdown/restart and reload the saved project. For a
complete restart the manual specifies at least 30 seconds off before power-on;
this is not an instruction to interrupt an update. Recheck both programs.
On disposable patterns, copy/paste and undo should carry/restore the program;
pattern trig clear/undo retains arp settings, following the stock behavior.
Do not deliberately cut power during saving or use factory/empty reset as tests.

Record pass/fail and exact steps in TRIAL_RESULTS.md. Stop on a new freeze,
menu error, stuck note, wrong recall or repeatable audio fault. No further
stress test is needed until these three checkpoints pass.

## Patch ZIP alternative

The local SYX is ready as a trial file. The accompanying patch ZIP is for sharing
without a full firmware image. Extract it into a writable folder, double-click
Create Firmware.cmd, and supply your own exact official OS 1.44 SYX. Python
3.10+ is required. The tool verifies input/output hashes, refuses overwrites and
never sends MIDI or USB. Automatic GitHub source ZIPs are not this patch package.

No GitHub release or hardware update was performed by this preparation.
'''
recovery='''# E10 stock recovery

Use the untouched official original Digitone / Digitone Keys OS 1.44 file:
`Digitone_and_Digitone_Keys_OS1.44_STOCK.syx`.

Required SHA-256:
`d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`.

The verified local copy is in `outputs/stock-recovery/` in this workspace. The
shareable patch ZIP does not include stock firmware or project backups.

If E10 fails after the update has completed, use the previously rehearsed route:
Rubix22 MIDI OUT to Digitone MIDI IN; hold FUNC at power-on; TRIG 4 OS UPGRADE;
Elektron Transfer SYSEX TRANSFER / OS Upgrade via device startup menu; select
**the official stock file**, then follow all prompts through completion.
Use physical MIDI for this route. Do not interrupt active erase/programming.
If an update reports a failure, preserve its exact message/stage; do not invent
a timeout-based power-cycle procedure. If the startup menu is unavailable or
stock recovery fails, stop and seek Elektron support/service.

EMPTY RESET, FACTORY RESET and FORMAT +DRIVE are not OS rollback. Avoid them.
Stock recovery does not guarantee preservation of custom E10 settings; keep the
external backup separate and do not use important projects for the trial.

[Official startup-update guidance](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer)
'''
results='''# E10 hardware trial record

Candidate SHA-256: bec5b8bbb71a17a96a5acd30962166e6d38b57e0f4c72c7a81ccf7d8e082b4c7
Device / date:
Previous installed build:
External backup location:
Update completion / messages:
Logo clears / normal interface:
Ordinary synth playback / RECORD / menus / Stop:
M1 single-note C-D-rest-F:
M1 sequencer-triggered arp:
DIN note output and final note-off:
USB note output and final note-off:
Two-pattern playback handoff:
Named save / reload / ordinary restart recall:
Disposable copy / undo / trig clear / undo:
Any audio faults, wrong notes or menu problems:
Stock recovery needed / outcome:

Record observations only; a successful short trial is not full certification.
'''
for n,t in [('README.md',readme),('RECOVERY.md',recovery),('TRIAL_RESULTS.md',results)]:frozen(out/n,t.encode('utf-8'))
meta,patch=make_patch(stock,data,'E10',name,'Experimental controlled hardware-trial candidate; PC validated, hardware trial pending')
frozen(out/'E10.darp',patch)
manifest={'patch_metadata':meta,'patch_sha256':sha(patch),'validation':{'reconstructed_byte_exact':True,'identical_to_PC_tested_container':True,'startup_DIN_model_cases_passed':4,'hardware_trial_pending':True,'hardware_certified':False,'device_updated':False},'tested_container_sha256':sha(data),'evidence':{'PC_package':'Digitone-E10-PC-package-integration.json','PC_user_workflows':'Digitone-E10-PC-package-workflow-verification.json','startup_updater':'Digitone-E10-startup-DIN-checks.json'}}
frozen(out/'manifest.json',(json.dumps(manifest,indent=2)+'\n').encode('utf-8'))
files={'E10.darp':patch,'manifest.json':(out/'manifest.json').read_bytes(),'README.md':readme.encode('utf-8'),'RECOVERY.md':recovery.encode('utf-8'),'TRIAL_RESULTS.md':results.encode('utf-8'),'apply_patch.py':(repo/'release-tools/apply_patch.py').read_bytes(),'Create Firmware.cmd':(repo/'release-tools/Create Firmware.cmd').read_bytes()}
zip_path=out/'Digitone-OS1.44-E10-hardware-trial-patch.zip'
import io
buffer=io.BytesIO()
with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n,b in sorted(files.items()):
  entry=zipfile.ZipInfo(n,date_time=(2026,10,18,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o100644<<16;z.writestr(entry,b)
frozen(zip_path,buffer.getvalue())
with tempfile.TemporaryDirectory(prefix='E10-trial-patcher-',dir=ROOT/'work') as tmp:
 tmp=Path(tmp)
 with zipfile.ZipFile(zip_path) as z:
  assert z.testzip() is None and set(z.namelist())==set(files);z.extractall(tmp)
 run=subprocess.run([sys.executable,str(tmp/'apply_patch.py'),'--stock',str(stock_path)],capture_output=True,text=True)
 assert run.returncode==0,run.stdout+run.stderr
 assert (tmp/name).read_bytes()==data
 repeat=subprocess.run([sys.executable,str(tmp/'apply_patch.py'),'--stock',str(stock_path)],capture_output=True,text=True)
 assert repeat.returncode!=0 and (tmp/name).read_bytes()==data
 assert reconstruct(stock,patch)[1]==data
checks='\n'.join(sha((out/n).read_bytes())+'  '+n for n in [name,'E10.darp',zip_path.name,'manifest.json'])+'\n'
frozen(out/'SHA256SUMS.txt',checks.encode('utf-8'))
report={'passed':True,'trial_candidate_prepared':True,'candidate':str(out/name),'candidate_sha256':sha(data),'bytes':len(data),'identical_to_tested_container':True,'firmware_code_changed':False,'patch_zip':str(zip_path),'patch_zip_sha256':sha(zip_path.read_bytes()),'patcher_cli_reconstructs_exact_bytes':True,'patcher_refuses_overwrite':True,'stock_recovery_sha256':sha(stock),'startup_DIN_checks_passed':4,'device_contacted':False,'hardware_trial_pending':True,'hardware_certified':False,'github_release_published':False,'limitations':['Modeled receiver uses SRAM code, first/end UART IRQ and recovered data callback; flash geometry/erase/program are fixtures.','PC loader/state handoffs, native startup and user workflows pass; physical RAM/cache/timing and all project/reset routes remain unproven.','Stock power handling is the accepted inherited assumption, not a guaranteed abrupt-loss recovery claim.']}
(ROOT/'outputs/Digitone-E10-hardware-trial-preparation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'prepared':str(out),'candidate_sha256':sha(data),'patch_bytes':len(patch),'patcher_roundtrip':True,'device_updated':False},indent=2))
