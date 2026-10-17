"""Record exact native MIDI-tail capacity and project-adapter limitations."""
from pathlib import Path
import json,hashlib,math
main=Path('work/os144/section-3.bin').read_bytes();MB=0x40000400
def raw(at,n):return main[at-MB:at-MB+n]
# Actual stock encoder clears all six trailing bytes of the 172-byte record.
assert raw(0x40008228,16).hex()=='4878000642a7486a00a64eb9400fbb20'
# The final runtime flag word is stock data, copied from the serialized +0xa4.
assert raw(0x40008222,6).hex()=='356800a200a4'
assert raw(0x400081de,8).hex()=='716900a4214000a0'
bridge=json.loads(Path('work/os144/E08-PC-settings-codec-bridge-layout.json').read_text())
assert bridge['runtime_slot']==158 and bridge['serialized_slot']==166
assert bridge['serialized_bytes']==172 and bridge['runtime_bytes']==164
target=Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx')
digest=hashlib.sha256(target.read_bytes()).hexdigest();assert digest=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
result=dict(PC_only=True,passed=True,E09A_unchanged=True,E09A_sha256=digest,
 native_MIDI_record=dict(runtime_bytes=164,serialized_bytes=172,tail_clear_site=hex(0x40008228),zeroed_tail=[166,172],existing_E09A_tag=[166,168],remaining_bytes=4,stock_flag_source=[164,166],stock_runtime_flags=[160,164]),
 sequence_information_lower_bound_bits=math.ceil(16*math.log2(49)+16+4+math.log2(12)+math.log2(36)+1),
 findings=['Four remaining MIDI-tail bytes cannot hold sixteen independent -24..24 offsets plus rests, length, root/scale and enable.','The runtime flag field at +0xa0 is stock-owned, not extra storage.','Native project record padding described by DNX is a candidate for investigation only; zero-filled bytes do not establish ownership or survival through native codecs.','The explicit slot/owner bank API has no automatic publisher or project save/load adapter. It must not be keyed from a UI pointer or queued panel request without a consumed-pattern witness.'],
 native_project_persistence=False,automatic_pattern_binding=False,
 next_native_targets=['Trace the kit serializer and complete project-image writer/reader; establish a versioned extension location or an owned separate-file route.','Connect exact pattern identity, accepted editor publication, copy/clear and quiescent replacement to the bank before claiming automatic per-pattern recall.','Run an actual native save -> change -> reload -> cold restart test, with no PC sidecar import.'])
Path('outputs/Digitone-E10-PC-persistence-route.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
