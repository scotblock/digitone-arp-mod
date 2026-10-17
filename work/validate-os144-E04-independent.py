from pathlib import Path
s=Path('work/validate-os144-E03-independent.py').read_text().replace('E03','E04').replace('emulator-E02-main.bin','emulator-E04-main.bin').replace('exact_E02_executable','exact_E04_executable').replace('verify-E04.exe','verify-E03.exe')
exec(compile(s,'E04-independent-validation','exec'))
