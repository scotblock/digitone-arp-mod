"""Read-only firmware inspection; all derived bytes isolated from 1.42."""
import pathlib,hashlib,json
directory=pathlib.Path('work/os144');directory.mkdir(exist_ok=True)
source=pathlib.Path('work/firmware_inspect.py').read_text()
source=source.replace("inputs/Digitone_and_Digitone_Keys_OS1.42.syx","inputs/Digitone_and_Digitone_Keys_OS1.44.syx")
source=source.replace("f'work/section-{sid}.bin'","f'work/os144/section-{sid}.bin'")
source=source.replace("'work/inspection.json'","'work/os144/inspection.json'")
# The terminal gamma offset wraps modulo 2**32, as in the firmware codec.
# The historical first-pass decoder recovered bytes but missed this terminator.
source=source.replace('off=(g<<8)+byte()','off=((g<<8)+byte())&0xffffffff')
ns={};exec(compile(source,'read-only-os144-inspection','exec'),ns)
result=ns['result'];c=ns['c']
for section in result['sections']:
 sid=section['id'];off=int(section['offset'],16);stored=c[off:off+section['stored_bytes']]
 (directory/f'section-{sid}-stored.bin').write_bytes(stored)
result['recognized_elekloader_hash']=result['sha256']=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
main=next(s for s in result['sections'] if s['id']==3)
assert result['recognized_elekloader_hash']
assert main['raw_sha256']=='fce648a97c6c5d93b961732e8f8db6b02e0820c6d344c7e2131fa05a4b3168e4' and main['raw_bytes']==2736304
assert result['content_checksum_stored']==result['content_checksum_calculated']
assert result['packet_checks_pass']==result['data_packets'] and result['sequence_contiguous'] and result['padding_zero']
assert main['stream_sum_stored']==main['stream_sum_calculated'] and main['explicit_end']
result['firmware_modified']=False
pathlib.Path('outputs/Digitone-OS1.44-inspection.json').write_text(json.dumps(result,indent=2))
print('PASS recognized stock 1.44; all framing/main stream checks; files unchanged')
