"""Run existing startup and arp suites with the verified 128MiB alias map."""
import pathlib,json
ns={};exec(pathlib.Path('work/ddr-alias-model.py').read_text(),ns)
source=pathlib.Path('work/test-reserved-RAM-route.py').read_text()
source=source.replace('m=fresh();',"ns['install_aliases'](s['Machine'])\nm=fresh();",1)
source=source.replace('outputs/Digitone-reserved-RAM-route-results.json','outputs/Digitone-reserved-RAM-alias-startup-results.json')
exec(compile(source,'alias-startup','exec'))
alias_checks=[]
for offset in [0,4,0x1000,0x1004,0x1b70]:
 value=m.read(RAM+offset,4)
 for window in range(8):
  assert m.read(RAM+offset+window*0x08000000,4)==value
  alias_checks.append((offset,window))
saved=m.read(BSS+32,4);m.write(ALIAS+0x1024,4,0xa55a1234);assert m.read(BSS+32,4)==0xa55a1234;m.write(BSS+32,4,saved)
assert ns['canonical'](0x43be0000)!=RAM
assert ns['canonical'](0x4bbe0000)==0x43be0000
startup_count=len(checks)
# The integration prefix reconstructs its classes; install aliases again there.
integration=pathlib.Path('work/test-reserved-RAM-arp-integration.py').read_text().replace('outputs/Digitone-reserved-RAM-arp-integration-results.json','outputs/Digitone-reserved-RAM-alias-arp-results.json')
integration=integration.replace('# Reuse the original integration',"ns['install_aliases'](h['Machine'])\n# Reuse the original integration")
exec(compile(integration,'alias-integration','exec'))
assert h['Machine'].alias_model_installed
r={'startup_assertions':startup_count,'arp_assertions':len(h['checks']),'alias_read_comparisons':len(alias_checks),'uncached_write_visible':True,'lower_64MiB_is_distinct':True,'firmware_modified':False,'limits':['Memory identity only; cache coherence, DMA and global ownership remain unverified.','Same bounded producer and supplied boundary coverage as the original suites.']}
pathlib.Path('outputs/Digitone-reserved-RAM-alias-results.json').write_text(json.dumps(r,indent=2));print('PASS',r)
