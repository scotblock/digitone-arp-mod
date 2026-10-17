from pathlib import Path
s=Path('work/validate-os144-E03-loader.py').read_text().replace('E03','E04').replace('emulator-E02-main.bin','emulator-E04-main.bin').replace('packed-context-overlay.bin','fallback-final-payload.bin')
s=s.replace('m.install_isa_patches_scoped(blob[:1784],0x47be0000)','m.install_isa_patches_scoped(blob[:1784],0x47be0000);m.install_isa_patches_scoped(blob[2212:],0x47be08a4)')
s=s.replace(' r.m.halt_vec=None'," from emu import bootrom\n bootrom.save_handoff(r,'work/os144/E04-loader-handoff.bin')\n out['handoff_saved_before_application_execution']='work/os144/E04-loader-handoff.bin'\n r.m.halt_vec=None")
exec(compile(s,'E04-packaged-loader-validation','exec'))
