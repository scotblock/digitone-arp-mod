# Queued pattern callbacks across rebind/reset — PC lifecycle audit

Eight controls pass. Firmware containers and existing overlay binaries remain unchanged. This audit extends the earlier direct-callback tests to the actual stock producer, queue publisher, worker, native conversion and descriptor cleanup.

## Queue ownership and retirement

The stock builder 4002f80c captures the raw source-owner and destination pointers. Publication through 400a87f0 installs a callable with manager 4002c1fe and invoke routine 4002c1d2. The worker 400a8690 copies that callable into a local handle before invoking it. The manager's clone operation allocates an eight-byte descriptor and copies both scalar pointers. It does not acquire ownership of the destination buffer or re-read the owner's current destination field.

This changes the retirement question: the pointer has multiple descriptor owners during dispatch. The observed sequence includes builder temporaries, the queue's descriptor, and the worker's selected clone. The selected clone performs the conversion, its manager is called with destruction operation 3, and that descriptor is freed. The queued descriptor is then destroyed and freed separately. Freeing one descriptor is not proof that every retained copy has retired.

The worker checks whether the selected callable exists. On the exercised path, it does not validate the old destination against owner +20 before conversion, and there is no observed generation/cancellation check that rejects these controls.

## Three queue controls

Baseline, clear-after-publication, and change-after-publication all reach the actual worker and cleanup. The latter two deliberately mutate only the owner field using a PC fixture after stock queue publication and before consumption; they are not evidence that a normal application dispatcher schedules that mutation there.

In the clear case the owner's field is zero at consumption. In the change case it is 407f29f4. In both, the selected clone retains 407ef9f4, and the actual conversion writes through that old destination. Both the selected clone and queue copy are later retired. The proposed custom queue remains unchanged.

The first shortened probe did not reach the target builder. After extending the panel workload, the initial observer could not associate the selected clone with the published descriptor: it is a distinct allocation. Those incomplete reports are retained separately. The final observer follows the native clone path and removes freed addresses from its active set, rather than treating later address reuse as repeated destruction of the same allocation.

## Full native parent rebind

A separate transient PC guest stub calls the complete stock parent binder 40028354 after publication. It supplies parent 41a720a0 and an existing alternate project backing at 407fd3f8. The binder returns with the parent base changed and the child destination field at 40a96df8. It updates the dependent views as part of its normal body.

The pending callback still consumes its selected descriptor's original destination 407ef9f4, performs conversion there, and retires normally. Thus the extra work in this recovered parent-binding routine does not cancel the already-published callback. This is an injected native rebind, not a recovered normal application transition or a claim that all alternate backings are valid on physical hardware.

The earlier lifetime audit accounts for the original destination as part of the fixed-address stock project buffer. Rebinding this view does not itself free that buffer. Different dynamically supplied backing or destruction of the raw source-owner object needs its own lifetime proof.

## Four guarded reset controls

Four temporary PC guest call stubs request warm setup 4009d0d8, pool wrapper 4009c5a0, initializer 400ffed0 and diagnostic exit 4009d0ea at the same publication boundary. They execute the existing unchanged PC refusal guards with admission LIVE.

All four return before the monitored stock reset body. Owner/context/custom-queue and selected stock pool/flag fingerprints remain unchanged; the guards preserve the checked registers and status. After refusal, the pending callback executes and its selected clone and queue copy are retired. These guards avoid mutation; they do not cancel pending work.

The refusal behavior belongs to the existing modified PC overlay, not a newly established stock protection mechanism. The monitored fingerprint is not a watch of every possible RAM write. Each guest stub is temporary RAM code, its instruction stream is checked for the target ISA, and displaced publisher instructions are replayed. No firmware or existing guard binary was rebuilt.

## Result and remaining boundary

Field clearing, conditional replacement and the recovered full parent binder are not callback-cancellation barriers. An operation that actually invalidates the backing or source owner must ensure all queued and selected copies have retired, or make their execution safely reject the old lifetime. The tested permanent-address backing does not become dangling merely because this field changes.

The four recovered LIVE reset requests are covered by refusal before mutation in these PC controls. All outer/computed callers, actual parent destruction, other buffer-backed rebindings, reset exception cleanup and full DDR-reinitialization producer shutdown are not certified. Actual application scheduling of these injected overlaps is still unproven. Physical DMA, cache behavior, timing and exclusive ownership of the custom RAM remain unresolved. These results do not authorize or establish hardware readiness.

Evidence: Digitone-E04-PC-queued-pattern-retirement-summary.json; Digitone-E04-PC-queued-pattern-retirement-controls.json; Digitone-E04-PC-queued-pattern-reset-refusal-controls.json; Digitone-E04-PC-queued-pattern-native-parent-rebind.json. Firmware and resident-overlay hashes were verified unchanged.
