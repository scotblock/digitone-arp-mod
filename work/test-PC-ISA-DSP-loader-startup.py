from pathlib import Path
s=Path('work/test-PC-ISA-loader-startup.py').read_text()
s=s.replace("'ISA-loader-startup-'","'ISA-DSP-loader-startup-'")
s=s.replace('Digitone-E04-PC-ISA-loader-startup.json','Digitone-E04-PC-ISA-DSP-loader-startup.json')
addition=r'''
s=s.replace('  image=Path(imgfile).read_bytes();',"  dsp_section=Path('work/os144/section-7-stored.bin').read_bytes()\n  assert dsp_section==Path('work/os144-emulator-E02-engine/sections/section_7_BLOB.bin').read_bytes()\n  Path(paths.sections,'section_7_BLOB.bin').write_bytes(dsp_section)\n  row['DSP_section_sha256']=hashlib.sha256(dsp_section).hexdigest()\n  image=Path(imgfile).read_bytes();")
s=s.replace("   held['ev']=ev", "   held['ev']=ev\n   row['DSP_model']=type(ev['dsplink']).__name__\n   assert row['DSP_model']=='DspCpu'")
s=s.replace("  row['ui_snapshot']=paths.gui_raw", "  row['DSP_intro_renders']=held['ev']['dsplink'].renders\n  row['DSP_booted']=held['ev']['dsplink'].booted\n  row['ui_snapshot']=paths.gui_raw")
'''
s=s.replace("s=s.replace('paths.cold,budget=', 'paths.cold,out=paths.gui_raw,budget=')",addition+"\ns=s.replace('paths.cold,budget=', 'paths.cold,out=paths.gui_raw,budget=')")
exec(compile(s,'DSP-loader-startup','exec'))
