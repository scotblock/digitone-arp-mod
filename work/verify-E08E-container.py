from pathlib import Path
s=Path('work/verify-E07-PC-container.py').read_text().replace('E07','E08E')
s=s.replace('E08E-PC-candidate.syx','E08E-PC-path-candidate.syx').replace('E08E-PC-main.bin','E08E-PC-layout-main.bin').replace('Digitone-E08E-PC-candidate-layout.json','Digitone-E08E-PC-path-layout.json')
start=s.index("old=json.loads(");end=s.index('manifest=json.loads(',start)
s=s[:start]+s[end:]
s=s.replace('manifest=json.loads(', "assert hashlib.sha256(Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx').read_bytes()).hexdigest()=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'\nassert hashlib.sha256(Path('work/os144/E08D-PC-path-candidate.syx').read_bytes()).hexdigest()=='c6e2b327af09c46858ab3b902e0a35a0dce5bf355258952c0915983aabfc5099'\nassert hashlib.sha256(Path('outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx').read_bytes()).hexdigest()=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'\nmanifest=json.loads(")
s=s.replace('old_firmware_and_overlay_hashes_unchanged','E07_E08D_and_stock_unchanged').replace('stock/E04 preserved','stock/E07/E08D preserved')
exec(compile(s,'E08E-independent-container-checks','exec'))
