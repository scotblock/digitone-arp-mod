import pathlib
text='''The PC software-DMA model now defers each source read and destination write until its scheduled beat boundary. It does not copy payload bytes at launch. Scatter/gather descriptor reads and completion publication follow that progression.

Controlled tests verify early destination reads, source mutation before/after a read beat, partial visibility, final completion, timed descriptor changes, modulo wrapping and unequal beat sizes. Native firmware-style polling and cache-maintenance integration fixtures pass.

The engine remains block-granular; beat timestamps are serviced at block, guest-memory and peripheral boundaries. The report must quantify service lateness. Initial TCD progress/address fields are published at completed descriptor boundaries, not per hardware beat. Cached byte values and real hardware arbitration are not modeled.

Live descriptors indicate self-links for the three observed channels, 30 to 30, 42 to 42 and 47 to 47. The walker continues their iterations, but explicit self-link channel arbitration/restart behavior remains outside the model. No cross-channel links have yet appeared in this tested workload.
'''
pathlib.Path('work/timestamped-DMA-report-notes.md').write_text(text)
print('Scope and limitations recorded for the final audit.')
