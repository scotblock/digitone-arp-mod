import pathlib,json,hashlib
O=pathlib.Path('outputs');cold=json.loads((O/'Digitone-fast-table-cold-startup.json').read_text());witness=json.loads((O/'Digitone-copied-table-read-witness.json').read_text());bounds=json.loads((O/'Digitone-table-copy-cache-preconditions.json').read_text())
assert cold['passed'] and witness['passed'] and cold['startup']['failure'] is None
stages=cold['startup']['stages'];q=witness['runs'][0]
assert all(x['table_intact'] and x['code_intact'] and x['guards_intact'] and not x['unexpected_writes'] for x in stages)
assert len(stages[0]['table_copy_writes'])==105 and sum(len(x['table_copy_writes']) for x in stages[1:])==0
assert q['halted'] is None and all(q['checks'].values()) and len(q['table_reads'])==len(q['quantize_calls'])==11
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes={'syx':hashlib.sha256(syx.read_bytes()).hexdigest(),'MAIN':hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()}
assert hashes=={'syx':'0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','MAIN':'ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'}
summary={'firmware_modified':False,'hashes':hashes,'table':cold['lookup_table'],'startup_stages':stages,'startup_events':cold['startup']['events'],'startup_created_playback':{'ms':q['ms'],'table_reads':q['table_reads'],'quantizer_calls':q['quantize_calls'],'checks':q['checks'],'hits':q['hits']},'copy_and_cache_controls':bounds,'cache_programming':{'stock_CACR':'0xa50ce100','stock_ACR0':'0x4007e020','DCINVA':True,'ICINVA':True,'BCINVA':True,'DEC':True,'IEC':True,'data_default_mode':'cache-inhibited precise','ACR0_region':'0x40000000..0x47ffffff','ACR0_data_mode':'copyback','loader_tail_CACR':'0x000cc100','loader_tail_DEC':False},'status':'PC copying, finite preservation, actual table loads, and cache-programming order pass; physical cache coherence and complete loader-to-copier continuity remain unverified.'}
(O/'Digitone-lookup-table-startup-summary.json').write_text(json.dumps(summary,indent=2))
lines=['# Digitone OS 1.42: lookup-table startup and cache handoff','',
 'The PC startup copier now carries the complete optimized image. Copying, preservation through initialization/UI startup, and actual pitch-helper reads pass. Stock cache programming precedes the first helper execution. Physical cache coherence and the complete loader-to-copier path remain unverified; no flashable firmware was created.','',
 '## Copy and lifetime','',
 '- The image is 2,324 bytes: 581 longwords, replacing the previous 473-longword count.',
 '- The 420-byte table occupies 0x47be0770–0x47be0913. All 105 table longword stores execute inside the early copier. The image ends at 0x47be0914, below the private pointer at 0x47be1000.',
 '- The source is a supplied decoded RAM extension at 0x4024f5b0. This test starts at MAIN OS entry; it does not load that extension through the real compressed container.',
 '- The complete image and table survive stock clear, the full stock initializer, intro, settled UI, and snapshot restore. Metadata stays unready during initialization and becomes ready after the stock initializer returns. The table is outside the metadata clear interval.',
 '- No unexpected reserved-region writes are observed across the monitored DDR aliases; adjacent sentinel guards remain intact. This is finite observed coverage, not global ownership certification.','',
 '| Stage | Table copy stores | Table preserved | Guards preserved | Unexpected writes |','|---|---:|---|---|---:|']
for s in stages:lines.append(f'| {s["stage"]} | {len(s["table_copy_writes"])} | {s["table_intact"]} | {s["guards_intact"]} | {len(s["unexpected_writes"])} |')
lines+=['',
 'The playback test restores the startup-created code, table, header, and hooks. It does not reinstall them. Over 10,066 ms, actual quantizer instructions perform 11 single-byte table loads at 0x47be0450, from 0x47be0778 in this workload. Every loaded byte matches the copied image, every quantized result matches its independent expected value, and the image/guards remain intact. The workload includes track selection and pattern requests; this report does not certify every transition or queue ownership case.','',
 'Native boundary controls also pass: the correct 581-longword copy transfers the complete table; the old 473-longword count omits all 420 bytes; a 579-longword count omits the last eight bytes. The next 16 bytes remain untouched in each case. These are PC detections; the bootstrap itself has no newly installed checksum or failure guard.','',
 '## Cache handoff','',
 'Observed stock order after the copier returns:','',
 '1. Stock SRAM initialization and BSS clear run.',
 '2. 0x4000055a programs CACR = 0xa50ce100.',
 '3. 0x40000564 programs ACR0 = 0x4007e020.',
 '4. 0x40000568 continues startup; the first resident execution is the initializer at 0x47be0666, with the complete table already present.','',
 'The CACR write requests data, instruction, and branch invalidation while enabling the caches. ACR0 covers the 0x40000000–0x47ffffff data region in copyback mode. The emulator records programmed values; it does not model self-clearing invalidation bits or cached byte versions. [NXP MCF5441x manual, sections 6.3.1–6.3.2](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=167).','',
 'An isolated native test of the actual relocated stock loader tail (entered after its reader returns) programs CACR = 0x000cc100, then calls the original MAIN entry at 0x400004e8. DEC is clear and IEC is set. Its descriptor pointer and boot flags are supplied fixtures; it does not establish that the complete loader reaches this point with the appended image visible in DDR.','',
 'The relevant precondition is that copied bytes reach memory before invalidate-all. Disabling a cache preserves its old contents; invalidating dirty copyback lines can discard unwritten bytes. These rules explain why register ordering alone is insufficient. [NXP manual, sections 6.3.1 and 6.4.6](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=181).','',
 '| Explicit value-coherence control | Table visible after handoff |','|---|---|',
 '| Copy with data cache disabled; stock invalidation | Yes |',
 '| Same copy; retain old valid cache contents when enabling | No |',
 '| Copy into dirty copyback cache; invalidate without push | No |',
 '| Dirty copyback copy; hypothetical push before invalidation | Yes |','',
 'This small cache-state model tests documented coherence rules, not physical timings or a complete hardware cache. The hypothetical push is a diagnostic control; no extra flush was implemented.','',
 '## Remaining gap','',
 'Next: trace the complete pre-OS loader to the early copier with the appended image, recording cache-control writes and whether the decoded source has reached DDR. That will test the inherited-state assumption beyond the isolated loader tail. Physical execution/cache behavior, global RAM ownership, and natural cached-context capture remain separate limits. Original SysEx and MAIN hashes match the recorded originals.']
(O/'Digitone-lookup-table-startup-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('PASS summary: 581 copied longwords, 105 table stores, 11 native table reads; firmware unchanged.')
