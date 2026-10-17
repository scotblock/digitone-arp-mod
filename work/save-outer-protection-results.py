from pathlib import Path
import sys,struct,re,json,hashlib
root=Path(__file__).resolve().parents[1]
exec((root/'work/disassemble.py').read_text().split('out=[]')[0]);md.skipdata=True
anchors={0x4003e4ca:'24bc40177ba8',0x40177bb0:'4003c8a0',0x40177bdc:'4003b50e',0x40177be0:'4003b4ac',0x4003d642:'4eb9400d6974',0x400d69d0:'22680038',0x400d69e8:'22680034',0x400d69f4:'4ed1',0x4003b4ca:'4e93',0x4003b4d8:'4eb940025628',0x4003b53a:'4eb940025628',0x4003b560:'4eb940025ada',0x40025bc4:'4eb9400208a0',0x400208bc:'4eb9400134e4',0x400256ec:'4e94',0x400256dc:'2f3c0001611d',0x400256e8:'2f09',0x400256ea:'2f00',0x4002531e:'4ebaef9a',0x40024384:'4eb940008de0',0x4003aca6:'4eb94002528c',0x4003cee8:'203c4003ac86',0x400172a8:'4eb940014678',0x40001dbe:'46c2',0x400eef68:'23c1400002fc',0x400eef86:'23c0400002fc',0x400071e8:'23c2404dc2fc',0x40007260:'23c2404dc2fc',0x400a9ca4:'4eb940093b72'}
for a,h in anchors.items():
 actual=b[a-base:a-base+len(bytes.fromhex(h))].hex()
 assert actual==h,(hex(a),actual,h)
ui_targets={}
for code in [10,11,12]:
 off=0x4003c8d2-base+2*(code-1)
 target=0x4003c8d2+struct.unpack_from('>h',b,off)[0]
 assert target==0x4003d63e
 ui_targets[str(code)]=f'{target:08x}'
windows={
'copy_helper':(0x40022552,0x400225ec),
'record_replacement':(0x40025628,0x40025796),
'reset_record_wrapper':(0x40025ada,0x40025c6c),
'pattern_default_method':(0x400208a0,0x400208da),
'import_wrapper':(0x4002528c,0x40025454),
'import_converter_caller':(0x400242ba,0x400243d8),
'ui_replacement_slot38':(0x4003b4ac,0x4003b50e),
'ui_replacement_reset_slot34':(0x4003b50e,0x4003b576),
'import_confirmation_callback':(0x4003ac86,0x4003acb6),
'screen_handler_entry':(0x4003c8a0,0x4003c8d2),
'screen_handler_default':(0x4003d63e,0x4003d64e),
'ui_dispatch':(0x400d6974,0x400d6a02),
'screen_virtual_dispatch':(0x400d6efc,0x400d6f1a)}
scan={}
for name,(s,e) in windows.items():
 ins=list(md.disasm(b[s-base:e-base],s))
 sr=[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in ins if re.search(r'\bsr\b',i.op_str)]
 suppress=[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in ins if any(f'${a:x}' in i.op_str for a in [0x400eef48,0x400eef72])]
 assert not sr and not suppress,(name,sr,suppress)
 scan[name]=dict(start=f'{s:08x}',end_exclusive=f'{e:08x}',explicit_sr_operations=sr,explicit_suppression_calls=suppress,scope='Local instructions only; called helpers and computed aliases are not transitively proved')
reference_inventory={}
for target in [0x40022552,0x400eef48,0x400eef72]:
 reference_inventory[f'{target:08x}']=[f'{base+m.start():08x}' for m in re.finditer(re.escape(struct.pack('>I',target)),b)]
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
sys.path.insert(0,str(root/'outputs'))
from digitone_transaction_handoff_checks import checks
model=checks()
result=dict(static_audit_only=True,verified_byte_anchors={f'{a:08x}':h for a,h in anchors.items()},ui_jump_targets=ui_targets,local_instruction_scans=scan,raw_pointer_inventory=reference_inventory,transaction_model=model,unchanged_input_sha256=dict(zip([p.name for p in paths],hashes)),conclusion='No outer complete-update guard recovered in these explicit UI replacement/reset/import routes; not a universal proof of absent protection')
(root/'outputs/Digitone-outer-protection-check-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Verified',len(anchors),'byte anchors;',len(windows),'local instruction ranges; three UI jump-table cases;',model['scenarios_passed'],'transaction scenarios; hashes unchanged')
