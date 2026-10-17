from pathlib import Path
p=Path('work/validate-E03-continuous-queue-action.py').read_text()
a=p.index('  elif pc==0x400e61cc:');b=p.index('  elif pc==0x40016fb4:',a);p=p[:a]+p[b:]
p=p.replace('0x400c92ac,0x400e61cc,','0x400c92ac,')
p=p.replace('m.uc.mem_write(VIEW+0x98,u32(PROVIDER))','m.uc.mem_write(VIEW+0x98,u32(PROVIDER));m.uc.mem_write(VIEW+0x2c,u32(LIST))')
p=p.replace('def consume(m):','def consume(m, stop_callback=None):')
p=p.replace(" h=m.uc.hook_add(UC_HOOK_CODE,empty,begin=0x40019cd4,end=0x40019cd4)"," h=m.uc.hook_add(UC_HOOK_CODE,empty,begin=0x40019cd4,end=0x40019cd4)\n stop=m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:uc.emu_stop(),begin=stop_callback,end=stop_callback) if stop_callback else None")
p=p.replace(' finally:m.uc.hook_del(h)',' finally:\n  m.uc.hook_del(h)\n  if stop:m.uc.hook_del(stop)')
p=p.replace(' assert m.uc.reg_read(UC_M68K_REG_PC)==0x40019cd4',' assert m.uc.reg_read(UC_M68K_REG_PC)==(stop_callback or 0x40019cd4)')
p=p.replace('case.update(no_flash_calls=True,work_queue_drained=True,context_released=context in m.freed)','case.update(no_flash_calls=True,work_queue_drained=True,context_released=context in m.freed)\n    assert int.from_bytes(m.uc.mem_read(Q+4,4),\'big\')==1\n    m.uc.mem_write(STACK-0x1800,b\'\\xa7\'*0x2000);consume(m,stop_callback=0x400c9c6a)\n    case.update(error_callback_reached_by_stock_consumer=True,temporary_worker_frames_overwritten=True)')
p=p.replace('  case.update(program_calls=',"  assert bytes(m.uc.mem_read(0x40000400,len(stock)))==stock;case['stock_executable_unchanged_in_model']=True\n  case.update(program_calls=")
p=p.replace('0x400a87f0,0x400c93aa,','0x400a87f0,0x400c93aa,0x400e61cc,')
Path('work/validate-E03-continuous-queue-action.py').write_text(p)
