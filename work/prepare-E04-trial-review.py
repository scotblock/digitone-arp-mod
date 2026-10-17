from pathlib import Path
import hashlib

s = Path('work/test-E03-startup-DIN-route.py').read_text().replace('E03','E04')
s = s.replace("r={'PC_only':True,", "r={'image_sha256':hashlib.sha256(raw).hexdigest(),'PC_only':True,")
Path('work/test-E04-startup-DIN-route.py').write_text(s)
source = Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx').read_bytes()
assert hashlib.sha256(source).hexdigest() == 'd4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
dest = Path('outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx')
dest.parent.mkdir(exist_ok=True)
assert not dest.exists() or dest.read_bytes() == source
dest.write_bytes(source)
assert hashlib.sha256(dest.read_bytes()).hexdigest() == hashlib.sha256(source).hexdigest()
print('Stock recovery copy verified; exact E04 receive test prepared.')
