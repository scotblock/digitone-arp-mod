# E04: cache rationale and physical timing status

Physical cache behaviour and physical render deadlines are **not yet measured**. This audit strengthens the cache argument, corrects an earlier bit description, records an unusable timing-model attempt, and prepares the first stock-hardware recording. E04 is unchanged and remains PC-only.

## Cache ordering established in the instruction model

NXP documents separate data-, instruction- and branch-cache invalidation. Instruction contents can persist across reset, and instruction invalidation stalls subsequent local accesses until complete. Data attributes use ACR0/1/4/5; instruction attributes use different ACRs. See the cache chapter in the [MCF5441x reference manual](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf).

The `a0000000` mask used by earlier copier assertions checks **data-cache enable and store-buffer enable**, not instruction-cache enable. The inherited loader CACR `0008c000` enables instruction caching. Earlier shorthand describing copying before “caching” or “both cache-enable bits” was inaccurate. This was a description/check-coverage error; the stock post-copy invalidation sequence remains present.

New packaged-loader tracing observes these actual CACR writes:

| Instruction address | Value | Relevant effect |
|---|---|---|
| `80000a78` | `000cc100` | Requests instruction and branch invalidation early in the loader |
| `800005e2` | `a508e000` | Enables data/instruction cache and requests data invalidation during loader setup |
| `80000644` | `0008c000` | Leaves data cache/store buffering disabled and instruction caching enabled before MAIN |
| `4000055a` | `a50ce100` | Stock application requests data/instruction/branch invalidation after copying |

The separate application startup trace confirms all 623 longword stores complete before the final control write. The **first helper execution is `47be08a4`**, after that write, with the complete payload exact. The global request includes ICINVA `00000100`, BCINVA `00040000`, and DCINVA `01000000`.

A small value-aware logical cache test seeds old instruction bytes, old data and an old branch target. The documented invalidation sequence removes all seeded stale values in three positive cases. Removing each relevant invalidation produces the corresponding failure in three negative controls. This checks the reasoning against deliberately stale state; it is not silicon emulation or a measurement of physical tags, write completion or invalidation latency.

The cache handoff is therefore supported by stock instruction ordering and the documented mechanism. It has not been tested by executing E04 on a physical Digitone. Stock audio recordings cannot directly establish that property.

## Detailed timing attempt rejected as evidence

Three 200-ms sensitivity runs use core/bus candidates of 264/132 MHz, the actual E04-derived playing snapshot, instruction timing without float/bitmap shortcuts, cache costs and the older shared-DMA/FIFO phase model: restored stock hooks at fill cost 20, E04 at 20, and E04 at 40.

All complete the requested modeled interval without a firmware halt and with no decode mismatches, but **none executes render vector 191 or a pitch/quantizer hook**. The model produces DMA output and completion interrupt 174 while mostly idling. Both the stock control and E04 exhibit this gap. Thus reported FIFO levels, zero underflow flags and short completion-handler costs cannot certify playback deadlines. These runs fail their required render-coverage assertion and are excluded from successful timing evidence. No physical regression conclusion follows.

The 264/132 MHz values and memory costs remain assumptions here. External audio/clock capture cannot directly read the core frequency or internal memory latency. No timing pass is claimed from these runs; adapting the older model's complete 1.44 render/interrupt path is separate work.

## Physical baseline prepared

The user confirmed that a physical stock 1.44 audio/MIDI recording is possible. A receive-only Windows logger has been prepared with no MIDI output capability. Message decoding and MIDI-port enumeration pass on this PC; Windows lists both Elektron Digitone and Rubix22 inputs. Actual clock capture still requires the user's recording.

The supplied guide connects Digitone main L/R to Rubix inputs 1/2 and Digitone MIDI OUT to Rubix MIDI IN. Live records analog audio independently while the logger receives MIDI clock/start/stop. The first take is 60 seconds of stock metronome at 120 BPM, with five seconds of silence on either side. It will allow comparison of audio click spacing, received clock intervals, drift and gross discontinuities. Interface, USB, driver and host timing remain part of the measurement; absolute audio/MIDI latency and sub-millisecond wire jitter are not directly established.

Only after that baseline should a matched busy/arp take be added. Measuring E04 itself would require a separately agreed hardware trial; no firmware installation was performed or requested as part of this recording setup.

## Artifacts

- `Digitone-OS1.44E04-loader-cache-controls.json`
- `Digitone-OS1.44E04-cache-order-valid.json`
- `Digitone-OS1.44E04-cache-stale-state-checks.json`
- Three `Digitone-OS1.44E04-cycle-*.json` records, marked failed execution coverage
- `Digitone-stock-clock-logger.py`
- `Start Digitone stock clock logger.cmd`
- `Digitone-stock-hardware-recording-guide.md`

Subsequent measurement received on 7 October 2026: the stock analog take contains 132 regular metronome clicks, with no missing beat detected or clipping, at approximately 120.020 BPM relative to the Rubix sample clock. The supplied MIDI log is empty. See `Digitone-stock-physical-click-review.md` for measurement methods and limits. This is external stock audio evidence, not physical E04 cache or internal deadline validation. E04 SHA-256 remains `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`.
