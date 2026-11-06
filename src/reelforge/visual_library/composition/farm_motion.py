"""Stage a short level route using the existing Rowan blocking contract."""

from .farm import farm_manifest


def farm_walk(layout="original", *, moving_camera=False):
    """Return a blocking-0.1 manifest suitable for the existing compiler and CLI."""
    world = farm_manifest("approach" if moving_camera else "establishing", layout=layout)
    world["nodes"] = [node for node in world["nodes"] if node["id"] != "rowan_contact"]
    direction = "right" if layout == "original" else "left"
    sign = 1 if direction == "right" else -1
    x = 91 if direction == "right" else 269
    y = 524
    actor = next(node for node in world["nodes"] if node["id"] == "rowan")
    actor["transform"].update(x=x, y=y)
    segments = []
    for start, end, mode, distance, speed, acting, expression in (
        (0, 9, "idle", 0, 0, "look_around", "calm"),
        (9, 60, "walk", 49, 36, "none", "calm"),
        (60, 72, "stop", 7.2, 0, "none", "calm"),
        (72, 90, "idle", 0, 0, "react", "surprised"),
    ):
        x += sign * distance
        segments.append(
            dict(
                id=f"{mode}_{start}",
                start_frame=start,
                end_frame=end,
                mode=mode,
                destination=[x, y],
                end_speed=speed,
                facing=direction,
                acting=acting,
                expression=expression,
            )
        )
    return dict(
        schema_version="blocking-0.1",
        title="Rowan notices the barn",
        base=world,
        actor_id="rowan",
        support_id="ground",
        corridor="level_field",
        start=dict(position=segments[0]["destination"], facing=direction),
        camera="base" if moving_camera else "locked",
        segments=segments,
    )
