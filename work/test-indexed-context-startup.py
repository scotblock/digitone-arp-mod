"""Re-execute loader and startup with compact isolated helpers; original unchanged."""
import pathlib
text=pathlib.Path('work/test-loader-derived-startup-playback.py').read_text()
text=text.replace("exec(compile(pre,'loader-fixture-preparation','exec'))", "pre=pre.replace('work/fast-pitch-overlay.bin','work/indexed-context-overlay.bin')\nexec(compile(pre,'loader-fixture-preparation','exec'))")
text=text.replace("wrapper=wrapper[:pos]+extra+wrapper[pos:]", "wrapper=wrapper[:pos]+extra+wrapper[pos:]\nwrapper=wrapper.replace('work/fast-pitch-overlay.bin','work/indexed-context-overlay.bin')")
text=text.replace('work/loader-derived-arp-emulator','work/indexed-loader-derived-arp-emulator')
text=text.replace('outputs/Digitone-loader-derived-startup-playback.json','outputs/Digitone-indexed-context-startup-playback.json')
text=text.replace('work/loader-derived-entry.handoff','work/indexed-loader-derived-entry.handoff')
text=text.replace('work/loader-derived-transform-audit.py','work/indexed-loader-derived-transform-audit.py')
exec(compile(text,'indexed-loader-startup','exec'))

