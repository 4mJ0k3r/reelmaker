"""Validated fixed views of the same farm layout, using the existing layer projection."""

from reelforge.environments.scene import Camera
from reelforge.scenes.contract import validate_scene

# Scene units on the 360 × 640 logical artboard. Ground and subject depth agree.
HORIZON = (180, 353)
GROUND = (180, 500)
ROWAN = (132, 541)
BARN = (262, 422)
TREES = (
    ("orchard_tree", 36, 475, 0.95, "broad"),
    ("roadside_tree", 321, 478, 0.81, "leaning"),
    ("foreground_tree", -27, 622, 1.07, "leaning"),
)
ALT_TREES = (
    ("orchard_tree", 42, 500, 0.85, "leaning"),
    ("roadside_tree", 332, 467, 0.85, "broad"),
    ("foreground_tree", 371, 626, 0.94, "broad"),
)
VIEWS = {
    "establishing": Camera(0, 0, 1),
    "medium": Camera(8, 25, 1.30),
    "approach": Camera(0, 0, 1),
}
LAYERS = (
    ("sky_plane", 0),
    ("distance", 0.18),
    ("terrain", 1),
    ("midground", 1),
    ("foreground", 1.4),
)
LEGACY = {
    "cinematic_dusk_sky_01": ("dusk_sky_01", "default"),
    "cinematic_dusk_hills_01": ("distant_hills_01", "default"),
    "cinematic_farm_track_01": ("orchard_ground_01", "default"),
    "cinematic_farm_tree_01": ("orchard_tree_01", None),
}


def transform(x=0, y=0, scale=1):
    return {"x": x, "y": y, "scale": scale, "rotation_degrees": 0}


def farm_scene(view="establishing", *, legacy=False, layout="original"):
    """Assemble an existing scene-0.1 contract. Legacy changes only the visual recipes."""
    if view not in VIEWS:
        raise ValueError(f"Unknown farm view: {view!r}")
    if layout not in {"original", "left_bend"}:
        raise ValueError(f"Unknown farm layout: {layout!r}")
    alternate = layout == "left_bend"
    if alternate and legacy:
        raise ValueError("Legacy artwork is only staged in the original layout")
    actor, barn, trees = ((228, 541), (142, 422), ALT_TREES) if alternate else (ROWAN, BARN, TREES)
    camera = VIEWS[view]
    nodes = []

    def add(identity, kind, parent, order, placement, **fields):
        nodes.append(
            dict(
                id=identity,
                kind=kind,
                parent=parent,
                order=order,
                visible=True,
                transform=placement,
                **fields,
            )
        )

    def place(identity, kind, layer, order, asset, variant, x, y, scale=1, **fields):
        if legacy and asset in LEGACY:
            asset, old_variant = LEGACY[asset]
            variant = old_variant or {"broad": "broad", "leaning": "lean"}[variant]
        add(
            identity,
            kind,
            layer,
            order,
            transform(x, y, scale),
            asset_id=asset,
            variant=variant,
            **fields,
        )

    add("root", "root", None, 0, transform())
    for order, (identity, depth) in enumerate(LAYERS):
        projection = camera.transform(depth)
        add(
            identity,
            "layer",
            "root",
            order,
            transform(projection.tx, projection.ty, projection.sx),
            depth=depth,
        )

    place("sky", "background", "sky_plane", 0, "cinematic_dusk_sky_01", "default", 0, 0)
    place(
        "hills",
        "background",
        "distance",
        0,
        "cinematic_dusk_hills_01",
        "folded" if alternate else "rolling",
        *HORIZON,
    )
    place(
        "ground",
        "environment",
        "terrain",
        0,
        "cinematic_farm_track_01",
        "left_bend" if alternate else "default",
        *GROUND,
    )
    if not legacy:
        place(
            "rowan_contact",
            "asset",
            "terrain",
            1,
            "cinematic_dusk_contact_01",
            "foot",
            *actor,
            0.68,
        )
        place(
            "barn_contact", "asset", "terrain", 2, "cinematic_dusk_contact_01", "prop", *barn, 1.25
        )
    place(
        "barn",
        "asset",
        "midground",
        0,
        "barn_01",
        "default" if legacy else "dusk_graded",
        *barn,
        0.67,
    )
    place(
        "rowan",
        "character",
        "midground",
        8,
        "rowan_01",
        "default",
        *actor,
        0.72,
        ground_id="ground",
        character=dict(
            character="rowan_01",
            action="look_around",
            direction="left" if alternate else "right",
            speed=1.0,
            expression="concerned",
            intensity=0.6,
        ),
    )
    for order, (identity, x, y, scale, variant) in enumerate(trees):
        layer = "foreground" if identity == "foreground_tree" else "midground"
        if not legacy and layer == "midground":
            place(
                f"{identity}_contact",
                "asset",
                "terrain",
                3 + order,
                "cinematic_dusk_contact_01",
                "trunk",
                x,
                y,
                scale,
            )
        place(identity, "asset", layer, 1 + order, "cinematic_farm_tree_01", variant, x, y, scale)

    return validate_scene(
        dict(
            schema_version="scene-0.1",
            title="Last light at the farm",
            camera="approach" if view == "approach" else "locked",
            output=dict(
                width=720, height=1280, fps=30, frames=90, codec="h264", pixel_format="yuv420p"
            ),
            art_direction=dict(warmth=0.8, atmosphere=0.52, breeze=0.2),
            nodes=nodes,
        )
    )
