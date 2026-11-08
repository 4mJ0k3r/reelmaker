"""Bounded chronological story direction for the opt-in prompt planner."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .planner import Beat, PlanError, StoryPlan
from .storylib import ENVIRONMENTS

VERSION = "director-v2"

# Exact words and documented inflections. Adjectives like "cold" and "warm" are
# deliberately not place names, and "safety" alone does not imply running.
_PATTERNS = {
    "frost_peak": r"snowy mountains?|icy mountains?|mountains?|ridges?|frost peak|alpine ridge",
    "orchard": r"orchards?|groves?|valleys?",
    "beacon": r"(?:an? )?(?:emergency |distress )?(?:beacon|signal|transmitter)s?",
    "storm": r"(?:snow |winter )?(?:blizzards?|storms?)",
    "run": r"runs?|ran|running|sprints?|sprinted|flee(?:s|ing)?|flees|dashes|dash",
    "escape": r"escapes?|escaped|escaping",
    "walk": r"walks?|walking|hikes?|treks?",
    "resolution": r"relie(?:f|ved)|relax(?:es|ed)?|safe|safety|calms down|finds peace",
    "audio": r"dialogue|voiceover|voice-over|narration|music|soundtrack|audio",
}
_MENTION = re.compile(
    r"\b(?:" + "|".join(f"(?P<{key}>{value})" for key, value in _PATTERNS.items()) + r")\b",
    re.IGNORECASE,
)
_NEGATION = re.compile(
    r"\b(?:no|without|avoid(?:s|ing)?|exclude|omit|never|do not|does not|must not|should not|"
    r"don['’]t|doesn['’]t|mustn['’]t)\s+"
    r"(?:(?:a|an|the|any|use|show|include|add|feature|depict|contain|have|make|him|her|them)\s+)*$"
)
_NEGATIVE_SUFFIX = re.compile(
    r"^\s+(?:(?:must|should|does|do|will)\s+not\s+(?:appear|be (?:seen|shown|visible|used)|"
    r"run|happen|occur)|(?:is|are)\s+forbidden)\b"
)
_NEGATIVE_LIST = re.compile(r"\s*(?:,\s*)?(?:and|or)?\s*")
_CLAUSE_BREAK = re.compile(r"[.!?;\n]|\b(?:then|later|afterwards|finally)\b")
_DESTINATION = re.compile(r"\b(?:to|into|toward(?:s)?|reach(?:es|ing)?|arriv(?:e|es|ing)\s+(?:at|in))\b")
_REVERSE = re.compile(r"\b(?:flashback|earlier|back to)\b")
_REACHED_SAFETY = re.compile(
    r"\b(?:reaches|reached|finds|found|recognizes|recognised)\s+safety$"
)


@dataclass(frozen=True)
class Mention:
    tag: str
    start: int
    end: int
    clause: int
    forbidden: bool


def _mentions(text: str) -> list[Mention]:
    breaks = [match.end() for match in _CLAUSE_BREAK.finditer(text)]
    mentions: list[Mention] = []
    for match in _MENTION.finditer(text):
        clause = sum(end <= match.start() for end in breaks)
        prefix = text[(breaks[clause - 1] if clause else 0):match.start()]
        previous = mentions[-1] if mentions else None
        inherited = (
            previous is not None and previous.forbidden and previous.clause == clause
            and bool(_NEGATIVE_LIST.fullmatch(text[previous.end:match.start()]))
        )
        forbidden = bool(
            _NEGATION.search(prefix) or _NEGATIVE_SUFFIX.match(text[match.end():]) or inherited
        )
        mentions.append(Mention(match.lastgroup, match.start(), match.end(), clause, forbidden))
    return mentions


def _place_for(text: str, mention: Mention, locations: list[Mention]) -> str:
    """A following location can qualify an action, unless it is the destination."""
    past = [place for place in locations if place.start < mention.start]
    for place in locations:
        if place.start > mention.start and place.clause == mention.clause:
            connector = text[mention.end:place.start]
            if not _DESTINATION.search(connector):
                return place.tag
            break
    return past[-1].tag if past else locations[0].tag


@dataclass(frozen=True)
class Shot:
    preset: str
    mood: str
    purpose: str
    style: str = "standard"


# Each recipe has a primary shot for a short film and meaningful continuations for
# a long one. Their windows are allocated by narrative role, not by prompt title.
_OPEN = (
    Shot("establish", "calm", "orient the viewer"),
    Shot("travel", "calm", "cross the starting ground"),
    Shot("reaction", "tense", "register uncertainty"),
    Shot("establish", "tense", "reframe the route ahead", "route"),
)
_STORM = (
    Shot("establish", "storm", "show the first strong gust", "weather"),
    Shot("reaction", "storm", "register the worsening weather"),
    Shot("travel", "storm", "cross exposed ground", "weather"),
    Shot("reaction", "storm", "brace and choose to move", "decision"),
)
_BEACON = (
    Shot("investigate", "tense", "investigate and activate the beacon"),
    Shot("threat", "storm", "show the flare and the reaction"),
)
_RUN = (
    Shot("travel_run", "determined", "launch the escape"),
    Shot("travel_run", "determined", "show travel across the landscape", "run_wide"),
    Shot("travel_run", "determined", "follow the effort up close", "run_tight"),
    Shot("travel_run", "determined", "carry the escape toward the next cut", "run_exit"),
)
_WALK = (
    Shot("travel", "determined", "follow the journey"),
    Shot("establish", "calm", "locate the route in the landscape", "route"),
    Shot("travel", "hopeful", "continue toward the destination", "route"),
    Shot("reaction", "hopeful", "check the route ahead", "decision"),
)
_ARRIVE = (
    Shot("establish", "warm", "establish the destination"),
    Shot("travel", "hopeful", "walk and come to a stop"),
    Shot("establish", "warm", "show the destination from another angle", "route"),
    Shot("reaction", "warm", "slow and take in the surroundings", "settle"),
)
_END = (
    Shot("reaction", "warm", "recognize safety"),
    Shot("establish", "warm", "give the new setting room to breathe", "route"),
    Shot("reaction", "warm", "settle into relief", "settle"),
    Shot("resolve", "warm", "close on a stopped, relieved character", "relief_close"),
)


@dataclass(frozen=True)
class Stage:
    name: str
    environment: str
    action: str
    emotion: str
    relationship: str
    shots: tuple[Shot, ...]
    weather: bool = False


def _stage_shots(stage: Stage, count: int) -> list[Shot]:
    # Preserve a resolving close even when the whole closing act is one shot.
    if stage.name == "resolution":
        return [*(stage.shots[i % (len(stage.shots) - 1)] for i in range(count - 1)), stage.shots[-1]]
    if stage.name == "danger" and count == 1:
        return [Shot("reaction", "storm", "react to the storm")]
    return [stage.shots[i % len(stage.shots)] for i in range(count)]


def _allocate(stages: list[Stage], target: int) -> list[int]:
    sizes = [len(stage.shots) if stage.name == "beacon" else 1 for stage in stages]
    if sum(sizes) > target:
        raise PlanError("The requested story beats need more than five shots. Use 60 seconds.")
    while sum(sizes) < target:
        # First fill each visual recipe once. If a long single-location story
        # still needs shots, distribute repeats across its shortest acts.
        candidates = [i for i, stage in enumerate(stages) if stage.name != "beacon"]
        available = [i for i in candidates if sizes[i] < len(stages[i].shots)]
        i = min(available or candidates, key=lambda i: (sizes[i], i))
        sizes[i] += 1
    return sizes


def plan_directed(prompt: str, duration: int, target: int, title: str | None) -> StoryPlan:
    if not isinstance(prompt, str) or not prompt.strip():
        raise PlanError("Provide a non-empty story prompt")
    if len(prompt) > 4000:
        raise PlanError("Director prompts are limited to 4,000 characters")
    text = prompt.lower()
    mentions = _mentions(text)
    requested = {m.tag for m in mentions if not m.forbidden}
    forbidden = {m.tag for m in mentions if m.forbidden}
    if clash := requested & forbidden:
        raise PlanError("Requested and forbidden: " + ", ".join(sorted(clash)))
    if unsupported := forbidden & {"walk", "resolution", "escape"}:
        raise PlanError("Cannot guarantee exclusion of " + ", ".join(sorted(unsupported)))
    if "audio" in requested:
        raise PlanError("Director output is silent. Use the structured workflow for registered audio.")
    locations = [m for m in mentions if m.tag in ENVIRONMENTS and not m.forbidden]
    environments = [m.tag for i, m in enumerate(locations) if i == 0 or m.tag != locations[i-1].tag]
    if not environments:
        raise PlanError("Mention a supported location: snowy mountain/ridge or orchard/valley")
    if len(environments) > 2 or _REVERSE.search(text):
        raise PlanError("Use a forward, chronological story with at most one location transition")

    origin, destination = environments[0], environments[-1]
    moving = len(environments) > 1
    storm = "storm" in requested
    beacon = "beacon" in requested
    running = "run" in requested
    if beacon and "storm" in forbidden:
        raise PlanError("The beacon flare preset includes storm weather")
    if "escape" in requested and "run" not in forbidden and "walk" not in requested:
        running = True

    run_mentions = [m for m in mentions if not m.forbidden and m.tag in {"run", "escape"}]
    storm_mentions = [m for m in mentions if not m.forbidden and m.tag == "storm"]
    beacon_mentions = [m for m in mentions if not m.forbidden and m.tag == "beacon"]
    for m in mentions:
        if m.forbidden:
            continue
        if m.tag in {"storm", "beacon"} and _place_for(text, m, locations) != "frost_peak":
            raise PlanError(f"{m.tag.capitalize()} is only supported on the snowy mountain")
        if m.tag in {"run", "escape"} and moving:
            place = _place_for(text, m, locations)
            if place != origin:
                raise PlanError("A journey escape must occur before arrival. Name the origin for the run.")
    # "Runs from the blizzard" describes its cause in the same clause.
    if running and storm_mentions and run_mentions[0].clause < storm_mentions[0].clause:
        raise PlanError("Place the storm before the escape in a chronological request")
    if running and beacon_mentions and run_mentions[0].clause < beacon_mentions[0].clause:
        raise PlanError("The beacon investigation must precede the escape in this workflow")
    if running and any(
        not m.forbidden and m.tag == "resolution" and m.clause < run_mentions[0].clause
        and _REACHED_SAFETY.search(text[:m.end])
        for m in mentions
    ):
        raise PlanError("The escape must precede reaching safety")
    if storm and origin != "frost_peak":
        raise PlanError("A storm escape must start on the snowy mountain")
    if beacon and origin != "frost_peak":
        raise PlanError("A beacon investigation must start on the snowy mountain")

    stages = [Stage("orientation", origin, "walk and look around", "uncertainty", "opening", _OPEN)]
    incidents = []
    if beacon:
        incidents.append((beacon_mentions[0].start, Stage(
            "beacon", origin, "activate and react", "suspense", "a local discovery", _BEACON, storm,
        )))
    if storm:
        incidents.append((storm_mentions[0].start, Stage(
            "danger", origin, "notice, brace and decide", "concern to determination",
            "weather motivates the next action", _STORM, True,
        )))
    stages.extend(stage for _, stage in sorted(incidents, key=lambda item: item[0]))
    stages.append(Stage("escape" if running else "journey", origin, "run" if running else "walk",
                        "determination", "travel before arrival", _RUN if running else _WALK, storm))
    if moving:
        stages.append(Stage("arrival", destination, "walk and stop", "caution to calm",
                            "editorial cut after origin travel", _ARRIVE))
    stages.append(Stage("resolution", destination, "stop and relax", "relief", "after travel or arrival", _END))

    warnings = []
    if re.search(r"\bdownhill\b", text):
        warnings.append("Downhill motion is unsupported. The run crosses the registered level ridge.")
    counts = _allocate(stages, target)
    beats, events = [], []
    occurrences: dict[tuple[str, str], int] = {}
    for stage, count in zip(stages, counts, strict=True):
        start_frame = len(beats) * 90
        for shot in _stage_shots(stage, count):
            key = (stage.environment, shot.preset)
            variant = occurrences.get(key, 0)
            occurrences[key] = variant + 1
            beats.append(Beat(
                shot.preset, stage.environment, shot.mood, f"{len(beats)+1:02d} {shot.purpose.capitalize()}",
                f"Yellow Mellow: {shot.purpose} in {ENVIRONMENTS[stage.environment]['display']}.",
                variant, shot.style, stage.weather,
            ))
        events.append({
            "purpose": stage.name, "environment": stage.environment, "action": stage.action,
            "emotional_intent": stage.emotion, "relationship": stage.relationship,
            "start_frame": start_frame, "end_frame_exclusive": len(beats)*90,
        })
    return StoryPlan(
        prompt=prompt, title=title or "Yellow Mellow — " + prompt.strip()[:65],
        environments=environments, beats=beats, duration_seconds=duration,
        strategy=VERSION, events=events,
        constraints={"requested": sorted(requested), "forbidden": sorted(forbidden),
                     "required_running": running, "beacon": beacon},
        warnings=warnings,
    )


def inspect_directed_manifest(plan: StoryPlan, manifest: dict) -> dict:
    """Check compiled inputs against the intent and expose their actual staging."""
    rows = []
    for index, (beat, segment) in enumerate(zip(plan.beats, manifest["segments"], strict=True)):
        board = segment["storyboard"]
        nodes = board["world"]["nodes"]
        offset = index * 90
        clock = offset
        run_starts = []
        for entry in board["beats"]:
            if entry["action"]["kind"] == "run_to":
                run_starts.append(clock)
            clock += entry["frames"]
        view = board["views"][0]
        rows.append({
            "shot": index + 1,
            "start_frame": offset,
            "environment": beat.env,
            "preset": beat.preset,
            "camera": view["kind"],
            "zoom": view["zoom"],
            "screen": view["screen"],
            "actor_start": board["rowan"]["start"]["position"],
            "actions": [entry["action"]["kind"] for entry in board["beats"]],
            "expressions": [entry["action"]["expression"] for entry in board["beats"]],
            "run_start_frames": run_starts,
            "storm_foreground": any(n.get("variant") == "storm" for n in nodes),
            "beacon_visible": any(
                n.get("asset_id") in {"beacon_01", "answer_light_01"} and n["visible"]
                for n in nodes
            ),
        })

    transitions = [
        row["start_frame"] for previous, row in zip(rows, rows[1:])
        if previous["environment"] != row["environment"]
    ]
    runs = [
        {"frame": frame, "environment": row["environment"]}
        for row in rows for frame in row["run_start_frames"]
    ]
    observed = list(dict.fromkeys(row["environment"] for row in rows))
    violations = []
    if observed != plan.environments or len(transitions) != len(plan.environments) - 1:
        violations.append("Missing or misordered environment")
    if plan.constraints["required_running"] and not runs:
        violations.append("Required run has no visible action")
    if transitions and any(run["frame"] >= transitions[0] for run in runs):
        violations.append("Escape occurs after arrival")
    if "walk" in plan.constraints["requested"] and not any(
        "walk_to" in row["actions"] for row in rows
    ):
        violations.append("Required walk has no visible action")
    if "run" in plan.constraints["forbidden"] and runs:
        violations.append("Forbidden run is present")
    if "storm" in plan.constraints["requested"] and not any(row["storm_foreground"] for row in rows):
        violations.append("Required storm has no visible weather")
    if "storm" in plan.constraints["forbidden"] and any(row["storm_foreground"] for row in rows):
        violations.append("Forbidden storm is present")
    has_beacon = any(row["beacon_visible"] for row in rows)
    if has_beacon != plan.constraints["beacon"]:
        violations.append("Beacon visibility differs from the requested constraint")
    if rows[-1]["preset"] != "resolve" or rows[-1]["expressions"][-1] != "happy":
        violations.append("Ending lacks a visible resolution")

    warnings = list(plan.warnings)
    same_reaction = longest_reaction = 0
    for row in rows:
        same_reaction = same_reaction + 1 if row["preset"] == "reaction" else 0
        longest_reaction = max(longest_reaction, same_reaction)
    compositions = {
        (row["environment"], row["camera"], tuple(row["zoom"]), tuple(row["screen"]),
         tuple(row["actor_start"]), tuple(row["actions"])) for row in rows
    }
    if len(compositions) < len(rows) * 0.8:
        warnings.append("More than one fifth of shots reuse the same staging signature.")
    if longest_reaction > 2:
        warnings.append("Three or more consecutive reaction presets may feel repetitive.")
    if violations:
        raise PlanError("; ".join(violations))
    return {
        "environment_transition_frames": transitions,
        "running_actions": runs,
        "beacon_visible": has_beacon,
        "longest_consecutive_reaction_run": longest_reaction,
        "violations": violations,
        "warnings": warnings,
        "shots": rows,
    }
