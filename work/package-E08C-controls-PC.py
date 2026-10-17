from pathlib import Path
import hashlib
import json

# Retain the existing exact stock container writer and independent decompressor.
source = Path('work/package-E08-PC-path.py').read_text()
source = source.replace('E08', 'E08C')
# The combined manifest has already been assembled by the integration step;
# do not replace it with only the baseline E07 and standalone M1 region lists.
start = source.index("old=json.loads(")
end = source.index('cc,ee=sections(out)', start)
source = source[:start] + '''cfg=json.loads(Path('outputs/Digitone-E08C-PC-path-layout.json').read_text())
cfg.update(candidate=str(out.resolve()), candidate_sha256=sha(out.read_bytes()), sections=entries, stock_writer_byte_exact=True, hardware_ready=False)
''' + source[end:]
exec(compile(source, 'E08C-internal-PC-package', 'exec'))
