# Autonomous story director

`run_reel.py --strategy director-v2` uses deterministic, chronological story events.
The default remains `legacy`, as does the Python planner API unless a caller selects
`strategy="director-v2"`. Both paths use the same registered renderer and validated
`production-0.1` contract. The output uses the default Yellow Mellow V2 rig and is silent.

## Operate the planner

1. Run `python3 run_reel.py --list-support` and `python3 run_reel.py --check`.
2. Write an ordinary chronological prompt with short clauses. Name the starting setting first
   and the destination afterward. Name a storm, beacon, run or walk only when the story needs it.
3. Run `python3 run_reel.py --strategy director-v2 --prompt-file story.txt --duration 60 --plan-only`.
   Check `story_events` for intent and `observed_staging` for the actual motion starts,
   setting transitions, weather foreground, beacon visibility, camera compositions and warnings.
4. Keep the prompt and flags. Remove `--plan-only` and use a new `--name` under a persistent
   `--output-root`. The job preserves `story_plan.json`, `production_manifest.json`,
   `render_report.json`, `verification.json` and the verified MP4.

The director has one actor, two worlds, seven registered shot families and two durations.
A 15-second story has five 90-frame shots. A 60-second story has 20. Rich short stories that
need more than five distinct shots return a planning error. The structured cinematic operator
remains the route for explicit authoring and registered audio or subtitles.

| Input | Director behavior |
|---|---|
| Mountain, snowy ridge or Frost Peak | Places the actor on the registered snowy ridge |
| Orchard, grove or valley | Uses the registered dusk orchard |
| Blizzard or storm | Uses the registered denser storm foreground on the mountain |
| Beacon, emergency signal or transmitter | Stages a mountain investigation and flare; this flare includes storm weather |
| Run, sprint, flee or escape | Shows the run in the origin during a two-place escape. Escape without a run can use travel when walking is explicit or running is forbidden |
| Safe, relief or relax | The closing event resolves with a stopped, smiling character. The words “safe” and “safety” alone do not request a run |
| No beacon, without a signal, or “the beacon must not appear” | Omits the beacon and answering-light nodes; the director only adds these assets for a positive beacon request |
| No storm or never run | Omits the strong storm treatment or running respectively. Ordinary snow is part of the mountain setting |
| Conflicting positive and negative instructions | Rejects with the conflict named |

Put constraints in simple clauses such as “No beacon or transmitter” and “Do not run.”
The director checks documented words and inflections, common negation patterns, and one
forward transition. It does not resolve arbitrary references, flashbacks, repeated locations,
nested conditions, or implied choreography. Name danger and actions in chronological order.
An explicit escape after reaching the destination is rejected. If the prompt requests downhill
movement, the plan warns that the actor runs across the level ridge. The orchard cut is
editorial and does not imply continuous ground geometry. Unrecognized prose is outside the
constraint grammar. Confirm supported content against the printed plan.

## What changes between strategies

The legacy planner matches broad keyword patterns, maps the order through its environment table,
and distributes extra shots round-robin over its four acts. Its beacon regex matches negated
mentions, and the stock ridge establishing and reaction shots can contain an inactive beacon.
The director recognizes positive and negative mentions separately and assigns origin travel
before destination arrival. It allocates runtime to the resulting events, then stages registered
shots with distinct framing, action or spatial blocking. Consecutive similar reactions and
frequently reused composition signatures are surfaced as warnings. Contract violations in the
generated staging stop the run before rendering.

The storm treatment reuses the registered foreground with a stronger, colder art-direction
preset. The weather reaches the frame before the escape and remains visible during the run.
The director changes the camera and staging only for the opt-in path. The memory limits,
renderer, media assembly and publication guards are shared with the legacy workflow.
