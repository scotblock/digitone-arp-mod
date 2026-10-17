"""PC candidate replay from the same stock/full prepared snapshot."""
import pathlib,os
os.environ['MATCHED_RENDER_MODE']='full'
outer=pathlib.Path('work/trace-matched-render.py').read_text().split("exec(compile(source,'matched-render-replay','exec'))")[0]
exec(compile(outer,'packed-matched-source','exec'))
source=source.replace('Digitone-matched-render-full','Digitone-matched-render-packed')
# Pin the actual reference workload, independent of inherited shell settings.
# The shared prepared state already contains the receiving arp pattern.
source=source.replace("CLONE=os.environ.get('CLONE_RECEIVING')=='1'","CLONE=False")
source=source.replace("LIVE=os.environ.get('FRESH_LIVE')=='1'","LIVE=False")
source=source.replace("NATIVE_COPY=os.environ.get('NATIVE_PATTERN_COPY')=='1'","NATIVE_COPY=True")
source=source.replace('def install(s):\n uc=s.m.uc','def install(s):\n global blob,layout\n uc=s.m.uc')
anchor=" assert rd(uc,PTR)==BSS-0x14100 and list(struct.unpack('>IIII',uc.mem_read(BSS,16)))==[0x534c4332,2,0xb70,1]"
source=source.replace(anchor,anchor+'''
 packed=json.loads(pathlib.Path('work/packed-context-build.json').read_text())
 original_blob_hash=hashlib.sha256(blob).hexdigest()
 # Verify inherited stock-hook destinations before the explicit PC overlay.
 for hook in packed['hooks']:
  pc=hook['site'];name=hook['name']
  inherited_build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())
  old_target=inherited_build['first_copy_address'] if name=='first_copy' else inherited_build['copy_address'] if name=='copy' else layout[name]['address']
  expected=bytes.fromhex(hook['bytes'][:4])+u32(old_target)+bytes.fromhex(hook['bytes'][12:])
  assert bytes(uc.mem_read(pc,len(expected)))==expected,hex(pc)
 blob=pathlib.Path('work/packed-context-overlay.bin').read_bytes();layout=packed['layout']
 uc.mem_write(RAM,blob)
 for hook in packed['hooks']:uc.mem_write(hook['site'],bytes.fromhex(hook['bytes']))
 result['candidate_installation']={'method':'Explicit PC RAM overlay before timed playback, after inherited image and hook verification','old_sha256':original_blob_hash,'candidate_sha256':hashlib.sha256(blob).hexdigest(),'table_unchanged':packed['table_unchanged'],'context_storage_preserved':True,'loader_executed_candidate':False,'model_cache_initial_state':'Standard cold timed restore, same as both reference controls'}
''')
source=source.replace(" s.m.install_isa_patches_scoped(blob[:1892],RAM);s.m.install_isa_patches_scoped(blob[2368:],RAM+2368)"," s.m.install_isa_patches_scoped(blob[:packed['code_bytes']],RAM)")
source=source.replace(" build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())"," build=dict(first_copy_address=layout['first_copy']['address'],copy_address=layout['copy']['address'])")
source=source.replace("result['PC_runtime_extension_installed']=False","result['PC_runtime_extension_installed']=True")
source=source.replace("result['helper_reinjected']=False","result['helper_reinjected']=True")
source=source.replace("'mode':'full'","'mode':'packed'")
exec(compile(source,'packed-matched-render-replay','exec'))
