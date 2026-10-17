from pathlib import Path
import sys,json,hashlib,zlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.snapshot import _load_blob
from emu.harness import PAGE
j=json.loads(Path('outputs/Digitone-E04-restore-decision-checks.json').read_text())
assert len(j['cases'])==4 and all(r['passed'] for r in j['cases'])
summary={'PC_only':True,'cases':[],'physical_freeze_reproduced':False}
for r in j['cases']:
 labels={e['label']:e for e in r['restore_decisions']}
 blank=r['image']=='blank_E04';second=r['image'].startswith('invalid_first')
 assert len(r['captures'])==(8 if blank else 4)
 if blank:
  assert labels['first_header_result']['d0']==labels['second_header_result']['d0']=='0x0'
  assert 'initialize_defaults' in labels and 'full_payload_read_return' not in labels
  assert int(labels['publish_selected_bank']['global_flags'],16)&4
  expected_root,expected_scale='43','ff';bank=None
 else:
  assert labels['first_header_result']['d0']==('0x0' if second else '0x1')
  if second:assert labels['second_header_result']['d0']=='0x1'
  assert 'initialize_defaults' not in labels and 'try_SPI_recovery' not in labels
  assert not int(labels['publish_selected_bank']['global_flags'],16)&4
  assert labels['publish_selected_bank']['d2']==('0x1' if second else '0x0')
  assert 'full_payload_read_return' in labels
  expected_root,expected_scale='3c','00';bank=0xf800000 if second else 0xf400000
  end=bank
  for e in r['card_reads']:
   lo=int(e['offset'],16);hi=lo+(e['length'] or 0)
   if bank<=lo<bank+0x2a7600 and lo<=end: end=max(end,hi)
  assert end>=bank+0x2a7514
 for c in r['captures']:
  assert c['source_fields']['0_root']['byte']==expected_root and c['source_fields']['0_scale']['byte']==expected_scale
  assert c['source_fields']['0_scale']['last_guest_writer']['estimated_instructions']<c['estimated_instructions']
 entry={'case':r['image'],'passed':True,'restored_bank':hex(bank) if bank else None,'capture_count':len(r['captures']),'first_track_root':int(expected_root,16),'first_track_raw_scale':int(expected_scale,16),'UI_up':r['intro']['up'],'native_timer_interrupts':r['timer_fired']}
 if r['image'].endswith('E04'):
  snap=next(Path('work/restore-decision-'+r['image']).rglob('boot.snap'))
  blob=_load_blob(str(snap));base=0x47be1a24&~(PAGE-1);data=zlib.decompress(blob['pages'][base]);word=int.from_bytes(data[0x47be1a24-base:0x47be1a28-base],'big')
  assert word==(0x80000043 if blank else 0x800000bc)
  entry['captured_first_track_context_word']=hex(word)
 summary['cases'].append(entry)
a,b=j['cases'][1:3]
assert [(c['track'],c['source'],c['event'],{k:v['byte'] for k,v in c['source_fields'].items()}) for c in a['captures']]==[(c['track'],c['source'],c['event'],{k:v['byte'] for k,v in c['source_fields'].items()}) for c in b['captures']]
summary['stock_E04_restored_capture_inputs_match']=True
summary['E04_SYX_sha256']=hashlib.sha256(Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').read_bytes()).hexdigest()
assert summary['E04_SYX_sha256']=='76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c'
saved=json.loads(Path('outputs/Digitone-E04-saved-project-state-checks.json').read_text())
for row in saved['cards']:
 h=hashlib.sha256()
 with open(row['path'],'rb') as f:
  while z:=f.read(1024*1024):h.update(z)
 assert h.hexdigest()==row['sha256']
summary['original_cards_unchanged']=True
summary['limits']=['Retained RAM mirror installed into disposable card fixtures; not physical-device persisted bytes.','Full SPI fallback recovery and header-requested reset branches are only statically inspected.','PC restore through intro with native modeled timer completion; not physical cache/timing validation.']
Path('outputs/Digitone-E04-restore-decision-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
