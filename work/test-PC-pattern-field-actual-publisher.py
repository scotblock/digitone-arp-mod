from pathlib import Path
s=Path('work/test-PC-pattern-field-cold-publication.py').read_text()
s=s.replace("[0x40152ffe,0x40153060,0x40153078]","[0x4002c1a0,0x40152ffe,0x40153060,0x40153078]")
s=s.replace('work/PC-pattern-field-cold-','work/PC-pattern-field-actual-publisher-').replace('outputs/Digitone-E04-PC-pattern-field-cold-publication.json','outputs/Digitone-E04-PC-pattern-field-actual-publisher.json')
exec(compile(s,'actual-publisher-cold-trace','exec'))
