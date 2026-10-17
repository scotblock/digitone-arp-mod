from pathlib import Path
p=Path('work/build-PC-deferred-release-overlay.py');s=p.read_text();start=s.index('read(a,COUNT);cmp(a,CAP)');end=s.index("a.label('overflow')",start)
new="""# Use the stock per-track/per-pitch reference count to distinguish repeated
# valid releases from duplicate messages. Zero references permits one stock
# cleanup attempt; no synthetic note-owner claim is made.
a.emit('202f001cef88d0af0020e5880680419952a8224020114a80');a.branch('6e00','budget');a.emit('7001');a.label('budget');a.emit('2240')
read(a,COUNT);cmp(a,CAP);a.branch('6200','overflow');a.emit('2400720041f9'+struct.pack('>I',ENTRIES).hex())
a.label('scan');a.emit('4a82');a.branch('6700','append')
for reader,comparison in [('202f001c','b090'),('202f0020','b0a80004')]:a.emit(reader+comparison);a.branch('6600','next')
a.emit('5281');a.label('next');a.emit('41e8000c5382');a.branch('6000','scan')
a.label('append');a.emit('2009b081');a.branch('6300','deny');read(a,COUNT);cmp(a,CAP);a.branch('6400','overflow')
for reader,store in [('202f001c','2080'),('202f0020','21400004'),('202f0024','21400008')]:a.emit(reader+store)
read(a,COUNT);a.emit('5280');absolute(a,'23c0',COUNT);a.branch('6000','deny')
"""
s=s[:start]+new+s[end:];p.write_text(s)
