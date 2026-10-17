from pathlib import Path
import sys
sys.argv=[sys.argv[0],'valid']
# Instrument the packaged E04 startup without changing its code.
s=Path('work/validate-os144-E04-startup.py').read_text()
prefix=s.split("exec(compile(s,'E04-actual-packaged-startup','exec'))")[0]
exec(compile(prefix,'make-E04-startup-trace','exec'))
s=s.replace('work/os144-E04-loader-startup-','work/os144-E04-cache-order-').replace('Digitone-OS1.44E04-startup-','Digitone-OS1.44E04-cache-order-')
needle=" uc=m.uc;r['stages'].append(stage)"
addition='''
 def cache_instruction(uc,pc,n,d):
  value=uc.reg_read(UC_M68K_REG_D0)
  r.setdefault('cache_order',[]).append({'stage':stage,'pc':hex(pc),'value':hex(value),'copied_words':r['copier_stores']})
  assert r['copier_stores']==623 and value==0xa50ce100
  assert value&0x01040100==0x01040100
 def helper(uc,pc,n,d):
  if 'first_helper_execution' not in r:
   assert r.get('cache_order') and r['cache_order'][0]['pc']=='0x4000055a'
   r['first_helper_execution']={'stage':stage,'pc':hex(pc),'CACR':hex(m.ctlregs[2]),'copied_words':r['copier_stores']}
   assert m.ctlregs[2]&0x80008000==0x80008000
 uc.hook_add(UC_HOOK_CODE,cache_instruction,begin=0x4000055a,end=0x4000055a)
 uc.hook_add(UC_HOOK_CODE,helper,begin=RAM,end=RAM+2491)
'''
assert needle in s;s=s.replace(needle,needle+addition)
exec(compile(s,'E04-cache-order-run','exec'))
