import pathlib
p=pathlib.Path('work/shared_dma_arbiter.py');s=p.read_text().replace('self.owner=None;self.pending={};','self.batching_audio=False;self.owner=None;self.pending={};').replace('  if self.owner is not None:return','  if self.owner is not None or self.batching_audio:return')
s=s.replace('   self.ssi._run_minors=minors','''   self.ssi._run_minors=minors
   original_service=self.ssi.service
   def service(done):
    self.batching_audio=True
    try:original_service(done)
    finally:self.batching_audio=False
    self.dispatch(self.clock.cycles)
   self.ssi.service=service''')
s=s.replace("self.arbitration['audio_requests_coalesced']", "self.arbitration['audio_requests_dropped_while_pending']")
s=s.replace('             # Preserve the baseline\'s explicit unsupported-link accounting.\n             channel.links_ignored+=1\n             self.payload_counts[\'unsupported_minor_link_descriptors\']+=1', "             self.payload_counts['self_link_descriptors']+=1")
p.write_text(s)
