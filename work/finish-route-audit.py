from pathlib import Path
import sys, json, hashlib
root = Path(__file__).resolve().parents[1]
out = root / 'outputs'
sys.path.insert(0, str(out))
import digitone_event_context_model as context
import digitone_firmware_route_checks as route
import digitone_behavior_model as behavior
import digitone_retained_pitch_checks as pitch
results = [(pitch.checks(), 'Digitone-retained-pitch-check-results.json'),
           (context.checks(), 'Digitone-event-context-model-results.json'),
           (route.checks(), 'Digitone-firmware-route-check-results.json'),
           (behavior.checks(), 'Digitone-behavior-model-results.json')]
for result, name in results:
    (out / name).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(name, result['scenarios_passed'])
p = out / 'Digitone-OS1.42-event-context-model.md'
s = p.read_text(encoding='utf-8')
s = s.replace('**14 lifecycle scenarios**', '**15 lifecycle scenarios**')
s = s.replace('Context decoding is allowed only for type-zero synth events.', 'Context decoding is allowed only for synth events of type zero or one.')
s = s.replace('requires the arp flag, type zero,', 'requires the arp flag, type zero or one,')
s = s.replace('| Type-two pointer event recycled into a synth-note event | Passed |', '| Type-two pointer event recycled into a synth-note event | Passed |\n| Cached type-one synth event and independent snapshot copy | Passed |')
notice = ('**Subsequent firmware-audit correction:** cached synth events use type 1 as well as type 0. '
          'The harness now admits both. Continuing remapped arp ticks bypass destination setup, so its '
          'strict incoming-event context guard loses coverage on those ticks. That guard remains in '
          'the harness to reproduce the gap; it is not a complete integration design. See '
          '`Digitone-OS1.42-producer-copy-remap-verification.md` for the corrected proposal and outstanding proofs.\n\n')
if notice not in s:
    s = s.replace('# PC-only event context model: results\n\n', '# PC-only event context model: results\n\n' + notice)
p.write_text(s, encoding='utf-8')
hashes = {}
for path in [Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'), root / 'work/section-3.bin']:
    hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
expected = ['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda', 'ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
assert list(hashes.values()) == expected
print(json.dumps(hashes, indent=2))
