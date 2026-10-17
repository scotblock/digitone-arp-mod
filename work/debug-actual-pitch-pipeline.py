s=open('work/test-actual-capture-and-pitch.py').read()
exec(s.split('# Capture across')[0])
scale_map=json.loads(pathlib.Path('outputs/Digitone-OS1.42-scale-map.json').read_text())
exec('rows='+s.split('rows=',1)[1].split('m=machine();quant_cases=0')[0])
quant_cases=0
exec('import copy\n'+s.split('import copy\n',1)[1])
