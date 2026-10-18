"""Freeze a local experimental E11 UI candidate after its packaged PC checks."""
from pathlib import Path
import json,hashlib,sys,zipfile,io
root=Path.cwd();repo=root/'github/digitone-arp-mod';sys.path.insert(0,str(repo/'release-tools'))
from build_patch import make_patch
from apply_patch import reconstruct
r=json.loads(Path('outputs/Digitone-E11-PC-verification.json').read_text(encoding='utf-8'));d=json.loads(Path('outputs/Digitone-E11-startup-DIN-checks.json').read_text(encoding='utf-8'));assert r['passed'] and d['passed'] and r['candidate_sha256']==d['image_sha256']
sha=lambda b:hashlib.sha256(b).hexdigest();b=Path(r['candidate']).read_bytes();assert sha(b)==r['candidate_sha256']
out=Path('outputs/E11-synth-style-candidate');out.mkdir(exist_ok=True);name='Digitone_OS1.44E11_M1_SYNTH_STYLE_EXPERIMENTAL.syx'
def frozen(path,data):
 if path.exists():assert path.read_bytes()==data,('Refusing different artifact',str(path))
 else:path.write_bytes(data)
frozen(out/name,b)
guide='''# E11 — M1 synth-style step programming

Experimental original Digitone / Digitone Keys OS 1.44 candidate, 18 October 2026.
No physical E11 trial or hardware certification is claimed. Your E10 files remain
unchanged. This changes M1 programming controls, retaining E10 playback and its
per-pattern record format; M2-M4 remain unextended.

Select M1, open FUNC + SYN2, and turn D clockwise for the step page as in E10.
Programming now follows the synth arp workflow:

| Control | Action |
| --- | --- |
| Left / Right | Select the arp step |
| E | Edit that step's scale-degree offset |
| F | Arp sequence length, 1-16 |
| Up | Enable the selected step |
| Down | Make the selected step a rest |
| A / B | Explicit root / scale, retained from E10 |
| D counterclockwise | Back to main MODE / RATE / GATE controls |
| H | Step sequence ON / OFF |

C is unused on the step page; G retains the old rest-control alias. On the main
page the existing controls are unchanged. This does not add the synth arp's other
sorting modes or octave-range engine. The FUNC + SYN2 entry remains different
from the synth arp's FUNC + SYN1 entry.

The strip shows '+' enabled, '-' rest, 'X' selected enabled, '*' selected rest,
and '.' outside the chosen length. The workflow matches the synth editor; the
artwork is not a pixel-identical copy. Offsets retain E06/E10 scale-degree units.

Quick check: C Ionian, length 4, offsets 0/1/2/3, Down on step 3, sequence ON,
main MODE UP. A held single C should give C, D, rest, F. Check release/Stop,
then repeat using a sequencer trig long enough for several arp pulses.

Native PC tests cover the controls, idempotent Up/Down, cursor/length bounds,
pattern recall, exact record checksum/retained mirror and M2 isolation. The
actual E11 stock loader and native copier/init/logo run before the final
keyboard/sequencer playback test. MIDI/USB and other hardware models remain
fixtures; physical code placement/cache/timing and a new full E11 persistence/
reset suite are not established. The unchanged E10 format is not a blanket
physical compatibility guarantee.

For any separate device trial, keep a current project/sound backup, the working
E10 file and official stock 1.44 recovery available. Use a disposable project.
Use the already rehearsed startup-menu DIN route: Rubix22 MIDI OUT to Digitone
MIDI IN; hold FUNC at power-on; TRIG 4 OS UPGRADE; Elektron Transfer's SYSEX
TRANSFER / OS Upgrade via device startup menu, selecting this E11 file.
Physical MIDI is required for that route. Follow Transfer and
the device through completion; never interrupt erase/programming. First check
normal boot, menus, RECORD, ordinary sound and Stop before trying the new editor.
Recover official stock with the rehearsed procedure if startup fails; empty/
factory reset is not OS rollback. No hold-up measurement or power-system
redesign is required; inherited stock power behavior remains the agreed assumption.

[Official startup-update instructions](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer).

The accompanying stock-dependent patch ZIP reconstructs this file from the exact
official 1.44 input; it does not install it. No GitHub release or device update
was performed by this preparation.
'''
frozen(out/'README.md',guide.encode('utf-8'))
stock=Path('outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx').read_bytes();assert sha(stock)=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
meta,patch=make_patch(stock,b,'E11',name,'Experimental synth-style M1 editor; packaged PC checks pass; physical E11 trial pending');assert reconstruct(stock,patch)[1]==b
frozen(out/'E11.darp',patch);frozen(out/'manifest.json',(json.dumps({'patch_metadata':meta,'patch_sha256':sha(patch),'physical_trial_pending':True,'hardware_certified':False},indent=2)+'\n').encode())
files={'README.md':guide.encode(),'E11.darp':patch,'manifest.json':(out/'manifest.json').read_bytes(),'apply_patch.py':(repo/'release-tools/apply_patch.py').read_bytes(),'Create Firmware.cmd':(repo/'release-tools/Create Firmware.cmd').read_bytes()}
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n,data in sorted(files.items()):
  entry=zipfile.ZipInfo(n,date_time=(2026,10,18,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o100644<<16;z.writestr(entry,data)
frozen(out/'Digitone-OS1.44-E11-experimental-patch.zip',buf.getvalue())
with zipfile.ZipFile(out/'Digitone-OS1.44-E11-experimental-patch.zip') as z:assert z.testzip() is None and reconstruct(stock,z.read('E11.darp'))[1]==b
frozen(out/'SHA256SUMS.txt',('\n'.join(sha((out/n).read_bytes())+'  '+n for n in [name,'E11.darp','Digitone-OS1.44-E11-experimental-patch.zip'])+'\n').encode())
Path('outputs/Digitone-E11-candidate-preparation.json').write_text(json.dumps(dict(passed=True,candidate=str(out/name),candidate_sha256=sha(b),identical_to_PC_tested_container=True,patch_reconstruction_exact=True,hardware_ready=False,physical_trial_pending=True,device_contacted=False,E10_unchanged=True),indent=2),encoding='utf-8')
print('Prepared experimental E11 candidate and patch; no device updated.')
