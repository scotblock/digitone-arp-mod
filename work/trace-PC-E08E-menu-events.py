from pathlib import Path
s=Path('work/test-PC-E08E-menu-panel.py').read_text()
s=s.replace("for label in ['stock','corrected']:","for label in ['corrected']:")
s=s.replace("row={'label':label,'page_calls':[],'marks':[],'tag_writes':[]}","row={'label':label,'page_calls':[],'marks':[],'tag_writes':[],'raw_events':[]}")
needle="        def called(u,pc,n,d):"
extra='''        from unicorn.m68k_const import UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_A4
        def raw_event(u,pc,n,d):
            ptr=u.reg_read(UC_M68K_REG_D2)
            row['raw_events'].append({'phase':phase,'pc':hex(pc),'A4':hex(u.reg_read(UC_M68K_REG_A4)),'D3':hex(u.reg_read(UC_M68K_REG_D3)), 'event':bytes(u.mem_read(ptr,24)).hex()})
        for pc in [0x4003fb8a,0x4003fc56,0x4003fb9c]:s.at(pc,raw_event)
'''
s=s.replace(needle,extra+needle)
s=s.replace('s.run_ms(6500);','s.run_ms(800);')
s=s.replace('audio=True','audio=False')
s=s.replace('for track in [4,5,0]:','for track in [4]:')
s=s.replace("['TRIG','SYN1','SYN2','FLTR','AMP','LFO']:","['SYN1','SYN2']:")
s=s.replace("[(0,'SYN1'),(5,'SYN2'),(4,'SYN2')]","[(4,'SYN2'),(4,'SYN1')]")
s=s.replace('outputs/Digitone-E08E-PC-menu-panel.json','outputs/Digitone-E08E-PC-menu-event-trace.json')
s=s.replace('work/PC-menu-panel-','work/PC-menu-event-trace-')
s=s.replace("'PC-menu-'+label", "'PC-menu-event-'+label")
exec(compile(s,'native-menu-event-trace','exec'))
