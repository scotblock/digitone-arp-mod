"""PC-only occupancy and serialized-resource sensitivity model, not silicon emulation."""
import collections
import struct


class Cache:
    def __init__(self):
        self.rows = [[None] * 4 for _ in range(128)]
        self.next = [0] * 128
        self.dirty = set()

    def access(self, address, write=False, allocate=True, locked=False):
        line = address // 16
        index = line % 128
        row = self.rows[index]
        if line in row:
            if write:
                self.dirty.add(line)
            return False, False
        if not allocate:
            return True, False
        ways = (2, 3) if locked else (0, 1, 2, 3)
        slot = next((w for w in ways if row[w] is None), None)
        if slot is None:
            slot = self.next[index]
            if slot not in ways:
                slot = ways[0]
        old = row[slot]
        dirty = old in self.dirty
        self.dirty.discard(old)
        row[slot] = line
        self.next[index] = ways[(ways.index(slot) + 1) % len(ways)]
        if write:
            self.dirty.add(line)
        return True, dirty

    def clear(self):
        lost = len(self.dirty)
        self.__init__()
        return lost

    def selected(self, address, physical):
        if physical:
            line = address // 16
            index = line % 128
            return [(index, w) for w, tag in enumerate(self.rows[index]) if tag == line]
        return [((address >> 4) & 127, address & 3)]

    def maintain(self, address, physical, invalidate, push):
        writes = 0
        for index, way in self.selected(address, physical):
            tag = self.rows[index][way]
            if push and tag in self.dirty:
                self.dirty.remove(tag)
                writes += 1
            if invalidate:
                self.dirty.discard(tag)
                self.rows[index][way] = None
        return writes


class SerialBus:
    def __init__(self):
        self.free = 0
        self.counts = collections.Counter()

    def reserve(self, now, cost, kind):
        start = max(now, self.free)
        self.free = start + cost
        self.counts[kind + '_cycles'] += cost
        self.counts[kind + '_requests'] += 1
        return self.free


class MemoryTiming:
    def __init__(self, session, fill=20, writeback=16, beat=4, contention=True):
        from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_HOOK_CODE
        from unicorn.m68k_const import UC_M68K_REG_A0, UC_M68K_REG_D0
        self.session = session
        self.clock = session.clock
        self.m = session.m
        self.fill, self.writeback, self.beat = fill, writeback, beat
        self.contention = contention
        self.i, self.d, self.bus = Cache(), Cache(), SerialBus()
        self.regs = dict(self.m.ctlregs)
        # Hardware clears the completed global-invalidate requests.
        self.regs[2] = self.regs.get(2, 0) & ~0x01040100
        self.counts = collections.Counter()
        self.maintenance = collections.Counter()
        self.samples = []
        self.channels = collections.Counter()
        self.dma_ready = {}
        self.hazards = collections.Counter()
        self.hooks = []
        self.registered_controls = set()
        self.initial_regs = {hex(k): hex(v) for k, v in self.regs.items()}

        class InstructionProxy:
            def touch(proxy, address, size):
                before, left = self.clock.cycles, self.clock.left
                self.fetch(address, size)
                cost = self.clock.cycles - before
                self.clock.cycles, self.clock.left = before, left
                return cost
        self.clock.icache = InstructionProxy()
        # CycleClock adds proxy return * penalty to its block budget.
        self.clock.miss_penalty = 1
        # The proxy provides count fields expected by CycleClock.report.
        self.clock.icache.hits = self.clock.icache.misses = 0

        def memory(uc, access, address, size, value, data):
            self.data(address, size, access == 17)
        self.hooks.append(self.m.uc.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE,
                                           memory, begin=0x40000000, end=0x7fffffff))
        previous = self.clock.on_new_block
        def register_control(address):
            if address in self.registered_controls:
                return
            self.registered_controls.add(address)
            def control(uc, at, size, data, address=address):
                word = int.from_bytes(uc.mem_read(address, 2), 'big')
                if word in (0x4e7a, 0x4e7b):
                    if word == 0x4e7b:
                        ext = int.from_bytes(uc.mem_read(address + 2, 2), 'big')
                        value = uc.reg_read(UC_M68K_REG_D0 + ((ext >> 12) & 7))
                        self.control_write(ext & 0xfff, value, address)
                elif word & 0xff38 == 0xf428:
                    target = uc.reg_read(UC_M68K_REG_A0 + (word & 7))
                    self.push((word >> 6) & 3, target, address)
            self.hooks.append(self.m.uc.hook_add(UC_HOOK_CODE, control,
                                                begin=address, end=address))
        self.register_control = register_control
        # Hooks added inside a translated-block callback may miss the first
        # execution of that block. Register stock sites before translation.
        if hasattr(session, 'main_img'):
            self.prescan(session.main_img, 0x40000400)
        def decoded(block, instructions):
            if previous:
                previous(block, instructions)
            for address, instruction in instructions:
                if instruction.op not in ('cpushl', 'intouch', 'movec'):
                    continue
                if address not in self.registered_controls:
                    self.counts['dynamic_control_first_execution_uncovered'] += 1
                    register_control(address)
        self.clock.on_new_block = decoded
        self.install_dma()

    def prescan(self, image, base):
        for offset in range(0, len(image) - 1, 2):
            word = int.from_bytes(image[offset:offset + 2], 'big')
            if word in (0x4e7a, 0x4e7b) or word & 0xff38 == 0xf428:
                self.register_control(base + offset)

    def charge(self, amount, kind):
        if amount <= 0:
            return
        self.counts[kind + '_stall_cycles'] += amount
        self.clock.cycles += amount
        if self.clock.left is not None:
            self.clock.left -= amount

    def cpu_bus(self, cost, kind):
        now = self.clock.cycles
        if self.contention:
            done = self.bus.reserve(now, cost, kind)
            self.counts['bus_wait_cycles'] += done - now - cost
        else:
            done = now + cost
        self.charge(done - now, kind)

    def policy(self, address, instruction=False):
        cacr = self.regs.get(2, 0)
        enabled = bool(cacr & (0x8000 if instruction else 0x80000000))
        mode = (1 if cacr & 0x400 else 0) if instruction else (cacr >> 25) & 3
        for rc in ((6, 7, 14, 15) if instruction else (4, 5, 12, 13)):
            value = self.regs.get(rc, 0)
            if not value & 0x8000:
                continue
            sm = (value >> 13) & 3
            if sm < 2:
                from unicorn.m68k_const import UC_M68K_REG_SR
                supervisor = bool(self.m.uc.reg_read(UC_M68K_REG_SR) & 0x2000)
                if (sm == 0 and supervisor) or (sm == 1 and not supervisor):
                    continue
            if value & 0x400:
                match = address >> 24 == value >> 24 and not (((address >> 20) ^ (value >> 20)) & (~(value >> 16) & 15))
            else:
                match = not (((address >> 24) ^ (value >> 24)) & (~(value >> 16) & 255))
            if match:
                mode = (value >> 5) & 3
                if instruction:
                    mode = int(mode >= 2)
                break
        return enabled and (mode == 0 if instruction else mode < 2), mode

    def fetch(self, address, size):
        if not 0x40000000 <= address < 0x80000000:
            return
        cached, _ = self.policy(address, True)
        if not cached:
            self.cpu_bus(((size + 3) // 4) * self.beat, 'uncached_instruction')
            return
        for line in range(address // 16, (address + size - 1) // 16 + 1):
            miss, _ = self.i.access(line * 16, locked=bool(self.regs[2] & 0x800))
            if miss:
                self.clock.icache.misses += 1
                self.cpu_bus(self.fill, 'instruction_fill')
            else:
                self.clock.icache.hits += 1

    def data(self, address, size, write):
        cached, mode = self.policy(address)
        if not cached:
            self.cpu_bus(((size + 3) // 4) * self.beat, 'uncached_data')
            return
        copyback = mode == 1
        for line in range(address // 16, (address + size - 1) // 16 + 1):
            miss, dirty = self.d.access(line * 16, write and copyback,
                                        allocate=not write or copyback,
                                        locked=bool(self.regs[2] & 0x08000000))
            if dirty:
                self.cpu_bus(self.writeback, 'dirty_eviction')
            if miss and (not write or copyback):
                self.cpu_bus(self.fill, 'data_fill')
            if write and not copyback:
                self.cpu_bus(((size + 3) // 4) * self.beat, 'write_through')

    def control_write(self, rc, value, pc):
        self.maintenance[f'movec_{rc:x}'] += 1
        if rc == 2:
            if value & 0x01000000:
                self.counts['dirty_lines_discarded_by_DCINVA'] += self.d.clear()
            if value & 0x100:
                self.i.clear()
            # Branch-cache invalidation is already outside this occupancy model.
            value &= ~0x01040100
        self.regs[rc] = value
        if len(self.samples) < 30:
            self.samples.append(dict(pc=hex(pc),control=hex(rc),value=hex(value)))

    def push(self, which, address, pc):
        cacr = self.regs[2]
        self.maintenance[f'cpush_{which}'] += 1
        if which == 0:
            self.fetch(address, 1)
            return
        physical, invalidate_only = bool(cacr & 0x4000), bool(cacr & 0x100000)
        if which & 1:
            writes = self.d.maintain(address, physical,
                                    invalidate_only or not cacr & 0x10000000,
                                    not invalidate_only)
            for _ in range(writes):
                self.cpu_bus(self.writeback, 'cache_push')
        if which & 2:
            self.i.maintain(address, physical,
                           invalidate_only or not cacr & 0x1000, False)
        if len(self.samples) < 30:
            self.samples.append(dict(pc=hex(pc),cache=which,address=hex(address),physical=physical))

    def dma_span(self, address, size, write=False):
        if not 0x40000000 <= address < 0x80000000:
            return 0
        # DDR aliases reach the same RAM, although their cache tags differ.
        lo = 0x40000000 + (address - 0x40000000) % 0x08000000
        for line in range(lo // 16, (lo + size - 1) // 16 + 1):
            present = line in self.d.rows[line % 128] if write else line in self.d.dirty
            if present:
                self.hazards['DMA_write_resident_lines' if write else 'DMA_read_dirty_lines'] += 1
        return ((size + 3) // 4) * self.beat

    def install_dma(self):
        from emu import edma_sw
        bank = self.session.ev['edma_sw_bank']
        assert bank._native is None, 'Must install the Python DMA bank before construction'
        for channel in bank.channels.values():
            original_run, original_apply = channel._run, channel._apply
            def run(tcd, ensure=True, channel=channel, original=original_run):
                src, attr, soff, nbytes, _, dst, citer, doff, *_ = tcd
                count = edma_sw.iteration_count(citer)
                ssize, dsize = 1 << ((attr >> 8) & 7), 1 << (attr & 7)
                smod, dmod = attr >> 11, (attr >> 3) & 31
                total = count * nbytes
                cost = 0
                # Walk actual transfer endpoints, including modulo wrapping.
                for size, address, off, mod, write in ((ssize, src, soff, smod, False),(dsize, dst, doff, dmod, True)):
                    if off == size and not mod:
                        cost += self.dma_span(address, total, write)
                    else:
                        for _ in range(total // size):
                            cost += self.dma_span(address, size, write)
                            address = edma_sw.modulo_add(address, off, mod)
                result = original(tcd, ensure)
                now = self.clock.cycles
                ready = self.bus.reserve(now, cost, 'DMA_DDR') if self.contention else now
                self.dma_ready[channel.channel] = ready
                self.channels[channel.channel] += total
                return result
            def apply(channel=channel, original=original_apply):
                if channel._pending is not None and self.clock.cycles < self.dma_ready.get(channel.channel, 0):
                    self.counts['DMA_completion_polls_deferred'] += 1
                    # The instant-copy baseline leaves the previous DONE bit set
                    # on SSRT. A delayed transfer must hide it while ACTIVE.
                    csr = channel._u16(edma_sw.CSR)
                    channel._w16(edma_sw.CSR, (csr & ~edma_sw.CSR_DONE) | edma_sw.CSR_ACTIVE)
                    return False
                return original()
            channel._run, channel._apply = run, apply

    def report(self):
        return dict(costs=dict(fill=self.fill,writeback=self.writeback,beat=self.beat,
                               serialized_contention=self.contention),
                    counts=dict(self.counts),bus=dict(self.bus.counts),
                    maintenance=dict(self.maintenance),samples=self.samples,
                    DMA_channel_bytes={str(k):v for k,v in self.channels.items()},
                    coherence_observations=dict(self.hazards),initial_controls=self.initial_regs,
                    final_controls={hex(k):hex(v) for k,v in self.regs.items()})
