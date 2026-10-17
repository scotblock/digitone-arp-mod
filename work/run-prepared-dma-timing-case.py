"""Sensitivity from confirmed native pattern-2 preparation, not panel request."""
import pathlib
outer=pathlib.Path('work/run-cache-context-timing-case.py').read_text().split("exec(compile(source,'cache-context-timing-case','exec'))")[0]
exec(compile(outer,'prepared-timing-source','exec'))
marker="exec(compile(source,'loader-derived-cycle-timing','exec'))"
extra='''
source=source.replace('session=Session(paths.gui',"session=Session('work/cache-native-prepared-handoff.snap'")
source=source.replace("session.tap(session.code('PLAY'),hold_ms=10,after_ms=30)","session.tap(session.code('PLAY'),hold_ms=30,after_ms=50)")
source=source.replace("rec['workload']=[]", "rec['workload']=[];rec['confirmed_start_pattern_backing']=hex(rd(session.m.uc,0x41342150));assert rec['confirmed_start_pattern_backing']=='0x407c61e9'")
'''
source=source.replace(marker,extra+marker)
exec(compile(source,'prepared-dma-timing-case','exec'))
