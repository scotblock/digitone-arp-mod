from pathlib import Path
exec(Path('work/os144-stock-env.py').read_text())
import json,time,traceback
out=Path('outputs/Digitone-OS1.44-stock-startup.json')
r={'firmware_modified':False,'version':'1.44','progress':[],'failure':None,'options':{'ddr':DDR,'custom_hooks':False},'limits':['Emulator direct main-image startup, not actual bootloader-to-main execution.','Engine device/storage/ISA stand-ins apply; this is functional evidence, not physical timing certification.']}
start=time.monotonic()
def progress(ev):
 r['progress'].append({'step':ev.step,'kind':ev.kind,'done':ev.done,'text':ev.text});r['elapsed_seconds']=time.monotonic()-start
 out.write_text(json.dumps(r,indent=2));print(ev.step,ev.kind,ev.text,flush=True)
try:
 r['snapshot']=bs.first_run(paths,progress=progress,options={'ddr':DDR})
 r['snapshot_sha256']=hashlib.sha256(Path(r['snapshot']).read_bytes()).hexdigest()
 r['main_sha256']=hashlib.sha256(Path(paths.main_img).read_bytes()).hexdigest()
except BaseException:
 r['failure']=traceback.format_exc();print(r['failure'],flush=True)
finally:
 r['firmware_sha256_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();r['elapsed_seconds']=time.monotonic()-start;out.write_text(json.dumps(r,indent=2))
