import pathlib
p=pathlib.Path('work/audit-clock-bootstrap.py');s=p.read_text();s=s.replace("out.update(stop=r.stop", "out.update(model_limitations=['Starts after hardware serial boot; PLL_CR/PLL_DR reset values are not seeded','LOCK/LOCKS and DDR-initialized flags are model inputs, not physical observations','Bounded to first two million instructions; not full boot or runtime writer certification'], control_registers={hex(k):hex(v) for k,v in r.m.ctlregs.items()}, stop=r.stop")
p.write_text(s)
