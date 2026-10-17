> Final-image review: E02’s literal-packed container exceeds the recovered stock flash interval and must remain PC-only. Startup header failures also enter an interrupt-masked infinite loop. See [the startup, memory and failure review](Digitone-OS1.44E02-startup-memory-failure-review.md).

# E02: Digiemu panel-light compatibility fix

Import `Digitone_OS1.44E02_SCALE_ARP_DIGIEMU_ONLY.syx` as a separate firmware in Digiemu. An untested firmware notice is expected. Let its first boot finish. The OS display/version field reads **1.44**, while the file name and build manifest identify this experimental build as **E02**.

E01's `1.44E01` version label prevented Digiemu from initializing its panel-light state from the existing OS1.44 RAM shadows. Its RECORD and step buttons still changed firmware state, but their lights did not reflect it. E02 restores the version label that Digiemu uses for this initialization. Its main executable, startup copier, reset helper and arp hooks are byte-identical to E01; only the container version field and associated transport/content checksum bytes change.

To enter a simple sequence: select T1, click RECORD, click steps 1, 5, 9 and 13, then click PLAY. RECORD should turn red in grid recording. Click RECORD again to leave that mode. To test scale locking, use a nonchromatic scale and enable the arp.

**Digiemu only. Do not flash this file to the physical Digitone.** Hardware timing, cache coherence, flash/update acceptance, complete RAM ownership and all reset paths remain unverified. The previously observed ordinary-audio scheduling difference is not fixed by E02.

The recording diagnosis compares stock, E01, E01 with the seven arp hooks restored to stock in RAM, and stock with those hooks installed in RAM. All enter/exit RECORD and edit the same step identically. The GUI LED decoder confirms E01 does not display RECORD's red state despite the firmware's red LED shadow. E02 uses the normal stock LED seed. Fresh-start, playback, nonchromatic scale-output and recording results are recorded separately in the validation JSON files.
