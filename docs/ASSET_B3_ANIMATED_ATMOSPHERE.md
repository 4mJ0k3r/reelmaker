# Animated atmosphere

See the [engineering report](../ReelMaker_Living_Worlds_Sprint_B_Engineering_Report.md) for tested scope, evidence and constraints.

`rain_field_01`: light, steady, heavy. Rain uses bounded screen-space
streaks at three authored depth rates.

`wind_leaves_01`: gentle, gust, autumn. Leaves advance along persistent
trajectories with periodic vertical drift.

`smoke_wisp_01`: thin, rising, windblown. Use a local emitter. Wisps fade
out before recycling and stay in the assigned painter layer.

See the rainy Village Lane and windy Woodland Creek examples. The closing
Creek Crossing shot includes rising smoke. Place effects clear of foreground
faces and adjust the scene composition to preserve contrast.
