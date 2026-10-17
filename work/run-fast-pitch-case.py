"""Reuse established timing probes with an alternate PC-only helper image."""
import pathlib,os
source=pathlib.Path('work/isolate-first-stale-read.py').read_text()
if os.environ.get('FAST_PITCH')=='1':
 source=source.replace('exec(p)\n',"exec(p)\nblob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()\n",1)
 source=source.replace("report={'experiment':", "report={'optimized_build':json.loads(pathlib.Path('work/fast-pitch-build.json').read_text()),'experiment':",1)
 # Preserve the lookup data as a checked read-only fixture, not executable ISA patches.
 source=source.replace('m.install_isa_patches_scoped(blob,RAM)','m.install_isa_patches_scoped(blob[:1892],RAM)')
 source=source.replace("  rec.update(memory_model=", "  if mode in ('all','all_fixed','context_only','sham'):assert bytes(session.m.uc.mem_read(RAM+1904,420))==blob[1904:2324]\n  rec.update(memory_model=",1)
if os.environ.get('LONG_PLAYBACK')=='1':
 heavy=pathlib.Path('work/test-voice-heavy-memory-sensitivity.py').read_text()
 segment=heavy[heavy.index("  session.tap(session.code('KEYBOARD')"):heavy.index('  rec.update(memory_model=')]
 source=source.replace("  mark('prefix ends at 80 ms before keyboard input')\n",segment)
exec(compile(source,'fast-pitch-timing','exec'))
