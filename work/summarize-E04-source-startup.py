from pathlib import Path
import sys,json,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.dspboot import build_flash
j=json.loads(Path('outputs/Digitone-E04-source-startup-checks.json').read_text())
origin=json.loads(Path('outputs/Digitone-E04-source-origin-checks.json').read_text())['cases'][0]
saved=json.loads(Path('outputs/Digitone-E04-saved-project-state-checks.json').read_text())
assert len(j['cases'])==4 and all(r['passed'] for r in j['cases']) and origin['passed']
summary={'PC_only':True,'initialization_checks':[],'physical_failure_reproduced':False}
for r in j['cases']:
 assert len(r['captures'])==8 and len(r['producer_entries'])==16
 assert all(c['source']=='0x407fd414' and c['current_pointer']=='407fd414' for c in r['captures'])
 assert [c['track'] for c in r['captures']]==[0,3]*4
 first=r['captures'][0]
 for field in first['source_fields'].values():
  writer=field['last_guest_writer'];assert writer is not None
  assert writer['estimated_instructions']<first['estimated_instructions']
  assert writer['pc']==('0x40008d0a' if field['address'][-1] in ['f'] else '0x40008d5a')
 assert all(e['return']=='0x40094d72' and e['args'][1]=='0x407fd414' for e in r['producer_entries'])
 assert all(c['source_fields']['0_root']['byte']=='43' and c['source_fields']['0_scale']['byte']=='ff' for c in r['captures'])
 if r['image'].endswith('E04'):assert all(c['private_ready']=='00000001' for c in r['captures'])
 summary['initialization_checks'].append({'case':r['image'],'passed':True,'source':first['source'],'first_capture_estimated_instructions':first['estimated_instructions'],'last_root_writer_before_first_capture':first['source_fields']['0_root']['last_guest_writer'],'last_scale_writer_before_first_capture':first['source_fields']['0_scale']['last_guest_writer']})
read=next(e for e in origin['card_reads'] if e['offset']=='0xfc00000')
writes=[e for e in origin['card_writes'] if 0xfc00000<=int(e['offset'],16)<0x10000000]
assert writes and min(e['estimated_instructions'] for e in writes)<read['estimated_instructions']
assert len(origin['serialized_track_entries'])==8
summary['working_project_replacement']={'first_write':writes[0],'first_read':read,'write_count_before_first_read':sum(e['estimated_instructions']<read['estimated_instructions'] for e in writes),'saved_project_restoration_verified':False}
flash=build_flash('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx')
summary['blank_modeled_flash_settings']={hex(off):flash[off:off+22].hex() for off in [0x3c0000,0x400000,0x800000,0xc00000]}
assert all(set(bytes.fromhex(value))=={0} for value in summary['blank_modeled_flash_settings'].values())
summary['original_cards_unchanged']={}
for row in saved['cards']:
 h=hashlib.sha256()
 with open(row['path'],'rb') as f:
  while chunk:=f.read(1024*1024):h.update(chunk)
 assert h.hexdigest()==row['sha256'];summary['original_cards_unchanged'][row['label']]=h.hexdigest()
summary['E04_SYX_unchanged']=hashlib.sha256(Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').read_bytes()).hexdigest()
assert summary['E04_SYX_unchanged']=='76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c'
summary['next_target']='Trace the working-project restore-versus-replacement decision and its persisted settings/header preconditions. Do not seed guessed metadata or treat RAM resume as a cold restore.'
Path('outputs/Digitone-E04-source-startup-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
