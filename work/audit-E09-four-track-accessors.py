"""Execute stock MIDI-handle indexing; document current extension constraints."""
from pathlib import Path
import json,sys,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
main=Path('work/os144/section-3.bin').read_bytes();m=Machine(ddr=0x8000000)
for a in [0x4001d000,0x47bcf000]:m.ensure(a)
code=main[0x4001d000-0x40000400:0x4001e000-0x40000400];m.uc.mem_write(0x4001d000,code);m.install_isa_patches_scoped(code,0x4001d000)
root=0x419f1000;rows=[]
for t in range(4):
    ptr=call(m,0x4001dd1a,[root+0x250,t],stack_top=0x47bcf800,limit=1000)
    assert ptr==root+0xff8+t*0x44
    rows.append({'track':'M'+str(t+1),'descriptor_track_index':t,'UI_handle_root_offset':hex(ptr-root),
      'UI_handle_stride':0x44,'parameter_record_bytes':164,'active_kit_record_offset':hex(0x5ce+t*0xa4),
      'stock_cached_record_slot':hex(0x419c5b14+t*4)})
out={'PC_only':True,'passed':True,'actual_stock_handle_getter_executed':True,'tracks':rows,
 'record_and_cache_offsets_basis':'Native consumer arithmetic at 0x400f43be..0x400f43de plus the established M1 record base; broader owner lifetimes still require per-track audit.',
 'current_extension_limits':['One 344-byte M1 state and one 64-byte private event arena.','M1-only descriptor predicate, fixed UI handle, fixed cache slot and fixed kit offset.','One source owner/request owner and one settings publication slot.','Page title, shortcut guard and getters currently M1-specific.'],
 'four_track_storage_minimum':{'independent_states_at_current_size':4*344,'independent_arenas_at_current_size':4*64,'additional_state_and_arenas_bytes':3*(344+64)},
 'sequencer_storage_minimum_per_track':{'signed_step_offsets':16,'enabled_step_mask':2,'length':1,'minimum_new_serialized_bytes':19},
 'sequencer_blockers':['Existing two-byte extension word already encodes MODE/RATE/GATE; it cannot hold 16 step offsets.','A separate owned saved block/schema and import/export migration are required, or an explicitly temporary RAM-only prototype.','Synth editor callbacks cannot safely be reused with MIDI records without new accessors.','Normal sequenced chord feeding and queued/sustained handoff must be proved before four-track release.'],
 'implemented_M2_M4_arp':False,'implemented_MIDI_step_editor':False}
Path('outputs/Digitone-E09-four-track-sequencer-audit.json').write_text(json.dumps(out,indent=2))
print('PASS native handle lookup for M1–M4; independent-state and sequencer storage requirements recorded.')
