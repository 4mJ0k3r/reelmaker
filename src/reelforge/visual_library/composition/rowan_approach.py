"""Stage the same Rowan acting recipe against the barn or beacon."""

from reelforge.characters.rowan_performance import NAME

from .cold_ridge import VIEWS as COLD_VIEWS
from .cold_ridge import cold_ridge_manifest
from .farm import VIEWS as FARM_VIEWS
from .farm import farm_manifest


def rowan_approach(world, *, reaction="surprised", legacy=False):
    """Build the shared fixed-facing blocking route at the authored world scale."""
    if world == "farm":
        base = farm_manifest()
        base["nodes"] = [node for node in base["nodes"] if node["id"] != "rowan_contact"]
        x, y = 91, 524
    elif world == "cold_ridge":
        base = cold_ridge_manifest()
        x, y = 110, 480
    else:
        raise ValueError("Select farm or cold_ridge")
    actor = next(node for node in base["nodes"] if node["id"] == "rowan")
    actor["transform"].update(x=x, y=y)
    segments = []
    start = (x, y)
    for first, last, mode, distance, speed, acting, expression in (
        (0, 47, "walk", 47.6, 44, "none", "calm"),
        (47, 59, "stop", 8.8, 0, "none", "calm"),
        (59, 90, "idle", 0, 0, "react", reaction),
    ):
        x += distance
        segments.append(
            dict(
                id=mode,
                start_frame=first,
                end_frame=last,
                mode=mode,
                destination=[x, y],
                end_speed=speed,
                facing="right",
                acting=acting,
                expression=expression,
            )
        )
    plan = dict(
        schema_version="blocking-0.1" if legacy else "blocking-0.2",
        title="Rowan notices a signal",
        base=base,
        actor_id="rowan",
        support_id="ground",
        corridor="level_field",
        start=dict(position=list(start), facing="right"),
        camera="locked",
        segments=segments,
    )
    if not legacy:
        plan["performance"] = {"name": NAME, "reaction": reaction}
    return plan


def rowan_storyboard(world, view="establishing", *, reaction="surprised", legacy=False):
    """Project the same route through a validated storyboard and fixed camera."""
    route = rowan_approach(world, reaction=reaction, legacy=legacy)
    if view not in ("establishing", "medium"):
        raise ValueError("Select establishing or medium")
    camera = (FARM_VIEWS if world == "farm" else COLD_VIEWS)[view]
    actor = dict(actor_id=route["actor_id"], support_id=route["support_id"], start=route["start"])
    if not legacy:
        actor["performance"] = route["performance"]
    focal = {"kind": "point", "position": [180, 400], "depth": 1}
    target = {"kind": "node", "id": "barn" if world == "farm" else "beacon"}
    beats = []
    for segment, beat, action in zip(
        route["segments"],
        ("establish", "discover", "react"),
        ("walk_to", "stop_at", "react"),
        strict=True,
    ):
        motion = dict(kind=action, expression=segment["expression"])
        if action in ("walk_to", "stop_at"):
            motion["end_x"] = segment["destination"][0]
        if action == "walk_to":
            motion["end_speed"] = segment["end_speed"]
        beats.append(
            dict(
                id=beat,
                type=beat,
                frames=segment["end_frame"] - segment["start_frame"],
                subject="signal",
                view="fixed",
                action=motion,
            )
        )
    return dict(
        schema_version="storyboard-0.1",
        title=route["title"],
        world=route["base"],
        rowan=actor,
        subjects=[dict(id="center", target=focal), dict(id="signal", target=target)],
        views=[
            dict(
                id="fixed",
                kind="establishing" if view == "establishing" else "suspense_hold",
                subject="center",
                zoom=[camera.zoom] * 2,
                screen=[180 - camera.x, 400 - camera.y],
                offset_start=[0, 0],
                offset_end=[0, 0],
                lead_seconds=0,
                hold=[0, 0],
                crop="full",
                foreground="clear",
                cut="matched",
            )
        ],
        pattern="discovery_reaction",
        beats=beats,
    )
