# Intervening application startup: allocation preservation

The early allocation and its owner pointer survive the executed application startup prefix, first startup-thread setup, and **all 119 actual constructor callbacks** in the PC model. Constructor traversal executes 412,495 instructions and enters the real stock allocator 999 times. The complete proposed `15c80`-byte allocation remains byte-for-byte unchanged throughout these tested portions, including metadata and copied code. No allocator-return or constructor immediate-return substitutions are used for this traversal.

This is stronger evidence for preservation, but **the full path from cache handoff to the initializer remains incomplete**. The second thread's hardware setup before the constructor table and its later hardware/application setup are separate attempts. They reach real hardware polling loops and do not reach their target boundaries with the zero-response hardware fixture. No modified or flashable firmware was generated; the original SysEx and decoded main hashes remain unchanged.

21 checks pass in five execution cases:

| Executed portion | Result |
|---|---|
| Application entry `4012b344` to first trap at `4012b3be` | 132 instructions; owner/allocation and allocator control, heads and bitmap unchanged |
| First saved startup-thread entry `4008c4f6` to its spin at `4008c524` | 52 instructions; creates the second thread and preserves owner/allocation and allocator metadata |
| Counted callback dispatcher `4008c7d4` to `4008c7f4` | All 119 callback entries execute in table order, with their bodies and callees; owner/allocation unchanged |
| Post-table startup toward initializer | Stops after 50,000 instructions in the UART readiness wait; owner/allocation unchanged over the executed portion |
| Second-thread hardware setup toward callback table | Stops after 50,000 instructions in the SPI receive wait; owner/allocation unchanged over the executed portion |

The application entry's clear at `429a3968..429a39a8` affects scheduler queues. The allocator's 21 free-head words occupy `429a38c0..429a3914`, so that clear does not overlap them. The application prefix creates the startup thread using actual stock thread-creation and queue-linking instructions. Its saved entry is `4008c4f6`, with saved frame pointer `4132758c`. That first thread creates a second saved entry at `4008c634`, frame pointer `4132b5e0`.

Thread entries are supplied at these recovered scheduling boundaries. The physical trap/RTE context-switch machinery and asynchronous interrupts are not executed. This prevents treating these runs as a continuous device startup. Hardware register reads/writes use a PC dictionary; writes to loaded main-image globals remain in the emulated RAM only.

The constructor execution preserves the allocator's initialized flag and its control pointers/parameters. Normal constructor allocations change free lists and bitmap contents; they are not expected to remain identical after those allocations. The early owner's complete bytes remain identical. The only exact literal references to the stock owner pointer `4199d590` in the unchanged main image occur in the stock initializer at `400f0574`, `400f058e`, and `400f05a0`. This is supporting evidence, not exclusion of computed pointers or bulk writes.

The two remaining observed waits are identified from unchanged instruction bytes:

* Before the table: `400ecee6..400ecef4` reads SPI status at `fc05c02c`, shifts right four, masks to four bits, and repeats while zero. The fixture provides no received FIFO data/status.
* After the table: `4009f34a..4009f358` reads UART status at `ec070004` and repeats until bit 2 indicates transmit readiness. The fixture provides no readiness response.

Neither wait itself writes the owner or allocation. However, later execution after those waits, complete device-dependent branches, and asynchronous effects have not been certified. These model stops are not evidence that the actual Digitone hangs or that its firmware destroys the proposed context.

Next: recover the SPI/UART transaction and completion requirements, model explicit responses for success and failure paths, and resume these hardware-dependent portions while monitoring owner, allocation and allocator control. Then connect that resumed startup to the already tested full initializer. Physical cache coherence and global executable-interval ownership remain separate open audits.

Machine-readable cases and check names are in `Digitone-intervening-startup-results.json`. Execution uses the project's custom interpreter and the earlier startup-overlay fixtures; long BSS-clear loops retain their previously validated summaries.
