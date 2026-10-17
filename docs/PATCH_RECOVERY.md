# Device trial and recovery notes

Creating a firmware file does not install it. The patcher never contacts USB, MIDI or the instrument. Start with a separate Digiemu entry and keep stock firmware available.

These are experimental modifications for the **original Digitone and Digitone Keys only**, not Digitone II. E08F has a user-reported successful hardware trial but a subsequently confirmed sequencer arp bug; E09 and the E09A sequence correction are PC-only previews. Physical cache/timing, complete RAM ownership and all project/reset interactions are not certified. E04 previously stalled during hardware startup; reinstalling stock restored the instrument. That recovery does not guarantee recovery from every failure.

Before any separate hardware trial, back up projects/sounds, retain the official stock 1.44 file and follow the official device manual/update instructions. This package is not a complete hardware installation guide or a claim of hardware readiness. The earlier project used a rehearsed startup-menu MIDI recovery route; the ordinary USB update path was not fully certified for the modification.

If a modified build stalls at startup, stop testing that build. Consult Elektron's documented startup-menu OS-upgrade procedure and restore official stock firmware using a supported transfer connection. Do not select factory reset or erase options as a substitute for restoring the OS. Preserve notes on the failed build and checksum for investigation.

Official documentation and recovery procedures should be obtained from Elektron for your exact model. No stock image, backups or recovery utility is included here.
