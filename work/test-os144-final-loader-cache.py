from pathlib import Path
source=Path('work/validate-os144-E03-loader.py').read_text()
source=source.replace("blob=Path('work/os144/packed-context-overlay.bin').read_bytes()","blob=Path('work/os144/fallback-final-payload.bin').read_bytes()")
source=source.replace("m.install_isa_patches_scoped(blob[:1784],0x47be0000)","m.install_isa_patches_scoped(blob[:1784],0x47be0000);m.install_isa_patches_scoped(blob[2212:],0x47be08a4)")
source=source.replace(" r.m.halt_vec=None",''' # Preserve the actual loader's state; overlay only after successful E03 load.
 # This does not validate a repackaged extended container.
 r.m.load(blob,stage+256)
 r.m.uc.mem_write(stage+14,struct.pack('>I',len(blob)//4))
 r.m.uc.mem_write(0x400ffed0,bytes.fromhex('4ef947be08a4'))
 out['source_overlay_after_loader']=True
 r.m.halt_vec=None''')
source=source.replace('outputs/Digitone-OS1.44E03-stock-loader-check.json','outputs/Digitone-OS1.44-final-fallback-loader-cache-check.json')
exec(compile(source,'final-fallback-loader-cache','exec'))
