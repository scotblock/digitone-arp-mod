# Digitone OS 1.42: larger zero-run placement audit

**No usable portion has been established in `401fd47c..401fdc8c` (2,064 bytes).** Three recovered stock readers can address every four-byte word in this interval. Treating its zero contents as available code space would change values those readers can consume.

## Table relationship

The readers use base `401fcc8c`. The candidate is exactly table entries **508 through 1023**, inclusive:

`address = 401fcc8c + 4 * index`

The previous entry, at `401fd478`, contains `05e49d56`; entries 508..1023 contain zero. The following word at `401fdc8c` contains `ffffffff` and has its own stock references. The two endpoint initialization paths explicitly load entry 1023 at `401fdc88`, reinforcing the table boundary.

## Recovered readers

| Stock instruction slice | Parameters | Index calculation |
|---|---|---|
| `400984fc..4009852c` | Signed words at structure +8e and +90 | First word >>6; sum of both words >>6 |
| `40098a5c..40098aba` | Signed words at structure +8 and +a | First word >>6; sum of both words >>6 |
| `40098fe0..40099022` | Signed words at structure +8 and +a | First word >>6; sum of both words >>6 |

All three use arithmetic right shifts and four-byte indexed reads. Their sum is computed in a 32-bit register, so two positive signed words can produce indices up to 1023. There is no clamp between the recovered parameter loads and these reads. Additional analogous +12c/+12e reads are visible at `40098538..40098574`; they are not needed for this coverage finding.

For each candidate index `i`, supply `sum = 64*i`, first parameter `min(sum,32767)`, second parameter `sum-first`. Both parameters are valid nonnegative signed 16-bit values. At the candidate's first word, `i=508`, the pair is `(32512,0)`. At its last word, `i=1023`, the pair is `(32767,32705)`.

## PC execution

Executed the unchanged stock instruction slices for all **516 candidate indices in each of three readers: 1,548 cases**. Observed both actual memory-read addresses and their returned values. Each reader's summed-index path covers the complete 2,064-byte candidate, with no uncovered four-byte word. Also executed the two unchanged endpoint initialization slices at `4009882c..40098850` and `40098d44..40098d5c`; both load the zero value at `401fdc88` into their stock globals.

These tests supply parameter structures and execute only the recovered reader slices. They do **not** establish that every supplied pair occurs during normal device operation, nor execute complete DSP functions. Proving that a subsection is never read would require upstream constraints excluding its indices across all readers. The current evidence supplies no such restriction, so it cannot certify a subsection for code.

## Placement consequence

The 814-byte shortfall remains. This candidate cannot presently contribute certified executable space. The useful next investigation is a deliberately allocated RAM code buffer: establish where its source bytes would live, when the buffer can be initialized, whether the CPU's configured regions allow execution there, and what instruction-cache synchronization is required. Keep that route as a PC-only design until those conditions are established. Alternatively, smaller resident intervals can be audited individually, but their byte counts alone do not establish ownership.

Original SysEx and decoded-image SHA-256 values were verified unchanged. No firmware was edited, repacked, or sent to hardware.

Evidence: `Digitone-large-zero-table-candidate-audit.json` and `Digitone-large-zero-table-reader-instructions.txt` in this output directory.
