"""Admitted scene dressing for the asset-aware director."""

from dataclasses import dataclass

from reelforge.characters.yellow_mellow_v2.artwork import REFERENCE_VARIANT

STRATEGY = "director-v3"


@dataclass(frozen=True)
class Dressing:
    asset: str
    variant: str
    x: float
    y: float
    scale: float

    def node(self, name: str, parent: str, order: int) -> dict:
        return {
            "id": name, "kind": "asset", "parent": parent, "order": order,
            "visible": True, "asset_id": self.asset, "variant": self.variant,
            "transform": {
                "x": self.x, "y": self.y, "scale": self.scale, "rotation_degrees": 0.0,
            },
        }


DUSK_SKY = "cinematic_dusk_sky_01"
DRESSING = {
    "parcel": Dressing("parcel_01", "wrapped", 241, 537, 1.2),
    "lamp": Dressing("streetlamp_01", "lit", 248, 515, 0.8),
    "shrubs": Dressing("shrub_cluster_01", "lush", 104, 514, 0.55),
    "mist": Dressing("ground_mist_01", "thin", 183, 479, 1.25),
    "rocks": Dressing("rock_group_01", "angular", 258, 458, 0.65),
}


def accessible_assets() -> set[str]:
    return {DUSK_SKY, *(item.asset for item in DRESSING.values())}


def dress_storyboard(board: dict, beat, *, forbidden: list[str]) -> None:
    """Choose from a fixed palette by scene, camera and story purpose."""
    nodes = board["world"]["nodes"]
    view = board["views"][0]
    next(node for node in nodes if node["id"] == "mellow")["variant"] = REFERENCE_VARIANT
    wide = view["kind"] in {"establishing", "follow"}
    if beat.env == "orchard":
        next(node for node in nodes if node["id"] == "sky")["asset_id"] = DUSK_SKY
        if wide and "shrubs" not in forbidden:
            nodes.append(DRESSING["shrubs"].node("path_shrubs", "structures", 10))
        if beat.mood in {"hopeful", "warm"} and "lamp" not in forbidden:
            nodes.append(DRESSING["lamp"].node("path_lamp", "structures", 11))
    elif wide:
        if "rocks" not in forbidden:
            nodes.append(DRESSING["rocks"].node("ridge_stones", "structures", 10))
        if beat.weather and "mist" not in forbidden:
            nodes.append(DRESSING["mist"].node("drifting_ground_mist", "terrain", 10))

    if beat.style == "parcel_reveal":
        nodes.append(DRESSING["parcel"].node("found_parcel", "terrain", 11))
        target = next(subject for subject in board["subjects"] if subject["id"] == "ahead")
        target["target"] = {"kind": "node", "id": "found_parcel"}
        view.update(kind="object_reveal", subject="ahead", zoom=[1.45, 1.62], screen=[241, 513],
                    offset_start=[0, -24], offset_end=[0, -24], crop="full")
        for entry in board["beats"][1:]:
            entry["action"]["expression"] = "curious"
