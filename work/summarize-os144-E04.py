from pathlib import Path
import json,hashlib
read=lambda name:json.loads(Path('outputs/'+name+'.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=read('Digitone-OS1.44E04-packaging');independent=read('Digitone-OS1.44E04-independent-checks');loader=read('Digitone-OS1.44E04-stock-loader-check');update=read('Digitone-OS1.44E04-update-boundary-checks')
assert independent['passed'] and loader['passed'] and update['update_loop']['passed']
assert loader['loader']['main_matches'] and not loader['loader']['flash_writes'] and loader['copier_stores']==623
assert independent['all_other_sections_unchanged'] and independent['in_place']['minimum_first_unread_byte_to_last_output_write_gap']>0
cases={}
for mode in ['valid','bad_magic','bad_pointer']:
 r=read('Digitone-OS1.44E04-startup-'+mode);old=read('Digitone-OS1.44-fallback-final-'+mode)
 assert r['passed'] and r['packaged_candidate_without_code_overlays'] and r['copier_stores']==623
 assert r['pitches']==old['pitches'] and r['audio_sha256']==old['audio_sha256']
 assert r['pointer_after_playback']==('0x47bccf04' if mode=='valid' else '0x0')
 cases[mode]={k:r[k] for k in ['passed','loader_handoff','copy_events','copier_stores','startup_entries','pointer_at_UI','pointer_after_playback','helper_hits','audio_bytes','audio_sha256','pitches']}
 assert not any(t['overlaps_reservation'] for t in r['tasks'])
 assert not any(e['overlaps_reservation'] for d in r['dma_descriptors'].values() for e in d['envelopes'])
assert sha('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx')==build['output_sha256']
assert sha('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx')=='8775320f161cb02efa8f51b2671034baf73eeec95f4bb66ffc20a29e9b0a2a3d'
out={'PC_only':True,'passed':True,'hardware_ready':False,'build':build,'independent_validation':{'passed':True,'C_verifier':independent['independent_C_verifier'],'packet_checks':independent['packet_checks'],'negative_checks':independent['negative_checks'],'decompression':independent['decompression'],'in_place':independent['in_place']},'loader':loader,'startup_playback':cases,'padding_and_simulated_programming':update['update_loop'],'E03_unchanged':True,'limits':['Only MAIN changes; physical cache coherence and audio/DMA timing remain unverified.','The real stock bootstrap/updater instructions run in an emulator with modeled hardware. No instrument was accessed.','Loader handoff transfers CPU/RAM/control-register and relevant MMIO state into the application engine; this is not one physical uninterrupted power-on.','Successful startup has no firmware-code overlays. Failure controls deliberately inject bad magic or pointer at initializer entry.','Prepared PC drive, source root/scale fixture, stopped pattern selection and short playback; broader live sustain/playing handoff behavior is inherited helper evidence, not newly exercised here.','The update-loop test simulates erase/program/display calls; it is not a completed DIN update/recovery trial.','Previously diagnosed emulator parameter-packet-age effects remain; E04 adds no audio synchronization workaround.']}
Path('outputs/Digitone-OS1.44E04-validation-summary.json').write_text(json.dumps(out,indent=2));print('PASS E04 packaged loader, inherited-state startup/playback, padding; E03 unchanged')
