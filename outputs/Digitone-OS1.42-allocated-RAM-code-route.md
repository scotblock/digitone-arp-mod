# Digitone OS 1.42: allocated RAM code route

**Allocated RAM is a plausible destination, but a complete installation route is not yet established.** Destination capacity looks adequate. Source-byte survival, full early allocation, relocation, and executable publication still require work. No startup hook or flashable output was implemented.

## Destination and ownership

One concrete design is to enlarge the already proposed persistent owner allocation explicitly. Existing stock records end at owner+14100; metadata ends at owner+14c70. Leave 16 bytes of alignment space and reserve 4 KB of code at **owner+14c80..owner+15c80**. Request **15c80 bytes (89,216)** in total. The current 1,678 bytes of helper instructions fit, with room for further integration; that reserve is not an estimate of final V1 size.

The previous request 14c70 and this new request both calculate to a 20000-byte buddy block. All 128 whole-block placements in the configured 16 MB heap fit the request. These are geometry checks, not execution of the actual allocator. The extra code bytes must be included in the explicit request; allocator rounding alone does not grant their ownership.

## Source lifetime is the immediate obstacle

The main loaded image ends at **4024f4b0**. Stock startup clears **40242000..431dc690**, before entering the application. Appending a helper payload at the image end therefore destroys its source before the later proposed pool initializer could copy it. Allocating a destination does not solve this.

A possible route to audit is an appended source temporarily excluded from the startup clear, followed immediately by allocation/copy/relocation and erasure of that staging interval before ordinary application startup. This changes startup behavior and must restore the stock zero-initialization contract before any affected global is read. It also needs verified loader/decompression bounds and a justified bootstrap layout. It is a proposal, not an implemented or approved placement.

Alternatively, source bytes could occupy independently verified resident space or a supported additional loaded section; neither source route is established. A compression screen of the current fixture bodies produced 994 bytes with zlib and 1,028 with LZMA, already exceeding the existing 864-byte interval before a decompressor, relocations, or dispatch stubs. This does not rule out every compression method, but these methods do not solve source placement.

## Startup allocation evidence

The stock allocator at **400dab8c** checks an initialization flag at **401fe590**. On first use it creates heap/free-list state before publishing that flag. This is lazy initialization, rather than dependence on a separately identified allocator constructor.

Its lock acquisition at **40001a4c** and release at **40001b6e** execute successfully with supplied zero lock and current-thread state. The PC interpreter executed **39 unchanged stock instructions**, returned acquisition success, restored the stack and SR control bits, and took neither scheduler trap. This is useful evidence for an early allocation after startup clear, before scheduler creation. It does not establish the full allocation result, exception behavior, or actual device preconditions.

The next focused check should execute the full lazy allocator in that state, including bitmap/free-list mutations and the enlarged request. The already tested pool-initializer fixture supplies the allocator result and cannot substitute for this check.

## Execution and cache requirements

The official [NXP MCF5441x reference manual](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf), chapter 6, identifies selector 0004 as **ACR0**, a data-attribute register. Capstone's ITT0 label is inappropriate for this target interpretation. Stock startup writes CACR=A50CE100 and ACR0=4007E020. ACR0 covers 40000000..47ffffff for data accesses in copyback mode, including the configured heap. Instruction caching is enabled; its default mode is cacheable. These attributes support a RAM-code investigation, not proof of the complete inherited mapping. Other control state and hardware remain unverified.

Copyback data must reach memory before instruction fetch; instruction and branch state must then be synchronized before publication. The manual documents CPUSHL and invalidation controls. Cache-inhibited instruction fetch also has a fill-buffer coherency caveat when DNFB is set. Do not use data-cache invalidation alone: dirty data may be lost. Exact synchronization remains unimplemented.

## Initialization and lifetime contract to verify

1. Keep mod dispatch unavailable until the allocation, complete copy, relocation, validation, and cache synchronization finish. Resident bootstrap/dispatch instructions must themselves have a justified source and placement.
2. Reassemble or relocate every helper address against the actual allocation. Current fixture bodies contain absolute helper addresses; copying them unchanged to an arbitrary heap address would not work. Stock firmware calls retain their original destinations; internal PC-relative branches retain their offsets when each body is moved intact.
3. Publish one complete executable state only after synchronization. On null allocation, malformed source, relocation failure, or copy failure, no call may enter the RAM buffer. A stock fallback is usable only where displaced stock instructions and the original continuation are preserved.
4. Give the code the owner's verified lifetime. Do not free, clear, or overwrite it while any hook or saved return address can reach it. Ordinary pool resets must exclude it; reinitialization requires dispatch withdrawal and absence of outstanding executions. Reboot requires installation again.
5. Include initialization and failure paths in the enlarged-allocation audit. The old metadata header's ready bit currently describes metadata, not a newly installed executable image; its contract must be updated deliberately.

## Result

This investigation moves the space problem to a specific startup/source-lifetime problem. RAM capacity is not the immediate blocker. The next bounded target is **actual early lazy allocation followed by a source-preservation/copy/erase design**, while checking loader limits. Firmware and decoded-image hashes remain unchanged.

Evidence: `Digitone-RAM-code-route-audit.json` in this output directory. The custom PC interpreter does not simulate CPU cache, bus, DMA, hardware exceptions, or device timing.
