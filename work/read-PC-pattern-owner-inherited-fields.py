from pathlib import Path
exec(Path('work/test-PC-resident-storage-extended-runtime.py').read_text().split('\ntry:')[0])
fields={}
def capture(s):
 for a in [0x41a720d0,0x41a720f0,0x407ef9f4]:fields[hex(a)]=hex(rd(s.m.uc,a))
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=capture);s.close();print(fields)
Path('outputs/Digitone-E04-PC-pattern-owner-inherited-fields.json').write_text(json.dumps({'PC_only':True,'snapshot':case['ui_snapshot'],'inherited_fields':fields,'limit':'Initial snapshot fields only, not a runtime writer or lifetime trace.'},indent=2))
