from pathlib import Path
src=Path('work/build-E08-PC-native-M1.py').read_text()
src=src.replace('INIT=B+0xd00','INIT=B+0xd00;CONFIG=B+0xe00;TABLE=B+0xf00')
src=src.replace("a.label('enabled');a.emit('202b0020')", "a.label('enabled');absop(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','done');a.emit('202b0020')")
src=src.replace("a.emit('4aab00084aab000c');a.branch('6700','done')", "a.emit('4aab0008');a.branch('6700','done');a.emit('4aab000c');a.branch('6700','done')")
src=src.replace("[(0,0x4d314131),(32,5400000),(36,1350000),(288,0xffffffff)]", "[(0,0x4d314131),(288,0xffffffff)]")
src=src.replace("a.emit('202f0044');absop", "a.emit('4878003248780002');js(a,CONFIG);a.emit('508f202f0044');absop")
extra='''# configure(rate_index, gate_percent): units are stock musical ticks, not ms.
# Native timestamp = 900000 units per MIDI clock; one beat is 21600000.
a=Asm();save(a);a.emit('202f0044222f00480c8000000008');a.branch('6400','bad');a.emit('0c8100000001');a.branch('6500','bad');a.emit('0c8100000063');a.branch('6200','bad');a.emit('2600');absop(a,'41f9',TABLE);a.emit('20300c0028004c010000243c000000c84c420000');absop(a,'23c4',S+32);absop(a,'23c0',S+36);absop(a,'23c3',S+304);absop(a,'23c1',S+308);a.emit('7001');a.branch('6000','return');a.label('bad');a.emit('7000');a.label('return');a.emit('2f400000');restore(a);a.emit('4e75');add('configure_rate_gate',CONFIG,a,256)
rates=[21600000,10800000,5400000,2700000,1800000,900000,7200000,3600000]
ratebytes=b''.join(struct.pack('>I',v) for v in rates)
parts.append((TABLE,ratebytes))
'''
src=src.replace('blob=bytearray(0xe00)',extra+'\nblob=bytearray(0x1000)')
src=src.replace("'init':INIT}","'init':INIT,'configure':CONFIG}")
src=src.replace("'hooks':hooks,'limits'", "'hooks':hooks,'data_regions':[{'name':'rate_table','base':TABLE,'bytes':32}],'rate_units':rates,'rate_labels':['1/4','1/8','1/16','1/32','1/48','1/96','1/8T','1/16T'],'limits'")
src=src.replace('E08-PC-native-M1-code.bin','E08-PC-tempo-M1-code.bin').replace('E08-PC-native-M1-layout.json','E08-PC-tempo-M1-layout.json')
Path('work/build-E08-PC-tempo-M1.py').write_text(src)
