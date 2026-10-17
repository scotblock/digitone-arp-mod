import pathlib
p=pathlib.Path('work/test-startup-completions.py').read_text()
exec(p.split("for mode in ['ready'")[0])
exec(p[p.index('# Resume full'):p.index('constructor_state=m;')])
m.configure(uart='current_version');m.stock_flash=True;m.timer_complete=True;m.startup_stops=[0x400ee2bc];before=len(m.steps)
try:m.advance(0x4008c7f4)
except t['Stop']:pass
print('decomp',hex(m.stop_pc),'regs',m.reg)
sp=m.reg['a7'];print('stack',[hex(m.read(sp+j,4)) for j in range(0,32,4)])
for a in [m.read(sp+4,4),m.read(sp+8,4)]:
 print('data',hex(a),bytes(m.read(a+j,1) for j in range(32)).hex())
for i in t['md'].disasm(b[0x400da320-base:0x400da420-base],0x400da320): print(hex(i.address),i.mnemonic,i.op_str)
