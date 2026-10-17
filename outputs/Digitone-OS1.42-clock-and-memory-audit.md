# Digitone OS 1.42: core-clock and memory/cache timing audit

The firmware points to an intended **264 MHz core / 132 MHz bus**, but the actual board frequency is **not verified**. Adding instruction-cache costs materially reduces the earlier zero-wait margin: the 40-cycle fill scenario passes stock, while the full hooks exceed one nominal render deadline. These are PC sensitivity results, not observed device faults.

Firmware and decoded MAIN OS hashes remain unchanged. No flashable image was generated; no hardware was accessed.

## Clock evidence and its limits

The user's OS 1.42 contains `132000000` (`07de2900`) at three sites. Two are directly followed by division and UART baud-divider programming: immediate instructions at `400028cc` and `40002cd2`, with low divider writes at `400028f6` and `40002cfc`. A third feeds arithmetic at `4008c576`. This establishes the software's peripheral-clock calibration, rather than measuring a physical oscillator. Together with the required core:bus ratio, it supports the intended-frequency inference.

The actual bootstrap entry is `80000e8a`. At `80000eae..80000ec0`, it performs:

```
PLL_DR = (PLL_DR & 0xffff83ff) | 0x00001800
```

This changes OUTDIV3 to 6 and preserves the core/bus divider fields. It polls PLL lock at `80000ed8..80000ee2`; this recovered entry does not establish the PLL multiplier or board reference frequency. The [NXP reference manual, chapter 8](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=202) defines these divisors and the 2:1 ratio.

A native, two-million-instruction bootstrap probe reached `800010be`, recorded that divider write and the DDR setup, and made no simulated flash writes. The engine starts **after** hardware serial boot; its reset PLL control/divider registers are unseeded, and lock/DDR-ready flags are supplied by its hardware model. Consequently, its observed divider value `1800` is **not a valid board clock readout**. This probe is bounded and does not certify every later clock writer.

The updater is normally stored from flash offset `80000`, while the hardware serial-boot header precedes that OS slot. The current extracted OS evidence has not recovered that factory reset configuration or a verified oscillator frequency. Neither 250 MHz nor 264 MHz should be called a measured device clock. The actual main-core clock therefore remains an explicit gap.

## Cache configuration

OS startup writes CACR `a50ce100` at `4000055a` and ACR0 `4007e020` at `40000564`. The same values are preserved in the settled stock snapshot. Decoding them gives enabled data/instruction caches and store buffering; startup requests both cache invalidations. ACR0 marks `40000000..47ffffff` as copyback data memory. Outside matching data regions, the default is cache-inhibited precise. Instruction caching uses the cacheable default; no enabled instruction ACR was recovered in the snapshot.

The proposed helper code and metadata at `47be0000` are within this cached DDR region. The audio output observer watches SRAM addresses. These have different memory paths; observing fresh SRAM stores does not certify DDR code/data coherence.

The [NXP cache chapter](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=163) specifies separate 8 KiB instruction/data caches, each four-way, 128 sets and 16-byte lines, with round-robin replacement and software-managed DMA coherence. The PC sensitivity cache was changed from upstream LRU to a round-robin approximation. It is an occupancy/cost model, not a cache-coherent memory engine.

## Executed instruction-cache sensitivity

Each run used the same stock settled snapshot and pattern 2, real firmware routines with floating-point/bitmap shortcuts disabled, conservative branch costs, dependency stalls and a **250 MHz assumption**. Tests covered about 280 ms each. The full-hook cases used the explicit valid-context fixture, because automatic cached-replay context capture/copy remains unfinished.

The extra cost is charged per modeled DDR instruction-line miss; 20 and 40 are deliberately selected sensitivity values, **not measured or certified line-fill penalties**. Data-cache costs and bus contention do not change scheduling in these runs.

| Extra cycles per instruction miss | Variant | Completed renders | Worst render | Margin within 666.668 us | Late renders |
|---|---|---:|---:|---:|---:|
| 20 | Stock | 419 | 533.044 us | 133.624 us | 0 |
| 20 | Full hooks, valid fixture | 419 | 553.292 us | 113.376 us | 0 |
| 40 | Stock | 419 | 652.532 us | 14.136 us | 0 |
| 40 | Full hooks, valid fixture | 419 | 685.124 us | -18.456 us | 1 |

Each run had 391 post-warmup DMA bulk captures: none late, unresolved, or containing unfresh words; none occurred inside the pending mixer-store window. All instruction decoders reported zero mismatches. A nominal render-period overrun and stale DMA output are distinct observations: this run showed the first, not the second. Test duration is too short to certify sustained playback.

## Data-memory assessment

The executed bootstrap programmed DDR_CR16 `02000407`, CR20 `00020708`, CR22 `04030003`, and CR23 `00000004`, among other timing/control values. These are actual guest writes, but cannot be converted directly into one CPU wait penalty: request arbitration, row state, burst transfers, refresh, PHY timing and competing DMA matter.

In the 40-cycle full-hook trace, an additional occupancy observer counted guest DDR data accesses, assuming the observed ACR0 copyback region. It counted 324 data-line fills and 201 dirty evictions during the slowest render, whose instruction-model wall time was 171281 cycles. It tracks cache occupancy across the run but does not implement CPUSHL invalidations, physical fill/store overlap, a store buffer, refresh or contention; initial cache state is a cold fixture. Uncached accesses are counted but have no added cost here.

An **offline projection**, adding the same extra cost to every data fill and dirty eviction of this fixed trace, gives:

| Extra data cycles per fill/writeback | Worst cycles | Overruns at 250 MHz | Overruns at conditional 264 MHz |
|---|---:|---:|---:|
| 0 | 171281 | 1 | 0 |
| 4 | 173381 | 1 | 0 |
| 8 | 175481 | 1 | 0 |
| 16 | 179681 | 1 | 1 |
| 20 | 181781 | 1 | 1 |

The 264 MHz column only changes the comparison budget to 176000 cycles; **it does not rerun event scheduling at that frequency**. Additive costs can overestimate stalls because transfers overlap execution; ignored invalidations/contention can underestimate them. This is sensitivity, not a worst-case bound.

## Consequence and next step

The earlier 244 us margin depended on zero-wait memory. It does not establish device timing safety. Stock and full hooks respond differently to the same added cache-cost assumptions, so the extra timing risk cannot be dismissed solely because the original firmware runs.

The next PC task is to include observed cache maintenance and DDR/DMA arbitration in the timing model, and compare matched stock/full-hook workloads over longer playback. Actual-clock closure requires the serial-boot reset configuration plus a verified board clock reference, or a trustworthy physical clock observation. Neither requires producing modified firmware. Cached-replay context capture/copy also remains unfinished.

Evidence: `Digitone-clock-bootstrap-trace.json`, `Digitone-clock-static-evidence.txt`, the three timing result JSON files, and `Digitone-clock-and-memory-summary.json` in this outputs folder. The firmware hashes in the summary match the original project baselines.
