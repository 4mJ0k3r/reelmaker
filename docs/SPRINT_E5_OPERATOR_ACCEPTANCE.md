# E5 operator and film acceptance

## Production proof

The operator discovered `grounded_signal_story_30s` through `capabilities`, copied the registered example and changed its title to `The Last Transmission - Refined`. The accepted operator input accompanies the film. Validate, two identical plans, inspect, preflight, render and separate verify all succeeded. Only the documented CLI participated in production. The review used a fresh destination on the alternate local root from E1. A second render to the occupied destination returned `OUTPUT_EXISTS` and its MP4 SHA-256 stayed identical.

The final project is a single 30-second edit with ten 90-frame shots. The MP4 passed full H.264/yuv420p and AAC decode, exact 30 fps presentation timestamps, 720×1280 dimensions, 900 frames, faststart and zero flagged black frames. Registered 48 kHz stereo AAC had a gapless effective interval of 1,440,000 samples per channel. Audible drift was −2 samples relative to the approved mix, within the 1024-sample AAC tolerance. The four effects are the existing synthetic diagnostic sounds. Captions and narration are absent.

| Identity | SHA-256 |
| --- | --- |
| Original plan | `6d954670512bd6ce11de3b9f08507dddfef52e9b1820b579bf72bb77c0806d44` |
| Original MP4 | `eaaeff92563c90b205a3dec8ec5c525899c2224d68c603ca4a8e6c963690afd4` |
| Refined operator plan | `384bfb65a5aeca7a5ed97299fc259ec29a989e33ca28f33ef7f8f4bb5bcf81b2` |
| Refined MP4 | `30b826f42227483a563b5033f4bc7e5ae04463ea79d903cb8fad402eb95cb7bd` |

The refined render and in-job verification took 51.54 seconds on the review host. The sampled process-tree peaks were 107.47 MiB for rendering and 124.52 MiB for in-job final verification. The separate operator verification peaked at 99.25 MiB. Both monitored render phases had continuous OOM telemetry and passed resource admission. These are sampled peaks. The original archived run took 71.24 seconds with peaks of 103.32 and 125.17 MiB. Its workload and run conditions differed, so the comparison does not establish a renderer speedup.

## Visual assessment

This self-assessment uses decoded 720×1280 and 360×640 samples, shot boundaries, adjacent frames around lighting changes, and motion studies. The visual package includes ten matched shot pairs and three side-by-side clips. Original is on the left in each clip. Independent artistic approval remains pending.

| Category | Original independent / 5 | Refined self / 5 | Observation |
| --- | ---: | ---: | --- |
| Story clarity | 3 | 4 | Showing loss and response in the same frame makes the central event readable without captions. The mechanics of the signal are still implicit. |
| Motion and grounding | 3 | 3 | Mira begins moving earlier and the planted stance holds through the reactions. The arrival has a short, stylized stride. |
| Acting | 3 | 4 | Mira recoils first and Bram responds later. The ending holds their separate recovery. Facial changes remain limited. |
| Geography | 3 | 3 | A rightward approach and repeated beacon silhouette connect the outpost and ravine. The cut still omits physical travel between locations. |
| Lighting and atmosphere | 4 | 4 | The practical is readable at each switch. The nearby window remains visible during the blackout, making the loss local. |
| Camera composition | — | 4 | The shared framing preserves both figures and the lamp. One opening wide keeps Bram deliberately small. |
| Cut continuity | 3 | 4 | The lamp state and actors' position carry across the preparation cut, with the blackout occurring inside the following shot. |
| Pacing | 3 | 4 | The on, off and answering beats land at frames 308, 475 and 781. Acting changes inside the fixed shot grid. |
| Mobile readability | 4 | 4 | The scarf, hat, dark lamp and warm glow distinguish subjects at 360×640. |
| Overall polish | 3 | 3 | The causal sequence is cleaner. Pose vocabulary and the abrupt change of location still read as cutout animation. |

The strongest comparisons are the original cut at 449–450 against the new in-shot blackout at 474–475, and the original single-actor ending against the shared refined payoff at 814–834. At refined frame 491 Mira is visibly recoiling while Bram remains planted in his prior expression. At frame 506 Bram's reaction is active. Frame 814 shows Mira settled as Bram is still reacting. Ground-reference samples show zero horizontal root movement and less than `3e-14` logical units of foot displacement in the stationary blackout and answer intervals.

Six original manifests retained exactly the same plan and sampled Cairo frame digests against the approved baseline. The focused acting and direction selection and the documented operator selection passed before the full regression gate. See the E6 qualification for final test counts.
