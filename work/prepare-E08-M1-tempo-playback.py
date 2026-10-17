from pathlib import Path
p=Path('work/test-E08-M1-native-playback.py').read_text()
p=p.replace('E08-PC-native-M1-layout.json','E08-PC-install-layout.json').replace('E08-PC-native-M1-code.bin','E08-PC-layout-payload.bin')
p=p.replace("s.m.uc.mem_write(native['base'],native_blob)", "\n for r in native['regions']+native['data_regions']:\n  s.m.ensure(r['base']);s.m.uc.mem_write(r['base'],native_blob[r['base']-native['base']:r['base']-native['base']+r['bytes']])")
a=p.index(' # Native MIDI input and grid recording create the chord;');z=p.index(" out['MIDI_received']=",a)
p=p[:a]+''' def configure(index,pct):
  regs=list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+8))+[UC_M68K_REG_SR,UC_M68K_REG_PC]
  saved={reg:s.m.uc.reg_read(reg) for reg in regs}
  got=native_call(s.m,native['entries']['configure'],[index,pct],stack_top=0x47be7f00,limit=30000);assert got==1
  s.m.uc.reg_write(UC_M68K_REG_SR,saved[UC_M68K_REG_SR])
  for reg,value in saved.items():
   if reg!=UC_M68K_REG_SR:s.m.uc.reg_write(reg,value)
 configure(2,50);s.m.uc.mem_write(native['state']+4,struct.pack('>I',1));state['phase']='initial_live'
 send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100]);s.run_ms(250)
 s.tap(s.code('TEMPO'),hold_ms=70,after_ms=150)
 def sample(label,ms=2000):
  state['phase']=label;start=s.now_ms();clk=rd(s.m.uc,0x80004614);wi=len(out['wire']);s.run_ms(ms)
  row={'phase':label,'begin_ms':start,'end_ms':s.now_ms(),'clock_delta':(rd(s.m.uc,0x80004614)-clk)&0xffffffff,'wire':out['wire'][wi:],'interval_units':rd(s.m.uc,native['state']+32),'gate_units':rd(s.m.uc,native['state']+36)};out['phases'].append(row);mark(label)
 sample('initial_tempo_1_16')
 s.turn(s.encoder('9'),400,after_ms=400);sample('LEVEL_plus400_1_16')
 s.turn(s.encoder('9'),-800,after_ms=400);sample('LEVEL_minus800_1_16')
 configure(1,25);sample('same_tempo_1_8_gate25',1500)
 release_request=s.now_ms();send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.run_ms(450)
 out['release_request_ms']=release_request;out['native_active_at_end']=rd(s.m.uc,native['state']+8);out['native_busy_at_end']=rd(s.m.uc,native['state']+280);out['native_count_at_end']=rd(s.m.uc,native['state']+16)
 for h in native['hooks']:assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['replacement']
 for r in native['regions']:assert bytes(s.m.uc.mem_read(r['base'],r['bytes']))==native_blob[r['base']-native['base']:r['base']-native['base']+r['bytes']]
 out['native_code_preserved']=True;out['native_state_final']=bytes(s.m.uc.mem_read(native['state'],320)).hex()
''' +p[z:]
p=p.replace('Digitone-E08-M1-native-playback.json','Digitone-E08-M1-tempo-playback.json')
Path('work/test-E08-M1-tempo-playback.py').write_text(p)
