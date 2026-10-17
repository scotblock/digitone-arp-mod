"""Bounded actual sequencer diagnostic, fixture notes rather than live input."""
from pathlib import Path
s=Path('work/test-E09-packaged-M1-both-ports.py').read_text()
s=s.replace("phase='UP_both'", "phase='sequenced_both'")
start=s.index("    send([v for note in [60,64,67]")
end=s.index('    def notes(raw):',start)
s=s[:start]+'''    base=rd(s.m.uc,0x4138f214)+4*0x3d0
    s.m.uc.mem_write(base,(1).to_bytes(2,'big'))
    s.m.uc.mem_write(base+0x80,bytes([100]));s.m.uc.mem_write(base+0xc0,bytes([76]))
    s.m.uc.mem_write(base+0x180,bytes([60,4,7,0,0,0,0,0]))
    s.m.uc.mem_write(base+0x3cc,bytes([16,2]))
    out['sequenced_chord_is_host_fixture']=True
    s.tap(s.code('PLAY'),hold_ms=100,after_ms=100);s.run_ms(2400)
    phase='stop';s.tap(s.code('STOP'),hold_ms=100,after_ms=350)
'''+s[end:]
s=s.replace('outputs/Digitone-E09-packaged-M1-both-ports.json','outputs/Digitone-E09-sequenced-M1-diagnostic.json')
s=s.replace("    assert not active and [rd", "    assert ons>=12,('Not enough arp steps to distinguish repeated raw chords',ons,din)\n    assert not active and [rd")
exec(compile(s,'E09-sequenced-M1-diagnostic','exec'))
