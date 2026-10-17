# E10 development decision — inherited power handling

17 October 2026. User agreement: continue E10 development using the existing stock power mechanism. Keep the unit closed and do not require oscilloscope measurements merely to continue the firmware work.

The unchanged stock shutdown writer, bank selector and existing board power design are inherited operating assumptions. Physical hold-up time and guaranteed abrupt-power-loss recovery are not certified. E10 adds no shutdown storage commands. The synthetic partial-write counterexample remains documented; it does not, by itself, require redesigning the stock protocol or halt all E10 development.

Earlier builds have user-reported physical operation. Those observations remain valid within their tested scope; the lack of a quantified hold-up specification does not negate them. E10 is still a separate PC prototype and is not newly hardware-ready merely because this assumption is accepted.

Continue with concrete E10 integration checks: custom settings update/interrupt handoff, then the packaged loader/startup/playback path and ordinary controls/saving regressions. New issues caused or exposed by the custom code should be reported and addressed on their own evidence. Do not expand into a general stock power-system redesign without a separate reason/request.

No firmware bytes, installed device or stock recovery route are changed by this decision. Do not claim protection against arbitrary mid-write power removal.
