"""Verify the continuous M1 controls run beyond its generic no-halt flag."""
from pathlib import Path
import hashlib
import json

folder = Path('outputs')
trace = json.loads((folder / 'Digitone-E08-native-M1-controls.json').read_text())
assert not trace.get('failure'), trace.get('failure')
assert trace.get('halted') is None, trace.get('halted')
steps = {row['label']: row for row in trace['steps']}
checks = []

def word(label, expected):
    actual = steps[label]['MIDI_settings_word']
    assert actual == expected, (label, hex(actual or 0), hex(expected))

word('encoder_1', 0xad32)
word('encoder_2', 0xadb2)
for channel in range(3, 9):
    word(f'encoder_{channel}', 0xadd0)
checks.append('Panel A/B/C select UP, 1/32 and 80%; D through H leave settings unchanged.')
assert trace['T4_data_unchanged'] is True
assert trace['existing_MIDI_fields_unchanged'] is True
checks.append('The captured synth T4 data and existing M1 fields remain byte-identical during edits.')
editing = {'M1_page', 'close', 'apply'} | {f'encoder_{i}' for i in range(1, 9)}
assert not [row for row in trace['sound_lookups'] if row['phase'] in editing]
checks.append('No synth-settings getter executes during the M1 page, edits, close or initial input test.')
assert trace['serialized_settings_after_save'] == 0xadd0
word('change_before_reload', 0xa9d0)
word('load_confirm', 0xadd0)
word('reload_page', 0xadd0)
word('reload_apply', 0xadd0)
assert steps['apply']['M1_config'] == [1, 3, 80, 0], steps['apply']['M1_config']
assert steps['reload_apply']['M1_config'] == [1, 3, 80, 0], steps['reload_apply']['M1_config']
checks.append('Native project save followed by OFF edit and native project reload restores UP/1/32/80% to the actual consumer without another encoder edit.')
for stem in ['settings-accessor-tests', 'settings-codec-bridge-tests',
             'settings-consumer-tests', 'M1-view-guard-tests', 'current-settings-binding-tests']:
    result = json.loads((folder / f'Digitone-E08-{stem}.json').read_text())
    assert result['passed'] is True, stem
checks.append('The accessor, codec, consumer, retained-view and binding contract checks pass.')
e07 = folder / 'Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx'
digest = hashlib.sha256(e07.read_bytes()).hexdigest()
assert digest == 'a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
checks.append('The published E07 container remains unchanged.')
display_path = folder / 'Digitone-E08-M1-completed-display.json'
display = json.loads(display_path.read_text())
assert not display.get('failure') and display.get('halted') is None
display_steps = {row['label']: row for row in display['steps']}
assert display_steps['encoder_3']['MIDI_settings_word'] == 0xadd0
assert display_steps['apply']['M1_config'] == [1, 3, 80, 0]
assert display['T4_data_unchanged'] and display['existing_MIDI_fields_unchanged']
checks.append('A separate completed-frame capture repeats the panel settings and consumer readback; its UP/1/32/80% OLED image was visually inspected.')
result = {'PC_only': True, 'passed': True, 'checks': checks,
          'E07_sha256': digest, 'new_controls_packaged': False,
          'artifact_sha256': {
              str(path): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in [folder / 'Digitone-E08-native-M1-controls.json', display_path] + [
                  Path('work/os144') / f'E08-PC-{name}.bin'
                  for name in ['settings-accessors', 'settings-codec-bridge', 'M1-controls']
              ]
          },
          'limits': [
              'The new controls and codec hooks are loaded as PC overlays after the older packaged E08 startup.',
              'Actual pattern replacement, second-pattern isolation, copy/reset lifetimes and physical storage ownership require further checks.',
              'Only M1 is implemented; M2 through M4 are not enabled.',
              'This is not a hardware-ready firmware release.'
          ]}
(folder / 'Digitone-E08-M1-controls-verification.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
