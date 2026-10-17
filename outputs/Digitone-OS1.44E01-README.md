**Superseded for Digiemu use by the E02 file, which fixes missing panel-light initialization.**

# Digitone scale-locked arp: Digiemu test build 1.44E01

Load `Digitone_OS1.44E01_SCALE_ARP_DIGIEMU_ONLY.syx` through Digiemu's add/import firmware flow. An untested Digitone release notice is expected because this image has its own version and hash. Use a separate firmware folder and let first boot finish.

The image contains the seven tested OS 1.44 context/pitch/copy hooks, a startup copier, and the reset helper. Code and the scale lookup table copy to reserved RAM before stock startup clearing. The private header starts not ready; the actual initializer/reset helper clears context and marks it ready. No manual post-boot code/header overlay is required.

Eligible arp results are constrained to the nearest note in their captured source track's root/scale. There is no new menu or enable switch. Stock cancellation decisions remain in force. Select a nonchromatic scale to hear a pitch constraint.

Verified locally: fresh Digiemu first boot, helper/table preservation, ready header, all seven installed hook sites, playback without a halt, and five actual scale outputs matching the oracle under root61/raw0: 57 to 56, 69 to 68, 81 to 80, 57 to 56, 69 to 68. The root/scale settings are explicit PC fixtures before pattern selection; event eligibility and metadata are not injected.

The original uploaded firmware is unchanged. Only the main OS section changes; all other section payloads remain byte-identical to stock. All-literal compression makes the image larger than stock.

**Emulator only: do not flash this image to a physical Digitone.** Hardware update acceptance, flash capacity for this representation, cache coherence, timing, full RAM ownership and every reset/transition path remain unverified. Ordinary audio can differ from stock due to the observed PC scheduling difference in parameter-packet age.

Build provenance and validation are recorded in `Digitone-OS1.44E01-build.json`, `Digitone-OS1.44E01-cold-start-validation.json`, and `Digitone-OS1.44E01-emulator-validation.json`. The fresh test uses an isolated device overlay for this image's hash and normal Digiemu extraction/startup. It does not inject the startup code or header.
