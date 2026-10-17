from pathlib import Path
import os
variant=os.environ.get('PROBE_VARIANT','stock')
os.environ['OS144_HOOK_MODE']='stock' if variant in ['stock','repeat','exact-stock','deep-stock','status-stock','origin-stock','sram-stock'] else 'helpers'
os.environ['OS144_HOOK_SCENARIO']='ordinary'
src=Path('work/run-os144-continuous-hooks.py').read_text().split("exec(compile(s,'continuous-1.44-hooks','exec'))")[0]
exec(compile(src,'build-probe','exec'))
s=s.replace("OUT=Path('outputs/Digitone-OS1.44-continuous-ordinary-"+MODE+".json')", "OUT=Path('outputs/Digitone-OS1.44-audio-copy-"+variant+".json')")
assert 'audio-copy-'+variant in s
s=s.replace("for h in port['hooks']:","for h in port['hooks']:\n   if "+repr(variant)+"=='allocator' and h['name']!='allocate_clear':continue\n   if "+repr(variant)+"=='pitch' and h['name']!='pitch_hook':continue")
if variant=='sham':
 s=s.replace("if MODE=='helpers':", "if False:",1)
extra='''
 r['probe_variant']=VARIANT
 if VARIANT=='sham':
  address=RAM+0xe00
  shim=bytes.fromhex('4e71')*64+bytes.fromhex('40c046fc27004ef9')+u32(0x400ffff8)
  uc.mem_write(address,shim);uc.mem_write(0x400ffff2,bytes.fromhex('4ef9')+u32(address))
  r['fixtures'].append({'kind':'Timing-only allocator shim','NOPs':64,'context_writes':False})
 if VARIANT.startswith('exact-'):s.stepper=False
 link=s.ev['dsplink'];original=link._service_dsp;packets=[];voices=[]
 def service(d,elapsed,taken=False):
  before=link.renders;packet=bytes(link._buf.raw[:0x3a0]);stamp=s.now_ms();answer=original(d,elapsed,taken=taken)
  if link.renders>before:
   voice=bytes(link._buf.raw[0x3a0:0x7a0]);packets.append(packet);voices.append(voice)
   r.setdefault('dsp',[]).append({'ms':stamp,'packet':hashlib.sha256(packet).hexdigest(),'voice':hashlib.sha256(voice).hexdigest()})
   if 3983<=stamp<=3986:r.setdefault('ordered_packet_trace',[]).append({'event':'DSP consumes packet','ms':stamp,'render_index':len(packets)-1,'word8':packet[8:12].hex(),'word32c':packet[0x32c:0x330].hex()})
   if VARIANT.startswith('origin-') and len(packets)==5977:
    memory=s.m._ddr_buf;where=memory.find(packet)
    r['packet_origin']={'ms':stamp,'address':hex(0x40000000+where) if where>=0 else None,'another':memory.find(packet,where+1) if where>=0 else None}
    descriptors=bytes(uc.mem_read(0xfc045000,64*32))
    r['origin_descriptors']=[{'channel':i,'bytes':descriptors[i*32:(i+1)*32].hex()} for i in range(64) if 0x10000000<=struct.unpack_from('>I',descriptors,i*32+16)[0]<0x10001000]
  return answer
 link._service_dsp=service;s._probe_packets=packets;s._probe_voices=voices
 ssi=s.ev['ssi0_dma'];sink=ssi.sink
 def transfer(uc,pc,n,d):
  if 3983<=s.now_ms()<=3986:r.setdefault('ordered_packet_trace',[]).append({'event':'DMA47 start instruction','ms':s.now_ms(),'source_word8':bytes(uc.mem_read(0x80001c08,4)).hex(),'source_word32c':bytes(uc.mem_read(0x80001f2c,4)).hex()})
 s.at(0x4009e050,transfer)
 def captured(raw):
  r.setdefault('ssi_chunks',[]).append({'ms':s.now_ms(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'pc':hex(s.m.uc.reg_read(UC_M68K_REG_PC))})
  sink(raw)
 ssi.sink=captured
 for name in ['_render_started','_render_returned']:
  original_window=getattr(ssi,name)
  def window(*args,name=name,original_window=original_window):
   r.setdefault('render_windows',[]).append({'ms':s.now_ms(),'event':name,'ssi_now':ssi.now})
   return original_window(*args)
  setattr(ssi,name,window)
 for pc in [0x40093c98,0x40093caa,0x40093cba,0x40093cc2,0x40093cca,0x40093d2e]:
  def gate(uc,pc,n,d):
   sp=uc.reg_read(UC_M68K_REG_A7)
   r.setdefault('first_copy_guards',[]).append({'ms':s.now_ms(),'pc':hex(pc),'flag':rd(uc,0x419f1fa0),'stack_2c':rd(uc,sp+0x2c),'stack_30':rd(uc,sp+0x30),'cache_states':[rd(uc,0x419f182c+t*72+4) for t in range(4)]})
  s.at(pc,gate)
 def status(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);packet=rd(uc,sp+4)
  if VARIANT.startswith('status-') and s.now_ms()>805 and not r.get('status_fixture'):
   packet=0x47bd0000;s.m.ensure(packet)
   message=bytearray(16);message[0]=0xec;message[1]=0x20;message[13]=3
   uc.mem_write(packet,bytes(message));uc.mem_write(sp+4,u32(packet))
   r['status_fixture']={'ms':s.now_ms(),'kind':'Synthetic transport-status input to actual stock render callback','packet':bytes(message).hex(),'prior_state':rd(uc,0x419eb8cc),'flag':rd(uc,0x419f1fa0),'event_fields_or_metadata_injected':False}
  if packet:r.setdefault('transport_packets',[]).append({'ms':s.now_ms(),'bytes':bytes(uc.mem_read(packet,16)).hex(),'prior_state':rd(uc,0x419eb8cc)})
 s.at(0x400ff684,status)
 if VARIANT.startswith(('deep-','sram-')):
  def packetwrite(uc,access,a,n,value,d):
   if 3980<=s.now_ms()<=3986:
    r.setdefault('packet_writes',[]).append({'ms':s.now_ms(),'offset':hex(a-LO),'size':n,'value':hex(value&((1<<(n*8))-1)),'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'registers':[uc.reg_read(reg) for reg in [UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2]]})
    if a==LO+8 and 3983<=s.now_ms()<=3986:r.setdefault('ordered_packet_trace',[]).append({'event':'parameter word8 update','ms':s.now_ms(),'word8':hex(value)})
  LO=0x80001c00 if VARIANT.startswith('sram-') else 0x10000000
  uc.hook_add(UC_HOOK_MEM_WRITE,packetwrite,begin=LO,end=LO+0x39f)
'''
s=s.replace("r['_guard']=guard.hex()", "r['_guard']=guard.hex()\n"+extra)
s=s.replace('session.close()',"Path('work/audio-copy-'+VARIANT+'.pcm').write_bytes(session.pcm)\n  Path('work/audio-copy-'+VARIANT+'-packets.bin').write_bytes(b''.join(session._probe_packets))\n  Path('work/audio-copy-'+VARIANT+'-voices.bin').write_bytes(b''.join(session._probe_voices))\n  session.close()")
if variant.startswith('held'):
 s=s.replace("old=rd(session.m.uc,CURRENT)","""old=rd(session.m.uc,CURRENT)
 session.tap(session.code('T3'),hold_ms=100,after_ms=100)
 session.press(session.code('1'));session.run_ms(200);mark('held before play')""")
 s=s.replace("mark('play')","mark('play');session.release(session.code('1'));session.run_ms(100);mark('released held note')")
if variant=='resume':
 s=s.replace("mark('play')", """mark('play')
 session.run_ms(200);session.tap(session.code('PLAY'),hold_ms=100,after_ms=100);mark('pause play')
 session.press(session.code('1'));session.run_ms(100)
 session.tap(session.code('PLAY'),hold_ms=100,after_ms=100);mark('resume held');session.release(session.code('1'));session.run_ms(100)""")
VARIANT=variant
s=s.replace("'bytes':length,'expected':", "'bytes':length,'source_sha256':hashlib.sha256(bytes(uc.mem_read(src,length))).hexdigest(),'expected':")
s=s.replace("r.setdefault('copy_checks',[]).append(item)", "item['payload_equal']=hashlib.sha256(bytes(uc.mem_read(int(item['destination'],16),item['bytes']))).hexdigest()==item['source_sha256'];r.setdefault('copy_checks',[]).append(item)")
exec(compile(s,'audio-copy-probe','exec'))
