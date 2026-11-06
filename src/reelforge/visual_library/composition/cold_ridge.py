"""Trusted scene-0.1 staging for the Cold Ridge mountain pass."""

from reelforge.environments.scene import Camera
from reelforge.scenes.contract import validate_scene

GROUND = (180, 470)
VIEWS = {"establishing": Camera(0, 0, 1), "medium": Camera(10, 12, 1.29)}
LAYERS = (
    ("sky_layer", 0),
    ("distance", 0.22),
    ("massif", 0.52),
    ("terrain", 1),
    ("subjects", 1),
    ("near_snow", 1.4),
    ("weather", 1.25),
)
LAYOUTS = {
    "pass": (
        (136, 480),
        (239, 484),
        (
            ("pine_left", 38, 475, 1.16, "pinnacle"),
            ("pine_right", 324, 491, 0.95, "windshear"),
            ("pine_spur", 350, 471, 0.60, "pinnacle"),
        ),
        (("outcrop", 287, 514, 0.43, "cliff"), ("ledge", -19, 646, 0.93, "cliff")),
    ),
    "saddle": (
        (245, 479),
        (146, 479),
        (
            ("pine_left", 29, 480, 0.93, "windshear"),
            ("pine_right", 325, 479, 1.19, "pinnacle"),
            ("pine_spur", 72, 471, 0.50, "pinnacle"),
        ),
        (("outcrop", 97, 489, 0.53, "cliff"), ("ledge", 378, 650, 0.95, "cliff")),
    ),
}


def _transform(x=0, y=0, scale=1):
    return dict(x=x, y=y, scale=scale, rotation_degrees=0)


def cold_ridge_manifest(view="establishing", *, layout="pass", weather="clear", legacy=False):
    """Build scene data for normal validation or trusted blocking composition."""
    if view not in VIEWS or layout not in LAYOUTS or weather not in ("clear", "storm"):
        raise ValueError(
            "Choose an establishing/medium view, pass/saddle layout and clear/storm weather"
        )
    actor, beacon, trees, rocks = LAYOUTS[layout]
    storm = weather == "storm"
    camera = VIEWS[view]
    nodes = [
        dict(id="root", kind="root", parent=None, order=0, visible=True, transform=_transform())
    ]
    for order, (key, depth) in enumerate(LAYERS):
        projection = camera.transform(depth)
        nodes.append(
            dict(
                id=key,
                kind="layer",
                parent="root",
                order=order,
                visible=True,
                depth=depth,
                transform=_transform(projection.tx, projection.ty, projection.sx),
            )
        )

    def place(key, layer, order, asset, variant, x, y, scale=1, kind="asset", **extra):
        nodes.append(
            dict(
                id=key,
                kind=kind,
                parent=layer,
                order=order,
                visible=True,
                transform=_transform(x, y, scale),
                asset_id=asset,
                variant=variant,
                **extra,
            )
        )

    place("sky", "sky_layer", 0, "frost_sky_01", "default", 0, 0, kind="background")
    place(
        "far_peaks",
        "distance",
        0,
        "frost_peaks_01",
        "far" if legacy else "cinematic_far",
        180,
        292,
        kind="background",
    )
    place(
        "near_peaks",
        "massif",
        0,
        "frost_peaks_01",
        "mid" if legacy else "cinematic_massif",
        180,
        300,
        kind="background",
    )
    place(
        "ground",
        "terrain",
        0,
        "frost_ridge_01",
        "default" if legacy else "sculpted",
        *GROUND,
        kind="environment",
    )
    place(
        "rock_contact",
        "terrain",
        1,
        "cinematic_dusk_contact_01",
        "prop",
        rocks[0][1],
        rocks[0][2],
        0.6,
    )
    place("outcrop", "subjects", 0, "frost_rocks_01", rocks[0][4], *rocks[0][1:4])
    for order, (key, x, y, scale, variant) in enumerate(trees, 1):
        old = "tall" if variant == "pinnacle" else "short"
        place(key, "subjects", order, "pine_snow_01", old if legacy else variant, x, y, scale)
    place(
        "rowan",
        "subjects",
        5,
        "rowan_01",
        "default",
        *actor,
        0.72,
        "character",
        ground_id="ground",
        character=dict(
            character="rowan_01",
            action="look_around",
            direction="right" if layout == "pass" else "left",
            speed=1,
            expression="concerned",
            intensity=0.65,
        ),
    )
    place(
        "beacon", "subjects", 6, "beacon_01", "active" if legacy else "local_signal", *beacon, 0.83
    )
    place("ledge", "near_snow", 0, "frost_rocks_01", rocks[1][4], *rocks[1][1:4])
    if storm:
        place(
            "wind",
            "weather",
            0,
            "frost_foreground_01",
            "storm" if legacy else "ridge_wind",
            180,
            640,
            kind="environment",
        )

    return dict(
        schema_version="scene-0.1",
        title="Cold Ridge",
        camera="locked",
        output=dict(
            width=720, height=1280, fps=30, frames=90, codec="h264", pixel_format="yuv420p"
        ),
        art_direction=dict(
            warmth=0.18, atmosphere=0.73 if storm else 0.51, breeze=0.85 if storm else 0.05
        ),
        nodes=nodes,
    )


def cold_ridge_scene(view="establishing", *, layout="pass", weather="clear", legacy=False):
    """Return a validated scene for the selected fixed composition."""
    return validate_scene(cold_ridge_manifest(view, layout=layout, weather=weather, legacy=legacy))


def cold_ridge_walk():
    """A sampled level approach through the existing blocking-0.1 contract."""
    world = cold_ridge_manifest(weather="storm")
    actor = next(node for node in world["nodes"] if node["id"] == "rowan")
    actor["transform"].update(x=110, y=480)
    segments = [
        dict(
            id=f"{mode}_{start}",
            start_frame=start,
            end_frame=end,
            mode=mode,
            destination=[x, 480],
            end_speed=speed,
            facing="right",
            acting=acting,
            expression=expression,
        )
        for start, end, mode, x, speed, acting, expression in (
            (0, 9, "idle", 110, 0, "look_around", "calm"),
            (9, 60, "walk", 159, 36, "none", "calm"),
            (60, 72, "stop", 166.2, 0, "none", "calm"),
            (72, 90, "idle", 166.2, 0, "look_around", "concerned"),
        )
    ]
    return dict(
        schema_version="blocking-0.1",
        title="Cold Ridge level approach",
        base=world,
        actor_id="rowan",
        support_id="ground",
        corridor="level_field",
        start=dict(position=[110, 480], facing="right"),
        camera="locked",
        segments=segments,
    )
