"""Locked Dusk Farm compositions for architectural scale and contact review."""

from reelforge.visual_library.architecture.buildings import BUILDINGS

from .farm import farm_manifest, transform


def building_showcase(asset_id, variant):
    building = BUILDINGS[asset_id]
    scene = farm_manifest()
    scene["title"] = f"{building.name} at Dusk Farm"
    scene["nodes"] = [node for node in scene["nodes"] if node["id"] != "barn_contact"]
    for node in scene["nodes"]:
        if node["id"] == "barn":
            node.update(id="building", asset_id=asset_id, variant=variant,
                        transform=transform(220, 473, 0.96))
        elif node["id"] == "rowan":
            node["transform"] = transform(114, 486, 0.25)
        elif node["id"] == "rowan_contact":
            node["transform"] = transform(114, 486, 0.25)
        elif node["id"] in {"roadside_tree", "roadside_tree_contact"}:
            node["transform"] = transform(340, 439, 0.66)
    return scene
