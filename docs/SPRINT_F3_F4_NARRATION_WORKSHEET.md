# Map a supplied narration take to the picture

Ask for the finished private WAV, the exact supplied script, the start and
end of each selected line, and any caption copy approved by the user.
Keep the original recording. Use a separate copy for PCM16 conversion if
needed. PCM16 mono or stereo at 16, 24, 44.1 or 48 kHz is admitted, up to
60 seconds and 11,585,536 bytes. Never guess timestamps from the script.
Record which marks are approximate and which were measured on the take.

For each authored interval fill in the columns in the example map below.
Use the take's source clock for script marks and the film clock for visual
and caption marks. Choose the nearest 30 fps frame for an authored picture
mark, document the rounding and review the adjacent frame. End frames are
exclusive. Shots stay on the 90-frame grid. Captions can use finer authored
intervals and must be sorted, non-overlapping, and at most two 32-character
ASCII lines each. Check reading duration and mobile layout.

| Source time in/out | Supplied script excerpt | Mark precision | Film time and frames | Beat and action | World and camera | Approved caption | Audio start frame |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fill from the private take | Copy approved words | Approximate or measured | Author both clocks | Select admitted values | Select admitted values | Copy approved text | Fill once per take |

Audio starts once. If a source line starts at source frame 120, the take
is trimmed from source frame 30, and the audio starts at film frame 15,
the line lands at film frame 105, or 3.500 s. Each film frame is exactly
1,600 samples in the 48 kHz mix. Mark start and intentional trim explicitly.
Use a null trim end to keep the recording's final sub-frame tail. Short
takes are padded with silence. The renderer rejects implicit truncation.
A 33–60 second project admits one registered narration and an empty cues
list. Preserve spoken pacing and gaps.

## Example project and timing map

The fully authored example is
`examples/sprint-f3-f4/the_light_in_the_empty_town_cinematic_refined.json`.
It uses a deterministic **synthetic timing signal** at film frame 0, with
no voice or user script. The captions below are the film's native text.
For a supplied take, add its approved script marks to a private copy of
the worksheet, then adjust the authored picture or caption timing as needed.

| Film time (s) | Film frames [start, end) | Visual beat | Actor action | World / mood | Camera | Native caption | Audio start |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00–03 | 0–90 | forest_road | walk_to_settle + walk_to_settle | forest_ravine / misty | establishing / hold | They took the forest road. | Frame 0 / 0.000 s |
| 03–06 | 90–180 | forest_road | walk_to_settle + walk_to_settle | forest_ravine / misty | two_shot / track | They took the forest road. | Continuous |
| 06–09 | 180–270 | mist_closes_in | idle_to_notice + notice_to_react | forest_ravine / misty | reaction / push_in | Mira refused to turn back. | Continuous |
| 09–12 | 270–360 | mist_closes_in | idle_to_notice + notice_to_react | forest_ravine / misty | reaction / reframe / partner | Bram had one parcel left. | Continuous |
| 12–15 | 360–450 | the_creek_crossing | push_cart | woodland_creek / windy | establishing / hold | The creek crossed their route. | Continuous |
| 15–18 | 450–540 | the_creek_crossing | push_cart | woodland_creek / windy | interaction_detail / track | Bram took it across by cart. | Continuous |
| 18–21 | 540–630 | the_last_path | walk_to_settle + walk_to_settle | forest_ravine / night | two_shot / track | They followed the ridge down. | Continuous |
| 21–24 | 630–720 | the_last_path | walk_to_settle + walk_to_settle | forest_ravine / night | two_shot / pullback | The village was just beyond it. | Continuous |
| 24–27 | 720–810 | quiet_village | walk_to_settle + walk_to_settle | village_lane / evening | establishing / hold | The village stood silent. | Continuous |
| 27–30 | 810–900 | quiet_village | walk_to_settle + walk_to_settle | village_lane / evening | two_shot / push_in | No doors opened. | Continuous |
| 30–33 | 900–990 | bram_delivers | pickup_carry_place | village_lane / evening | interaction_detail / hold | Bram picked up the parcel. | Continuous |
| 33–36 | 990–1080 | bram_delivers | pickup_carry_place | village_lane / evening | interaction_detail / pullback | He set it by the lane. | Continuous |
| 36–39 | 1080–1170 | the_parcel_stays | react_to_idle | village_lane / evening | medium / hold | He left it for whoever came. | Continuous |
| 39–42 | 1170–1260 | mira_listens | idle_to_notice + idle | village_lane / evening | reaction / push_in | Mira searched. No one answered. | Continuous |
| 42–45 | 1260–1350 | wait_in_the_lane | idle + idle_to_notice | village_lane / evening | establishing / hold | They decided to wait. | Continuous |
| 45–48 | 1350–1440 | wait_in_the_lane | idle + idle_to_notice | village_lane / evening | two_shot / push_in | They decided to wait. | Continuous |
| 48–51 | 1440–1530 | an_answer | idle + idle | village_lane / evening | signal_two_shot / hold | One last moment... | Continuous |
| 51–54 | 1530–1620 | an_answer | idle + idle | village_lane / evening | signal_two_shot / hold | A lamp came on. | Continuous |
| 54–57 | 1620–1710 | an_answer | idle + idle | village_lane / evening | two_shot / hold | Mira saw it first. | Continuous |
| 57–60 | 1710–1800 | an_answer | idle + idle | village_lane / evening | two_shot / pullback | They were not alone. | Continuous |

## Register, verify and deliver

Use a private registry and a fresh output leaf under an existing persistent
non-symlink parent. Keep the real recording, registry and script out of Git
and public review archives. Register a prepared recording using a fresh ID.

```sh
PYTHONPATH=src .venv/bin/python tools/register_audio.py /private/prepared.wav \
  --id town_narration --role narration --registry /private/reelmaker-registry
```

Copy the example into a new request file. Set the narration `asset_id` to
the newly registered ID, apply the authored start/trim and edit the project
from the approved timing map. The supplied recording's file hash stays
pinned in its private registry. The CLI uses the same registry for each step.

```sh
reel() { .venv/bin/python tools/cinematic_project.py --registry /private/reelmaker-registry "$@"; }
reel capabilities
reel validate /private/request.json
reel plan /private/request.json
reel inspect /private/request.json
```

For preflight and production use the same approved request path and fresh
destination. A successful render emits the fully verified native package.

```sh
reel preflight /private/request.json /persistent/job-parent/town
reel render /private/request.json /persistent/job-parent/town
reel verify /persistent/job-parent/town
```

For the synthetic example instead, use
`tools/sprint_f_audio_fixture.py /private/new-timing.wav`, register it
with `--id f_timing_signal --role narration`, then use the example directly.
Review decoded captions, the authored lamp cue, and the report's source hash
and presentation sample clock before delivering the MP4. Human voice
acceptance requires the supplied take and a separate listening review.
