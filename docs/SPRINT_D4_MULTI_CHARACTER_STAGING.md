# Two-character staging

Use `cinematic-project-0.2` to place Scout and Mechanic on the same registered
ground layer. Each actor has its own identity, action, expression, facing,
anchor and optional action delay. Each shot may select a lead or partner,
and `two_shot` fits the pair on the same artboard. The existing renderer
samples the beat and actor clocks before projecting the camera.

A paired beat reserves disjoint swept lanes and accepts registered idle,
locomotion, reaction and transition actions. It accepts at most four shots.
Two-actor prop manipulation and arbitrary choreography are outside this
contract. A signal cue can turn the lamp on and pivot stationary actors to
the right at a specified beat frame. Moving left-facing actors cannot pivot.

The caption-free `unexpected_meeting.json` proves a delayed reaction across
the first cut, the environmental cue, and the final shared composition.
