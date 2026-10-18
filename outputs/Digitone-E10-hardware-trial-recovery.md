# E10 stock recovery

Use the untouched official original Digitone / Digitone Keys OS 1.44 file:
`Digitone_and_Digitone_Keys_OS1.44_STOCK.syx`.

Required SHA-256:
`d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`.

The verified local copy is in `outputs/stock-recovery/` in this workspace. The
shareable patch ZIP does not include stock firmware or project backups.

If E10 fails after the update has completed, use the previously rehearsed route:
Rubix22 MIDI OUT to Digitone MIDI IN; hold FUNC at power-on; TRIG 4 OS UPGRADE;
Elektron Transfer SYSEX TRANSFER / OS Upgrade via device startup menu; select
**the official stock file**, then follow all prompts through completion.
Use physical MIDI for this route. Do not interrupt active erase/programming.
If an update reports a failure, preserve its exact message/stage; do not invent
a timeout-based power-cycle procedure. If the startup menu is unavailable or
stock recovery fails, stop and seek Elektron support/service.

EMPTY RESET, FACTORY RESET and FORMAT +DRIVE are not OS rollback. Avoid them.
Stock recovery does not guarantee preservation of custom E10 settings; keep the
external backup separate and do not use important projects for the trial.

[Official startup-update guidance](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer)
