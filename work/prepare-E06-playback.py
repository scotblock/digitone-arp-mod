from pathlib import Path
s=Path('work/test-E06-PC-playback.py').read_text()
s=s.replace("'quantize':[],'pitches':[]", "'quantize':[],'degrees':[],'arp_setting_fixtures':[],'pitches':[]")
s=s.replace("row['quantize'].append(x)", "row[x.pop('kind','quantize')].append(x)")
anchor='    session.at(qpc,quantize)'
add='''
    def degree(u,pc,n,d):
     sp=u.reg_read(UC_M68K_REG_A7);ret=rd(u,sp);fallback,word,base,offset,octave=[rd(u,sp+i) for i in [4,8,12,16,20]]
     offset=offset-0x100000000 if offset&0x80000000 else offset
     raw=((word>>7)&63)-1;root=word&127;expected=fallback
     if word>>31 and not word&0x7fff8000 and raw in rows and base<128 and -128<=offset<=127:
      pcs=rows[raw];held=min((v for v in range(128) if (v-root)%12 in pcs),key=lambda v:(abs(v-base),v));pc0=(held-root)%12;cycles,index=divmod(pcs.index(pc0)+offset,len(pcs));expected=held-pc0+cycles*12+pcs[index]+octave
      if not 0<=expected<256:expected=-1
     assert ret not in pending
     pending[ret]={'kind':'degrees','ms':session.now_ms(),'base':base,'offset':offset,'octave':octave,'word':hex(word),'expected':expected&0xffffffff}
     if ret not in installed:session.at(ret,returned);installed.add(ret)
    session.at(cfg['degree_address'],degree)
'''
assert anchor in s;s=s.replace(anchor,anchor+add)
anchor="   session.at(0x4009e890,lambda"
add='''   def arp_fixture(u,pc,n,d):
    if scenario!='scale':return
    track=rd(u,u.reg_read(UC_M68K_REG_A7)+4)
    if track>=4:return
    state=0x413915f4+track*40;settings=rd(u,state+0x20)
    if not 0x40000000<=settings<0x48000000:return
    u.mem_write(settings+0x111,bytes([0]));u.mem_write(settings+0x113,bytes([7]));u.mem_write(settings+0x114,bytes.fromhex('00ff'));u.mem_write(settings+0x116,bytes(range(8)))
    if not any(x['settings']==hex(settings) for x in row['arp_setting_fixtures']):row['arp_setting_fixtures'].append({'track':track,'settings':hex(settings),'length':8,'offsets':list(range(8)),'range':0,'before_stock_selector':True})
   session.at(0x40097e46,arp_fixture)
'''
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s.replace('bytes([62])','bytes([60])').replace("'root':62", "'root':60")
s=s.replace("send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])", "send([0x90|channel,60,100] if scenario=='scale' else [0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])")
s=s.replace("if scenario=='scale':assert any(x['actual']!=x['note'] for x in row['quantize'])", "if scenario=='scale':\n    assert row['degrees'] and all(x['matches'] for x in row['degrees']);assert set(range(8))<=set(x['offset'] for x in row['degrees']),row['degrees']\n    examples=[x for x in row['degrees'] if x['base']==60 and x['octave']==0 and x['word']=='0x800000bc'];assert examples\n    assert set([60,62,64,65,67,69,71,72])<=set(x['actual'] for x in examples),examples")
s=s.replace("'No physical cache, timing, DMA or hardware-ready claim.'", "'Eight-step arp settings are applied as disclosed PC fixtures before the actual stock selector; guest capture, eligibility and hook execution remain native.','No physical cache, timing, DMA or hardware-ready claim.'")
Path('work/test-E06-PC-playback.py').write_text(s)
