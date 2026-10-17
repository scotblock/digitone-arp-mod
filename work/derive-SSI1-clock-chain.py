import json,pathlib
from fractions import Fraction
def chain(ccr,external):
 div2=2 if ccr&(1<<18) else 1;psr=8 if ccr&(1<<17) else 1;pm=(ccr&255)+1
 bit=Fraction(external,2*div2*psr*pm)
 return {'CCR':hex(ccr),'source':'external SSI_CLKIN; CDRH bypassed','external_input_hz_conditional':external,'DIV2_factor':div2,'PSR_factor':psr,'PM_plus_one':pm,'bitclock_hz':str(bit),'I2S_frame_bits':64,'frame_hz':str(bit/64)}
r={'firmware_modified':False,'physical_frequency_verified':False,'stock_source_selection':{'address':'0xec09000e','bit':5,'clear_pc':'0x40000f96','mask':'0xffffffcf','bootstrap_same_mask_pc':'0x80004eea','observed_final':'0x0800'},'branches':[dict(board_flag_0x80000=False,chain=chain(0x16101,12288000)),dict(board_flag_0x80000=True,chain=chain(0x56103,49152000),additional_interface='SSI0 enabled; not modeled by current playback path')],'core_candidates_hz':[250000000,264000000],'audio_rate_support':'Elektron original Digitone manual specifies 48 kHz converters; required external inputs derived from register divisors','unsupported_inference':'Core frequency cannot be derived from external SSI1 clock; neither oscillator frequency is physically read out','phase_policy_limits':['TXSR modeled as word validity, not 24-bit waveform','Status assertion delayed one I2S bit; request acknowledge/deassert timing remains a modeled policy','Hardware serial-boot reset values, global computed writers and alternate board playback not certified']}
assert all(x['chain']['frame_hz']=='48000' for x in r['branches'])
pathlib.Path('outputs/Digitone-SSI1-clock-chain.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r['branches'],indent=2))
