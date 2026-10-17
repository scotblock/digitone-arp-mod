"""Short panel run: capture completed OLED frames without repeating filesystem IO."""
from pathlib import Path

driver = Path('work/test-E08-native-M1-controls.py').read_text()
tail = '''
start = s.index(" phase='save_menu';")
end = s.index(" out['halted']=s.halted", start)
s = s[:start] + s[end:]
s = s.replace('Digitone-E08-native-M1-controls.json', 'Digitone-E08-M1-completed-display.json')
s = s.replace('E08-native-M1-controls-', 'E08-M1-completed-display-')
exec(compile(s, 'E08-completed-OLED-capture', 'exec'))
'''
driver = driver.replace("exec(compile(s,'E08-native-M1-device-controls','exec'))", tail)
exec(compile(driver, 'E08-display-test-driver', 'exec'))
