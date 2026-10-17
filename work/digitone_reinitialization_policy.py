"""PC-only specification model. This is not a native firmware guard.

V1 supplies no live shutdown/owner-drain protocol, so no live pool rebuild is
admitted. A fresh boot supplies one non-replayable initialization permit.
"""
from dataclasses import dataclass
from enum import Enum

class Phase(Enum):
 COLD='cold'
 INITIALIZING='initializing'
 LIVE='live'
 FAILED='failed'

@dataclass(frozen=True)
class Decision:
 allowed:bool
 reason:str

class ProtectionViolation(RuntimeError):pass

class ReinitializationPolicy:
 """Caller admission precedes any stock mutation; initializer entry repeats it.

 owner counts are deliberately NOT used to grant warm reconstruction. An
 incomplete alias/owner inventory must not masquerade as quiescence proof.
 """
 def __init__(self):
  self.phase=Phase.COLD
  self._boot_permit=object()
  self._permit_consumed=False
  self._entered=False
  self.producer_admission=False
  self.context_ready=False
  self.initializations=0

 def producer(self):
  return Decision(self.phase is Phase.LIVE and self.producer_admission,'live admission' if self.phase is Phase.LIVE and self.producer_admission else 'boot/setup admission closed')

 def operation(self,name):
  # Recovered test-enter/test-exit/audio-test page paths are not supported V1
  # operations. Deny even before initialization or when no queue is visible.
  if name in {'diagnostic_enter','diagnostic_exit','audio_test_select','audio_test_remove','reinitialize','unknown_setup'}:
   return Decision(False,'V1 requires a fresh startup for note-storage reconstruction; reject whole operation before mutation')
  if name=='boot_setup':
   return Decision(self.phase is Phase.COLD and not self._permit_consumed,'single fresh-boot permit' if self.phase is Phase.COLD and not self._permit_consumed else 'boot permit already consumed or failed')
  if name in {'pattern_change','sustain_release','note_release','playback_stop'}:
   return Decision(self.phase is Phase.LIVE,'ordinary operation preserves pool lifetime')
  return Decision(False,'unknown operation has no admitted reconstruction contract')

 def begin_boot(self):
  if not self.operation('boot_setup').allowed:raise ProtectionViolation('No live, repeated or failed-state setup admission')
  self._permit_consumed=True
  self.phase=Phase.INITIALIZING
  return self._boot_permit

 def initializer_entry(self,permit):
  if self.phase is not Phase.INITIALIZING or permit is not self._boot_permit or self._entered or self.producer_admission or self.context_ready:
   raise ProtectionViolation('Pool entry rejected before first mutation')
  self._entered=True
  self.initializations+=1

 def finish_boot(self,*,stock_complete,context_complete,mode_is_normal):
  if self.phase is not Phase.INITIALIZING or not self._entered:raise ProtectionViolation('Completion without admitted initializer')
  if not stock_complete or not mode_is_normal:
   self.phase=Phase.FAILED
   self.producer_admission=False
   self.context_ready=False
   return
  # Valid stock continuation can run with feature context unavailable. A
  # context failure never returns the already consumed boot permit.
  self.phase=Phase.LIVE
  self.producer_admission=True
  self.context_ready=bool(context_complete)

 def run_operation(self,name,mutation):
  decision=self.operation(name)
  if decision.allowed:mutation()
  return decision
