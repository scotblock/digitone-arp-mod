"""DMA payload visibility at scheduled beat boundaries in the PC cycle model."""
import collections
import heapq
import struct
from shared_memory_timing import MemoryTiming


class TimestampedMemory(MemoryTiming):
    supports_restart_latching = False
    def install_dma(self):
        from emu import edma_sw as e
        self.events = []
        self.sequence = 0
        self.active = {}
        self.payload_counts = collections.Counter()
        self.payload_samples = []
        self.restart_samples = []
        self.servicing = False
        bank = self.session.ev['edma_sw_bank']
        assert bank._native is None
        for channel in bank.channels.values():
            original_apply = channel._apply
            def transfer(uc, ensure=True, channel=channel):
                self.service_payload()
                if channel.channel in self.active:
                    if not self.supports_restart_latching:
                        raise RuntimeError('Overlapping requests require the shared DMA arbiter')
                    from unicorn.m68k_const import UC_M68K_REG_PC
                    state=self.active[channel.channel]
                    # SSRT sets one START bit; it neither rewinds the active
                    # minor nor queues an unbounded number of transfers.
                    state['restart_latched']=True
                    channel._w16(e.CSR,channel._u16(e.CSR)|e.CSR_START)
                    self.payload_counts['software_requests_while_inflight']+=1
                    if len(self.restart_samples)<32:
                        frame=state['generator'].gi_frame
                        loc=frame.f_locals if frame else {}
                        self.restart_samples.append(dict(channel=channel.channel,pc=hex(uc.reg_read(UC_M68K_REG_PC)),cycles=self.clock.cycles,owner=getattr(self,'owner',None),descriptor=bytes(uc.mem_read(channel.tcd,32)).hex(),progress={k:loc.get(k) for k in ('minor','count','src','dst','tcd')}))
                    return
                descriptor = list(struct.unpack(e.TCD_FMT, bytes(uc.mem_read(channel.tcd, 32))))
                if ensure:
                    channel._ensure_span(descriptor[0],descriptor[2],e.iteration_count(descriptor[6]),descriptor[3],descriptor[1] >> 11)
                    channel._ensure_span(descriptor[5],descriptor[7],e.iteration_count(descriptor[6]),descriptor[3],(descriptor[1] >> 3) & 31)
                state = {'channel':channel,'generator':self.walk(channel,descriptor),
                         'buffer':bytearray(),'moved':0,'seen':set(),'start':self.clock.cycles}
                self.active[channel.channel] = state
                channel._pending = (descriptor[10] & ~(e.CSR_START | e.CSR_ACTIVE)) | e.CSR_DONE
                channel._w16(e.CSR,(descriptor[10] & ~e.CSR_DONE) | e.CSR_ACTIVE)
                self.advance(state,self.clock.cycles)
            def apply(channel=channel, original=original_apply):
                self.service_payload()
                if channel.channel in self.active:
                    self.counts['DMA_completion_polls_deferred'] += 1
                    channel._w16(e.CSR,(channel._u16(e.CSR)&~e.CSR_DONE)|e.CSR_ACTIVE)
                    return False
                return original()
            channel._transfer,channel._apply = transfer,apply
        # At run-loop boundaries, service payload before SSI/external peers.
        self.session.sources = (self,) + self.session.sources
        from unicorn import UC_HOOK_BLOCK,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
        self.hooks.append(self.m.uc.hook_add(UC_HOOK_BLOCK,lambda *args:self.service_payload()))
        # SRAM and MMIO accesses also need the preceding DMA payload visible.
        self.hooks.append(self.m.uc.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,
                                           lambda *args:self.service_payload(),
                                           begin=0x80000000,end=0xffffffff))

    def data(self,address,size,write):
        self.service_payload()
        super().data(address,size,write)
        self.service_payload()

    def cpu_bus(self,cost,kind):
        self.service_payload()
        super().cpu_bus(cost,kind)
        self.service_payload()

    def walk(self,channel,tcd):
        from emu import edma_sw as e
        seen=set()
        for depth in range(e.MAX_LINKS):
            src,attr,soff,nbytes,slast,dst,citer_raw,doff,dlast,biter,csr=tcd
            count=e.iteration_count(citer_raw)
            ss,ds=1<<((attr>>8)&7),1<<(attr&7)
            smod,dmod=attr>>11,(attr>>3)&31
            if not count or not nbytes or nbytes%ss or nbytes%ds or count*nbytes>e.MAX_BYTES:
                raise RuntimeError('Unsupported or invalid timestamped DMA descriptor')
            if e.link_channel(citer_raw) is not None:
                # Preserve the baseline's explicit unsupported-link accounting.
                channel.links_ignored+=1
                self.payload_counts['unsupported_minor_link_descriptors']+=1
                self.payload_counts[f'minor_link_{channel.channel}_to_{e.link_channel(citer_raw)}']+=1
            for minor in range(count):
                buffer=bytearray()
                for beat in range(nbytes//ss):
                    value=yield ('read',src,ss,None)
                    buffer.extend(value)
                    src=e.modulo_add(src,soff,smod)
                for beat in range(nbytes//ds):
                    yield ('write',dst,ds,bytes(buffer[beat*ds:(beat+1)*ds]))
                    dst=e.modulo_add(dst,doff,dmod)
                self.payload_counts['minor_loops_completed']+=1
            total=count*nbytes
            channel.bytes_moved+=total
            self.channels[channel.channel]+=total
            src=(src+e._signed(slast,32))&0xffffffff
            final=list(tcd);final[0]=src;final[5]=dst;final[6]=biter
            if not csr&e.CSR_ESG:
                final[5]=(dst+e._signed(dlast,32))&0xffffffff
                # Publish final address/count fields only after final payload.
                self.m.uc.mem_write(channel.tcd,struct.pack(e.TCD_FMT,*final))
                channel._pending=(csr&~(e.CSR_START|e.CSR_ACTIVE))|e.CSR_DONE
                channel.transfers+=1
                return
            if dlast in seen or dlast%32:
                raise RuntimeError('Invalid timestamped scatter-gather chain')
            seen.add(dlast)
            descriptor=yield ('descriptor',dlast,32,None)
            tcd=list(struct.unpack(e.TCD_FMT,descriptor))
            self.m.uc.mem_write(channel.tcd,descriptor)
            channel.links_followed+=1
        raise RuntimeError('Timestamped scatter-gather chain exceeded bound')

    def advance(self,state,at,value=None):
        try:
            op=state['generator'].send(value)
        except StopIteration:
            ch=state['channel'].channel
            del self.active[ch]
            self.dma_ready[ch]=at
            self.payload_counts['major_transfers_completed']+=1
            state['channel']._apply()
            return
        kind,address,size,data=op
        # Every beat is visible only at its reservation's completion. DDR
        # endpoints use the common resource; other endpoints have a selected
        # nonzero beat cost but no claimed DDR contention.
        cost=((size+3)//4)*self.beat
        is_ddr=0x40000000<=address<0x80000000
        if self.contention and is_ddr:
            due=self.bus.reserve(at,cost,'DMA_DDR')
        else:
            due=at+cost
        self.sequence+=1
        heapq.heappush(self.events,(due,self.sequence,state,op))

    def service_payload(self):
        if self.servicing:
            return
        self.servicing=True
        try:
            while self.events and self.events[0][0]<=self.clock.cycles:
                due,sequence,state,op=heapq.heappop(self.events)
                kind,address,size,data=op
                # Observe cache aliases at actual modeled access, not launch.
                self.dma_span(address,size,kind=='write')
                if kind=='write':
                    self.m.uc.mem_write(address,data)
                    value=None
                else:
                    value=bytes(self.m.uc.mem_read(address,size))
                self.payload_counts[kind+'_beats']+=1
                self.payload_counts['service_lateness_cycles_max']=max(self.payload_counts['service_lateness_cycles_max'],self.clock.cycles-due)
                if len(self.payload_samples)<24:
                    self.payload_samples.append(dict(channel=state['channel'].channel,kind=kind,
                                                    address=hex(address),size=size,due=due,
                                                    observed=self.clock.cycles))
                self.advance(state,due,value)
        finally:
            self.servicing=False

    def step(self,done,remaining=None):
        # CycleClock is block-granular. Restarting Unicorn for every beat is
        # costly and cannot make that clock instruction-cycle-exact. Block
        # and memory hooks service preceding payload before guest accesses;
        # this source services preceding payload before peripheral peers.
        return None

    def service(self,done):
        self.service_payload()

    def report(self):
        result=super().report()
        result['timestamped_payload']=dict(counts=dict(self.payload_counts),samples=self.payload_samples,
                                          active_channels=sorted(self.active),queued_events=len(self.events),restart_samples=self.restart_samples)
        return result
