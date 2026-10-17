import pathlib,json,struct
exec(pathlib.Path('work/watch-continuous-reserved-RAM.py').read_text().split('def canonical')[0])
from emu.session import Session
from emu import edma_sw as e
s=Session(paths.gui,syx=str(SYX),ddr=DDR)
p=s.ev['ssi0_dma'].p
r={'scope':'Actual selected SSI profile and programmed descriptors at Session initialization; no playback executed','profile':p.name,'rx_channel':p.rx_chan,'tx_channel':p.tx_chan,'descriptors':[]}
for ch in [p.rx_chan,p.tx_chan]:
 td=struct.unpack(e.TCD_FMT,s.m.uc.mem_read(e.TCD_BASE+ch*32,32));r['descriptors'].append({'channel':ch,'source':hex(td[0]),'dest':hex(td[5]),'ATTR':hex(td[1]),'NBYTES':td[3],'CITER':hex(td[6]),'CSR':hex(td[10])})
pathlib.Path('outputs/Digitone-DMA-SSI-profile-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
