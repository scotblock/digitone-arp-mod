"""Native CPU acknowledgements must preserve unrelated completion bits."""
from pathlib import Path
import sys,struct,json
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu','work']
from emu.harness import Machine,call
from emu.esdhc import BASE,IRQSTAT
from E10_powerfail_fixture import PolledCompletionStatus
m=Machine();m.ensure(BASE+IRQSTAT);m.ensure(0x40010000);m.ensure(0x47fdff00)
class Controller:
 def __init__(self):self.uc=m.uc
 def _get(self,off):return int.from_bytes(self.uc.mem_read(BASE+off,4),'big')
 def _put(self,off,val):self.uc.mem_write(BASE+off,struct.pack('>I',val))
es=Controller();adapter=PolledCompletionStatus(es)
def ack(value):
 m.uc.mem_write(0x40010000,bytes.fromhex('203c')+struct.pack('>I',value)+bytes.fromhex('23c0fc0cc0302039fc0cc0304e75'))
 m.uc.ctl_remove_cache(0x40010000,0x40010040)
 return call(m,0x40010000,[],stack_top=0x47fdff00,limit=100)
es._put(IRQSTAT,3);assert ack(1)==2 and ack(0)==2 and ack(2)==0
es._put(IRQSTAT,3);assert ack(2)==1 and ack(1)==0
es._put(IRQSTAT,1);assert ack(1)==0
es._put(IRQSTAT,es._get(IRQSTAT)|2);assert ack(0)==2 and ack(2)==0
r=dict(PC_only=True,passed=True,native_guest_stores_and_reads=True,CC_ack_retains_TC=True,TC_ack_retains_CC=True,zero_write_preserves_status=True,later_TC_arrival_preserved=True,scope='Narrow CC/TC adapter only, not an eSDHC timing/error/full-interrupt implementation.',reference='https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=638')
Path('outputs/Digitone-E10-PC-powerfail-status.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print('CC/TC native acknowledgement controls pass.')
