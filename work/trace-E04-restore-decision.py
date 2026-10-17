from pathlib import Path
s=Path('work/trace-E04-source-origin.py').read_text()
cases=[('blank_E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin','work/user-session-audio/stock/plusdrive.img'),('valid_first_stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin','work/os144/PC_ONLY-saved-mirror-valid_first.img'),('valid_first_E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin','work/os144/PC_ONLY-saved-mirror-valid_first.img'),('invalid_first_valid_second_E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin','work/os144/PC_ONLY-saved-mirror-invalid_first_valid_second.img')]
s=s.replace('cases=cases[-1:]','cases='+repr(cases))
s=s.replace('Digitone-E04-source-origin-checks.json','Digitone-E04-restore-decision-checks.json')
s=s.replace('work/source-origin-','work/restore-decision-')
anchor='   def serialized(uc,pc,size,data):'
addition=r'''   row.setdefault('restore_decisions',[])
   labels={0x400a8360:'restore_entry',0x400a838c:'first_header_result',0x400a83aa:'second_header_result',0x400a83fa:'try_SPI_recovery',0x400a825c:'SPI_recovery_failure',0x400a8402:'initialize_defaults',0x400a8442:'select_first_bank',0x400a83b0:'selected_header_flags',0x400a83da:'payload_read_gate',0x400a83f4:'full_payload_read_return',0x400a8410:'publish_selected_bank'}
   def decision(uc,pc,size,data):
    row['restore_decisions'].append({'stage':stage,'label':labels[pc],'pc':hex(pc),'estimated_instructions':done,'d0':hex(uc.reg_read(UC_M68K_REG_D0)),'d2':hex(uc.reg_read(UC_M68K_REG_D2)),'sr':hex(uc.reg_read(UC_M68K_REG_SR)),'global_flags':read(0x402296f0,4),'selected_bank':read(0x402369e4,4),'header':read(0x40555ee4,0x68)})
   for pc in labels:mm.uc.hook_add(UC_HOOK_CODE,decision,begin=pc,end=pc)
'''
assert anchor in s;s=s.replace(anchor,addition+anchor)
exec(compile(s,'E04-restore-decision-wrapper','exec'))
