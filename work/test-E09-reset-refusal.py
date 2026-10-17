from pathlib import Path
s=Path('work/test-E08C-reset-refusal.py').read_text().replace('E08C','E09')
s=s.replace("u.mem_write(0x47be2840,struct.pack('>I',admission))", "u.mem_write(0x47be2840,struct.pack('>I',admission))\n        u.mem_write(layout['USB_mirror_records'],struct.pack('>IIII',1,60,1,0))\n        row['USB_pending_owner_is_fixture']=True")
exec(compile(s,'E09-expanded-payload-reset-refusal','exec'))
