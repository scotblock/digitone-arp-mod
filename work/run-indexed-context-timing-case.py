"""Cycle-aware controls from compact helper's actual loader-derived startup."""
import pathlib
source=pathlib.Path('work/run-loader-timing-case.py').read_text()
source=source.replace('work/fast-pitch-overlay.bin','work/indexed-context-overlay.bin')
source=source.replace('work/loader-derived-arp-emulator','work/indexed-loader-derived-arp-emulator')
source=source.replace('outputs/Digitone-loader-derived-startup-playback.json','outputs/Digitone-indexed-context-startup-playback.json')
source=source.replace("flash_namespace={};exec", "pre=pre.replace('work/fast-pitch-overlay.bin','work/indexed-context-overlay.bin')\nflash_namespace={};exec")
source=source.replace('work/fast-pitch-build.json','work/indexed-context-build.json')
source=source.replace("exec(compile(source,'loader-derived-cycle-timing','exec'))", "if os.environ.get('EXTENDED_HOLD')=='1':source=source.replace('  for i in range(16):','  for i in range(32):')\nexec(compile(source,'loader-derived-cycle-timing','exec'))")
exec(compile(source,'indexed-context-timing-case','exec'))

