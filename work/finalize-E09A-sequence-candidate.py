"""Finalize a separately verified PC-only sequencer correction and patch."""
from pathlib import Path
import json,hashlib,shutil,sys
sha=lambda b:hashlib.sha256(b).hexdigest()
proofs=['Digitone-E09-PC-sequence-owner-contracts.json','Digitone-E09-native-sequence-owner-current.json',
        'Digitone-E09-native-sequence-owner-fixed.json','Digitone-E09A-consumer-chord-contracts.json',
        'Digitone-E09A-packed-loader.json','Digitone-E09A-PC-startup-comparison.json','Digitone-E09A-PC-container-verification.json','Digitone-E09A-packaged-native-sequence.json']
results={p:json.loads(Path('outputs',p).read_text()) for p in proofs}
assert all(p['passed'] for p in results.values())
final=results[proofs[-1]];assert not final['owner_fix_host_overlay'] and not final['helpers_host_loaded']
assert final['sequenced_pulse_count']>=3 and final['keyboard_arp_pitches']==[60,64,67]
candidate=Path('work/os144/E09A-PC-path-candidate.syx')
output=Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx')
assert sha(candidate.read_bytes())=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
assert sha(Path('outputs/Digitone_OS1.44E09_DUAL_PORT_ARP_PC_ONLY.syx').read_bytes())=='2d7446c086699918ed882a7f9e52ac6e29657d09557a4be519b1500bfcd710f0'
shutil.copyfile(candidate,output)
review={'passed':True,'PC_only':True,'hardware_ready':False,'candidate':output.name,'sha256':sha(output.read_bytes()),
        'bytes':output.stat().st_size,'parent':'E09','new_RAM_bytes':0,'payload_bytes':34720,
        'sequence_pulses_current':results[proofs[1]]['sequenced_pulse_count'],
        'sequence_pulses_corrected':final['sequenced_pulse_count'],'matching_note_pairs_per_port':final['matching_note_pairs'],
        'keyboard_arp_pitches':final['keyboard_arp_pitches'],'native_chord_contract':[60,64,67,60,64,67],
        'packaged_helpers_host_loaded':False,'checks':proofs,
        'limits':['Panel-entered continuous sequence test uses a single-pitch trig; multi-note chord output additionally covered by isolated descriptor fixtures.',
                  'USB endpoint and route/input state retain disclosed PC fixtures. No new physical delivery/timing/cache validation.',
                  'M2–M4 arps, step editor, saved-project persistence and exhaustive transition/context ownership are not established.']}
Path('outputs/Digitone-E09A-sequence-review.json').write_text(json.dumps(review,indent=2))
notes='''# E09A — M1 sequencer arp correction (PC candidate)

The native panel-entered sequence confirmed that E09 disables the arp when a note selects its parameter-lock list as if it were a full MIDI parameter record. Descriptor +0x28 and cached address 0x419c5b14 hold parameter-lock list pointers. Reading the custom +0x9e settings word from either list is incorrect. The current isolated ownership tests that called these pointers runtime records modeled the wrong contract.

E09A obtains M1 arp settings from the KitActive context already consumed by the MIDI task, at its M1 runtime record +0x5ce. It does not read the current UI selection to override a playing pattern. Only the existing 242-byte source-owner helper interval changes; the corrected helper is 220 bytes plus NOP padding. No RAM or startup copier growth is introduced. E09 remains unchanged.

The unchanged E09 control generated one raw note for the actual sequenced trig and disabled the arp. The corrected overlay and final startup-copied E09A generate repeated pulses with the arp enabled. The packaged check also sends a live C–E–G chord, checks its three keyboard arp pitches, compares DIN and USB messages, balances note-ons/offs and checks clean state after releases and Stop. The helper is not host-loaded in the final packaged run. A separate isolated consumer/dispatcher/retirement test produces C E G C E G from a sequenced chord fixture and checks OFF, Stop, live release and M2 bypass.

The real loader reaches MAIN, the native startup copier/initializer reaches the UI, and independent MAIN decompression matches. These are PC tests. Continuous native multi-note chord entry, physical port delivery/timing/cache behavior, saved-project persistence and exhaustive queued-note context ownership remain separate gaps. M2–M4 and the MIDI arp step editor are not added.

Try this as a separate Digiemu entry first. Use a trig length long enough for several arp steps: a very short trig can legitimately contain only one arp pulse. Configure M1 with FUNC + SYN2 from an ordinary MIDI parameter page, enable UP, choose RATE/GATE, and check note-offs when stopping. No device was updated by this work.

File: `CANDIDATE`. SHA-256: `HASH`.
'''.replace('CANDIDATE',output.name).replace('HASH',review['sha256'])
Path('outputs/Digitone-E09A-sequence-notes.md').write_text(notes,encoding='utf-8')
repo=Path('github/digitone-arp-mod').resolve();sys.path.insert(0,str(repo/'release-tools'))
from build_patch import make_patch
stock=Path('outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx').read_bytes()
assert sha(stock)=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
meta,patch=make_patch(stock,output.read_bytes(),'E09A',output.name,'PC-only preview: M1 sequencer owner fix; no physical trial')
folder=repo/'patches/E09A';folder.mkdir(parents=True,exist_ok=True)
(folder/'E09A.darp').write_bytes(patch)
(folder/'manifest.json').write_text(json.dumps({'patch_metadata':meta,'patch_sha256':sha(patch),'validation':{'reconstructed_byte_exact':True,'new_hardware_test':False}},indent=2)+'\n')
(folder/'README.md').write_text(notes+'\n\n## Create the file\n\nInstall Python 3.10 or newer. Extract the ZIP, double-click Create Firmware.cmd and supply your original stock OS 1.44 .syx, or run `python apply_patch.py --stock "path/to/stock.syx"`. Output is created beside the patch. Wrong stock files and overwriting existing files are refused. See RECOVERY.md.\n',encoding='utf-8')
print(json.dumps(review,indent=2))
