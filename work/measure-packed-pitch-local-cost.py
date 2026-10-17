"""Quick cold/warm pitch sanity check; independent of full replay."""
import pathlib
source=pathlib.Path('work/measure-fresh-pitch-local-cost.py').read_text()
source=source.replace("for mode in ['stock','helper']:","for mode in ['original','packed']:\n info=json.loads(pathlib.Path('work/packed-context-build.json').read_text())\n blob=pathlib.Path('work/'+('packed-context-overlay' if mode=='packed' else 'cache-context-overlay')+'.bin').read_bytes()\n layout=info['layout'] if mode=='packed' else json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())")
source=source.replace("m.install_isa_patches_scoped(blob[:1892],ram)","m.install_isa_patches_scoped(blob[:info['code_bytes'] if mode=='packed' else 1892],ram)")
source=source.replace("if mode=='helper':","if mode in ['original','packed']:")
source=source.replace("if v['address']<=pc<v['address']+v['size']","if v['address']<=pc<v['address']+v.get('size',0)")
source=source.replace("  return next((name for name,v in layout.items() if v['address']<=pc<v['address']+v.get('size',0)),'stock')", "  if mode=='packed':\n   roots=sorted((v['address'],name) for name,v in layout.items())\n   return next((name for j,(a,name) in enumerate(roots) if a<=pc<(roots[j+1][0] if j+1<len(roots) else ram+info['code_bytes'])),'stock')\n  return next((name for name,v in layout.items() if v['address']<=pc<v['address']+v.get('size',0)),'stock')")
source=source.replace('Digitone-fresh-pitch-local-cost.json','Digitone-packed-pitch-local-cost.json')
exec(compile(source,'packed-local-pitch-cost','exec'))
