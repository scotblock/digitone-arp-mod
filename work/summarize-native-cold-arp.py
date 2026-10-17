"""Produce a concise audited record of the cold startup/playback experiment."""
import pathlib,json,hashlib
out=pathlib.Path('outputs');r=json.loads((out/'Digitone-native-cold-arp-results.json').read_text());g=json.loads((out/'Digitone-native-startup-guard-results.json').read_text())
assert r['passed'] and r['startup']['failure'] is None and g['failure'] is None
p=r['runs'][0];assert all(p['checks'].values()) and p['halted'] is None
stages=r['startup']['stages'];assert len(stages)==3
assert all(s['code_intact'] and s['guards_intact'] and s['ready']==1 and s['stock_pool_links_valid'] and not s['unexpected_writes'] for s in stages)
assert stages[0]['hits']['copier_entry']==stages[0]['hits']['initializer_entry']==stages[0]['hits']['initializer_caller_return']==1
assert len(g['cases'])==5 and all(all(c['checks'].values()) for c in g['cases'])
changed=[i for i in p['pitches'] if i['before']!=i['after']];assert len(changed)==11
eligible=[c for c in p['captures'] if c['pool_eligible']];assert len(eligible)==18 and all(c['matches'] for c in eligible)
orig=pathlib.Path('work/section-3.bin').read_bytes();copy=pathlib.Path('work/native-cold-arp-emulator/sections/section_3_MAIN_OS.bin').read_bytes();assert copy==orig
summary={'passed':True,'bootstrapped_code_bytes':r['code_bytes'],'copy_longs':r['startup']['copy_longs'],'initializer_entries':1,'eligible_captures':len(eligible),'unsupported_producer_events':len(p['captures'])-len(eligible),'constrained_arp_notes':len(changed),'fixed_point_outputs':len(p['pitches']),'failure_guard_cases':len(g['cases']),'firmware_modified':False,'firmware_sha256':r['firmware_after'],'main_section_sha256':hashlib.sha256(orig).hexdigest(),'limitations':['MAIN OS entry with supplied flags; pre-OS loader and physical caches not tested.','Cold, intro, settle and playback preserve guest state through explicit emulator snapshots; separate engine instances.','Synthetic initialized +Drive copied into a separate experiment directory.','Playback source root/scale and later edit supplied as explicit PC fixtures.','Fail-closed guards spin with interrupts masked, rather than recover into stock.','Chromatic audio discrepancy from previous test remains uninvestigated.','Queued/held live-note capture, complete writer coverage and global storage ownership remain incomplete.']}
(out/'Digitone-native-cold-arp-summary.json').write_text(json.dumps(summary,indent=2))
text=f'''# Digitone OS 1.42 — corrected bootstrap through playback

The corrected 1,892-byte helper image now reaches playback through actual native startup instructions. The PC bootstrap copies it into reserved RAM, initializes unavailable metadata, and the wrapper calls the complete stock initializer before marking the context ready. The resulting state survives the intro and settling stages and produces 11 independently verified scale-constrained arp notes. Firmware files remain unchanged.

## Installation and lifetime evidence

The early hook at `40000538` calls a {r['startup']['bootstrap_bytes']}-byte PC-only bootstrap at `4024f4b0`. Its source is `4024f5b0`; it copies {r['startup']['copy_longs']} longwords (1,892 bytes) into `47be0000`. The private pointer/header at `47be1000`/`47be1004` remain separate from the stock owner.

The native initializer is at `{r['startup']['initializer']}`. The prior comparison-lowering relocation now exports its corrected address and trampoline address explicitly. The original startup source was rebuilt with the corrected length and initializer target.

| Boundary | Ready | Stock owner | Evidence |
|---|---:|---|---|
| Bootstrap return | 0 | 0 | Copied code matches byte for byte |
| Wrapper entry | 0 | 0 | Exactly one initializer invocation |
| Stock initializer body | 0 | 0 during observed loop | Interrupt mask held at level 7 |
| Return to stock caller | 1 | `419c38c0` | Readiness published after stock return |
| Cold boot parked | 1 | `419c38c0` | Code, guards and 64 stock links intact |
| Intro complete | 1 | `419c38c0` | Same copied code/header preserved |
| Interface settled | 1 | `419c38c0` | Same copied code/header preserved |

The watched bootstrap performed 1,210 writes: 473 code longwords, 733 pointer/header/metadata clear longwords, and four pointer/header publication writes. The stock clear made 729 metadata writes while readiness was zero and interrupts masked. The wrapper then made the readiness publication write. No unexpected watched write occurred through any of the eight DDR aliases; unused reserved bytes and guards remained intact.

The stock initializer body boundary was observed 128 times within its own loop; this is not 128 initializer invocations. Wrapper entry and caller return were each observed once.

Cold startup parked at an estimated 122M instructions. The interface became live after the intro and settled with 166 consecutive main-interface frames and no overlays. These are emulator stage metrics, not measured device timing.

## Playback from startup-produced state

Playback restored the snapshot produced by that cold-start chain. It verified the helper bytes, readiness and patch targets already present. It did not copy helpers again, manufacture a ready header or reinstall the note hooks.

Play, track/trig inputs, pattern 2 then pattern 1, and Stop completed over {p['ms']/1000:.2f} emulated seconds without halting. The execution hit {p['hits']['allocator']} allocator entries, {p['hits']['producer']} producer finalizations, {p['hits']['acceptance']} acceptance entries, one retained-copy commit and {p['hits']['pitch_site']} pitch boundaries.

All 18 supported fixed-pool captures matched their actual source root/scale/track. Two events outside that pool remain unsupported. The existing running arp on user track 3 captured `800040bd` after the PC fixture selected root 61/raw scale 0; the fixture edited that source to root 62/raw scale 5 after capture. Actual acceptance and selection were executed by firmware.

Eleven subsequent notes still read the retained word and changed `57 → 56`, `69 → 68`, `81 → 80`, matching the independent scale-table oracle. All 31 observed outputs matched the fixed-point conversion. Code and unused-region guards remained intact through playback. Audio was generated, but this test does not resolve the earlier chromatic audio mismatch.

## Failure guards and corrections

Five additional native tests supplied a wrong initializer argument, null private pointer, bad magic, bad version and bad metadata size. Each entered the terminal guard spin with interrupts masked, before reaching the stock initializer body. Stock owner, pool bytes and private metadata were unchanged. This is a fail-closed halt, not a recovery continuation.

The first cold harness attempt tried to observe an unmapped owner page before stock initialization; the observer was corrected to provision the engine's zero-backed page. A subsequent draft copier had an incorrect loop branch displacement and used a memory clear encoding. The final copier uses the corrected backward branch and a zero-register store. These corrections were made only to PC experiment code; the final cold startup/playback and five guard tests passed.

## Scope and next step

The chain begins at MAIN OS application entry with boot argument `00140000` explicitly supplied. The pre-OS loader, extension acceptance, real flash source and physical instruction-cache coherence are not exercised. Source helper bytes are staged in emulator RAM, not packaged into firmware. The stock VBR/cache sequence remains in the executed path, but the engine result is not proof of physical cache behavior.

Cold, intro, settle and playback use separate native engine instances with guest state preserved through explicit snapshots. All are in a separate experiment directory with a copied, already initialized synthetic +Drive. No stock snapshot is relabeled as a patched startup result. Engine HLE/completion assumptions, unmodelled devices, transient native DMA effects and physical timing remain limitations.

This closes the corrected-code cold application-startup-to-playback gap in the PC model for this boot case. It does not establish full RAM ownership, all startup modes, queued/held live capture, complete writer protection or hardware readiness.

The next focused check is the unexplained chromatic audio discrepancy: compare actual note dispatch values and their timestamps against a stock run from an equivalent cold-start state. Complete live-input/writer coverage and physical cache checks remain separate gates before considering a firmware build.

Original SysEx SHA256: `{r['firmware_after']}`. The extracted original main section and the experiment's copied main section remain identical. No modified firmware or flashable image was produced.

Evidence: `Digitone-native-cold-arp-results.json`, `Digitone-native-startup-guard-results.json`, and `Digitone-native-cold-arp-summary.json`.
'''
(out/'Digitone-OS1.42-bootstrap-through-playback-audit.md').write_text(text,encoding='utf-8')
print('PASS cold-start summary:',summary)
