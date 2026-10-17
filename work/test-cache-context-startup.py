"""Re-execute loader and startup with compact isolated helpers; original unchanged."""
import pathlib
text=pathlib.Path('work/test-loader-derived-startup-playback.py').read_text()
text=text.replace("exec(compile(pre,'loader-fixture-preparation','exec'))", "pre=pre.replace('work/fast-pitch-overlay.bin','work/cache-context-overlay.bin')\nexec(compile(pre,'loader-fixture-preparation','exec'))")
text=text.replace("wrapper=wrapper[:pos]+extra+wrapper[pos:]", "wrapper=wrapper[:pos]+extra+wrapper[pos:]\nwrapper=wrapper.replace('work/fast-pitch-overlay.bin','work/cache-context-overlay.bin')")
text=text.replace('work/loader-derived-arp-emulator','work/cache-loader-derived-arp-emulator')
text=text.replace('outputs/Digitone-loader-derived-startup-playback.json','outputs/Digitone-cache-context-startup-playback.json')
text=text.replace('work/test-continuous-loader-copier.py','work/cache-loader-fixture.py')
text=text.replace('work/loader-derived-entry.handoff','work/cache-loader-derived-entry.handoff')
text=text.replace('work/loader-derived-transform-audit.py','work/cache-loader-derived-transform-audit.py')
text=text.replace("try:exec(compile(wrapper,", "wrapper=wrapper.replace('assert len(blob)==2324','assert len(blob)==2564')\nwrapper=wrapper.replace('m.install_isa_patches_scoped(blob[:1892],RAM)','m.install_isa_patches_scoped(blob[:1892],RAM);m.install_isa_patches_scoped(blob[2368:],RAM+2368)')\ntry:exec(compile(wrapper,")
exec(compile(text,'cache-loader-startup','exec'))

