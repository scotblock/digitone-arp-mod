"""Cycle-aware controls from compact helper's actual loader-derived startup."""
import pathlib
source=pathlib.Path('work/run-loader-timing-case.py').read_text()
source=source.replace('work/fast-pitch-overlay.bin','work/compact-hook-overlay.bin')
source=source.replace('work/loader-derived-arp-emulator','work/compact-loader-derived-arp-emulator')
source=source.replace('outputs/Digitone-loader-derived-startup-playback.json','outputs/Digitone-compact-hook-startup-playback.json')
source=source.replace("flash_namespace={};exec", "pre=pre.replace('work/fast-pitch-overlay.bin','work/compact-hook-overlay.bin')\nflash_namespace={};exec")
source=source.replace('work/fast-pitch-build.json','work/compact-hook-build.json')
exec(compile(source,'compact-hook-timing-case','exec'))
