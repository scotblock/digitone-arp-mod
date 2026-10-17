"""Guest input, descriptor copies and arp selection; PC runtime overlay only."""
from pathlib import Path
exec(compile(Path('work/test-PC-restored-arp-DSP.py').read_text().split("exec(compile(s,'restored-live-arp-DSP','exec'))")[0],'build-live-fixed','exec'))
s=s.replace("[('ordinary','corrected'),('ordinary','stock_sites'),('scale','corrected')]","[('scale','corrected')]")
s=s.replace('Digitone-E04-PC-restored-arp-DSP.json','Digitone-E04-PC-live-capture-session.json')
probe=r'''
    cfg=json.loads(Path('work/os144/PC_ONLY-live-capture-layout.json').read_text());newcode=Path('work/os144/PC_ONLY-live-capture-code.bin').read_bytes()
    uc.mem_write(cfg['base'],newcode);uc.mem_write(cfg['state'],bytes(cfg['state_bytes']));session.m.install_isa_patches_scoped(newcode,cfg['base'])
    for h in cfg['hooks']:
     assert bytes(uc.mem_read(h['site'],h['length'])).hex()==h['stock'];uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
    r['owner_reads']=[];r['live_captures']=[];r['descriptor_bindings']=[];r['live_copies']=[];r['copy_branches']={};r['context_commits']=[];r['actual_pattern_changes']=[];r['pattern_publications']=[];r['quantizer_owners']=[]
    from unicorn import UC_HOOK_MEM_WRITE
    from unicorn.m68k_const import UC_M68K_REG_A6,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D0,UC_M68K_REG_A7,UC_M68K_REG_PC
    def index_read(uc,pc,n,d):
     ptr=rd(uc,0x4138f214);index=uc.reg_read(UC_M68K_REG_D0)
     r['owner_reads'].append({'ms':session.now_ms(),'pointer':hex(ptr),'pointer_index':rd(uc,ptr+0x16119),'returned_index':index,'base':hex(0x407fd414+index*0x1611d)})
    session.at(0x400eae94,index_read)
    def captured_live(uc,pc,n,d):
     pattern=uc.reg_read(UC_M68K_REG_A2);track=uc.reg_read(UC_M68K_REG_D2);note=uc.reg_read(UC_M68K_REG_D3)
     if track>=4 or note>=128:return
     root=bytes(uc.mem_read(pattern+track*0x3d0+0x3cb,1))[0];raw=struct.unpack('b',uc.mem_read(pattern+track*0x3d0+0x3ce,1))[0]
     word=0x80000000|root|((raw+1)<<7)|(track<<13) if root<128 and -1<=raw<35 else 0
     actual=rd(uc,cfg['pending']+track*8+4)
     r['live_captures'].append({'ms':session.now_ms(),'pattern':hex(pattern),'track':track,'original_note':note,'root':root,'raw':raw,'expected':hex(word),'actual':hex(actual),'matches':word==actual,'index_owner_matches':bool(r['owner_reads']) and pattern==int(r['owner_reads'][-1]['base'],16)})
    session.at(0x400eaf50,captured_live)
    def bound_live(uc,pc,n,d):
     inp=uc.reg_read(UC_M68K_REG_A2);track=rd(uc,inp);note=rd(uc,inp+4);state=rd(uc,inp+12)
     if track>=4 or note>=128:return
     r['descriptor_bindings'].append({'ms':session.now_ms(),'input':hex(inp),'track':track,'original_note':note,'state':state,'word':hex(rd(uc,cfg['state']+(track*128+note)*4)),'pending_consumed':rd(uc,cfg['pending']+track*8)==0})
    session.at(0x400ff484,bound_live)
    for pc,label in [(0x400ff5ac,'cached_old'),(0x400ff5d4,'cached_selected'),(0x400ff5f6,'direct')]:
     session.at(pc,lambda uc,pc,n,d,label=label:r['copy_branches'].__setitem__(label,r['copy_branches'].get(label,0)+1))
    for pc in [0x400ff5ae,0x400ff5d6,0x400ff5fc]:
     def copied(uc,pc,n,d):
      sp=uc.reg_read(UC_M68K_REG_A7);dst=rd(uc,sp);src=rd(uc,sp+4);length=rd(uc,sp+8)
      track=None;note=None
      for t in range(4):
       delta=src-(0x43220348+t*0x2a18)
       if 0<=delta<128*72 and delta%72==0:track=t;note=delta//72;break
      word=rd(uc,cfg['state']+(track*128+note)*4) if track is not None else 0
      slot=0x47be1024+(dst-0x419ebe2c)//72*4 if 0<=dst-0x419ebe2c<9216 and (dst-0x419ebe2c)%72==0 else None
      r['live_copies'].append({'ms':session.now_ms(),'return':hex(pc),'source':hex(src),'destination':hex(dst),'length':length,'track':track,'original_note':note,'state':rd(uc,dst+4),'expected':hex(word),'actual':hex(rd(uc,slot)) if slot else None,'matches':bool(slot) and word==rd(uc,slot),'bytes_match':bytes(uc.mem_read(src,length))==bytes(uc.mem_read(dst,length))})
     session.at(pc,copied)
    def committed(uc,pc,n,d):
     sp=uc.reg_read(UC_M68K_REG_A7)
     r['context_commits'].append({'ms':session.now_ms(),'identity':rd(uc,sp+8),'word':hex(rd(uc,sp+12)),'track':rd(uc,sp+16)})
    session.at(0x47be004e,committed)
    def published(uc,access,address,size,value,d):
     r['pattern_publications'].append({'ms':session.now_ms(),'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'before':hex(rd(uc,address)),'value':hex(value),'size':size})
    uc.hook_add(UC_HOOK_MEM_WRITE,published,begin=0x4138f214,end=0x4138f217)
    def pitch_owner(uc,pc,n,d):
     sp=uc.reg_read(UC_M68K_REG_A7);r['quantizer_owners'].append({'ms':session.now_ms(),'pattern':hex(rd(uc,0x4138f214)),'note':rd(uc,sp+4),'word':hex(rd(uc,sp+8))})
    session.at(info['layout']['quantize']['address'],pitch_owner)
    uc.hook_add(UC_HOOK_CODE,strict,begin=cfg['base'],end=cfg['base']+len(newcode)-1)
'''
anchor="   s=Session(case['ui_snapshot']";assert anchor in s;s=s.replace(anchor,probe+'\n'+anchor)
# Distinguishable scale fixtures; guest selection supplies owner identity.
s=s.replace("   s.tap(s.code('STOP'),hold_ms=100,after_ms=100)","   s.m.uc.mem_write(0x40813531+0x3cb,bytes([65]));s.m.uc.mem_write(0x40813531+0x3ce,bytes([5]))\n   s.tap(s.code('STOP'),hold_ms=100,after_ms=100)",1)
handoff=r'''   oldpattern=rd(s.m.uc,0x4138f214)
   s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(3000)
   newpattern=rd(s.m.uc,0x4138f214)
   r['actual_pattern_changes'].append({'before':hex(oldpattern),'after':hex(newpattern),'completed':oldpattern!=newpattern,'index':rd(s.m.uc,newpattern+0x16119)})
'''
s=s.replace("   send([0xb0|channel,64,127])",handoff+"   send([0xb0|channel,64,127])")
s=s.replace('62,100','65,100').replace('62,0','65,0')
s=s.replace("   send([0x90|channel,65,100])", "   s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN1'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200)\n   s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('KEYBOARD'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200)\n   s.tap(s.code('NO'),hold_ms=100,after_ms=100)\n   send([0x90|channel,65,100])")
s=s.replace("   r['passed']=True","   assert r['live_captures'] and all(x['matches'] and x['index_owner_matches'] for x in r['live_captures'])\n   assert r['live_copies'] and all(x['matches'] and x['bytes_match'] for x in r['live_copies'])\n   assert all(x['returned_index']==x['pointer_index'] for x in r['owner_reads'])\n   assert any(x['word']!='0x0' for x in r['quantize'][1:])\n   r['passed']=True")
s=s[:s.index("out['ordinary_comparisons']=[]")]+"out['passed']=all(c['passed'] for c in out['cases']);dest.write_text(json.dumps(out,indent=2));assert out['passed']\n"
exec(compile(s,'live-capture-session','exec'))
