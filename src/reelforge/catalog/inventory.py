"""Adapt trusted runtime declarations to a discovery document without drawing."""

import inspect
from pathlib import Path

from reelforge.blocking import contract as blocking
from reelforge.characters import registry, rowan, rowan_performance
from reelforge.characters.yellow_mellow_v2 import episode as mellow_episode
from reelforge.characters.yellow_mellow_v2 import investigation
from reelforge.direction import contract as direction
from reelforge.environments import artwork, polish, snowy
from reelforge.mvp import storylib
from reelforge.procedural import compiler, contract, planning, recipes
from reelforge.scenes import assets, graph
from reelforge.scenes import contract as scene
from reelforge.visual_library.architecture.buildings import BUILDINGS
from reelforge.visual_library.composition import character_staging

from reelforge.characters.living import PROFILES, draw_actor
from reelforge.visual_library.living_assets import EFFECTS, PROPS
from reelforge.visual_library import frontier_art
from reelforge.visual_library.world_assets import WORLD_ASSETS

ROOT = Path(__file__).resolve().parents[3]
FAMILIES = (
    "architecture",
    "characters",
    "composition",
    "effects",
    "infrastructure",
    "lighting",
    "materials",
    "nature",
    "props",
)
# Curated labels and source pointers. Registration, variants and limits come from ASSETS.
SCENE_LABELS = {
    "ravine_fir_01": ("Ravine fir", "nature", (frontier_art.ravine_fir.__wrapped__,)),
    "abandoned_outpost_skyline_01": ("Outpost skyline", "nature", (frontier_art.skyline.__wrapped__,)),
    "forest_ravine_skyline_01": ("Ravine skyline", "nature", (frontier_art.skyline.__wrapped__,)),
    "abandoned_outpost_terrain_01": ("Outpost terrain", "nature", (frontier_art.terrain.__wrapped__,)),
    "forest_ravine_terrain_01": ("Ravine terrain", "nature", (frontier_art.terrain.__wrapped__,)),
    "outpost_watch_shelter_01": ("Outpost watch shelter", "architecture", (frontier_art.watch_shelter.__wrapped__,)),

    **{identity: (item.name, item.family, (item.draw,))
       for identity, item in {**WORLD_ASSETS, **PROPS, **EFFECTS}.items()},
    **{identity: (building.name, "architecture", (building.draw,))
       for identity, building in BUILDINGS.items()},
    "cinematic_dusk_sky_01": ("Cinematic dusk sky", "nature", (assets.dusk_sky,)),
    "cinematic_dusk_hills_01": ("Cinematic dusk hills", "nature", (assets.dusk_hills,)),
    "cinematic_farm_track_01": ("Cinematic farm track", "nature", (assets.farm_track,)),
    "cinematic_farm_tree_01": ("Cinematic farm tree", "nature", (assets.farm_tree,)),
    "cinematic_dusk_contact_01": ("Dusk ground contact", "lighting", (assets.dusk_contact,)),
    "dusk_sky_01": ("Dusk sky", "nature", (polish.sky,)),
    "distant_hills_01": (
        "Distant hills and haze",
        "nature",
        (
            artwork.hills,
            polish.haze,
        ),
    ),
    "orchard_ground_01": ("Orchard ground", "nature", (polish.ground,)),
    "barn_01": (
        "Barn exterior",
        "architecture",
        (
            artwork.barn,
            polish.barn_light,
            assets.grade_architecture,
        ),
    ),
    "orchard_tree_01": ("Orchard tree", "nature", (polish.tree,)),
    "fence_01": ("Farm fence", "architecture", (artwork.fence,)),
    "foreground_boughs_01": (
        "Foreground boughs",
        "nature",
        (
            artwork.foreground,
            polish.foreground_detail,
        ),
    ),
    "frost_sky_01": ("Frost Peak sky", "nature", (snowy.frost_sky,)),
    "frost_peaks_01": (
        "Snowy peaks",
        "nature",
        (
            snowy.frost_peaks,
            assets.cold_peaks,
        ),
    ),
    "frost_ridge_01": (
        "Snowy ridge",
        "nature",
        (
            snowy.frost_ridge,
            assets.cold_ground,
        ),
    ),
    "pine_snow_01": (
        "Snow-covered pine",
        "nature",
        (
            snowy.pine_snow,
            assets.cold_pine,
        ),
    ),
    "frost_rocks_01": ("Frost Peak rocks", "nature", (snowy.frost_rocks,)),
    "beacon_01": ("Emergency beacon", "props", (snowy.beacon,)),
    "answer_light_01": ("Distant answering light", "lighting", (snowy.answer_light,)),
    "frost_foreground_01": (
        "Frost foreground and snowstorm",
        "effects",
        (
            snowy.frost_foreground,
            assets.ridge_wind,
        ),
    ),
}
CINEMATIC_METADATA = {
    "cinematic_dusk_sky_01": (
        ("warmth", "atmosphere"),
        "sky-hills.jpg",
        "Canvas origin at top left. Dusk sun is on the left.",
    ),
    "cinematic_dusk_hills_01": (
        ("atmosphere",),
        "sky-hills.jpg",
        "Place the origin at the horizon reference. Static profiles.",
    ),
    "cinematic_farm_track_01": (
        ("warmth",),
        "ground-path.jpg",
        "Supports ground-plane staging. The track is authored geometry.",
    ),
    "cinematic_farm_tree_01": (
        ("warmth",),
        "tree-silhouettes.jpg",
        "Place the trunk foot at the origin. Static authored silhouettes.",
    ),
    "cinematic_dusk_contact_01": (
        (),
        "farm-establishing.jpg",
        "Static ground decal. Place under its subject on the same plane.",
    ),
}
RECIPE_FAMILIES = {
    "building": "architecture",
    "entrance": "architecture",
    "prop": "props",
}
COLD_METADATA = {
    "frost_peaks_01": (
        ("atmosphere",),
        "mountains.jpg",
        "Cinematic variants are trusted scene opt-ins; the planner retains far and mid.",
    ),
    "frost_ridge_01": (
        ("warmth", "atmosphere"),
        "terrain-rock.jpg",
        "Sculpted uses atmosphere and the original level support; no slope navigation.",
    ),
    "pine_snow_01": (
        ("breeze",),
        "conifers.jpg",
        "Pinnacle and windshear are static; breeze applies only to legacy variants.",
    ),
    "frost_foreground_01": (
        ("breeze",),
        "clear-storm.jpg",
        "Ridge wind adds restrained streaks outside the action band of the Cold Ridge composition.",
    ),
    "beacon_01": (
        ("warmth",),
        "cold-establishing.jpg",
        "Local signal keeps the activation socket and amber light without the distant beam.",
    ),
}
SCENE_ART = {
    key: {"type": "number", "minimum": 0, "maximum": 1}
    for key in ("warmth", "atmosphere", "breeze")
}


def reference(target):
    return (
        f"{Path(inspect.getfile(target)).resolve().relative_to(ROOT).as_posix()}:{target.__name__}"
    )


def component(
    identity,
    name,
    family,
    kind,
    sources,
    *,
    registration=(),
    variants=(),
    exposure="unavailable",
    parameters=None,
    restrictions=(),
    dependencies=(),
    details=None,
):
    return {
        "id": identity,
        "name": name,
        "family": family,
        "type": kind,
        "sources": [reference(source) for source in sources],
        "variants": list(variants),
        "parameters": parameters,
        "registration": list(registration),
        "engine_capability": True,
        "production_status": "candidate",
        "planner_exposure": exposure,
        "quality_review": "not_assessed",
        "restrictions": list(restrictions),
        "dependencies": list(dependencies),
        "details": details or {},
    }


def planner_usage():
    """Inspect actual trusted storyboard builders, including their staging variants."""
    asset_ids, views = set(), set()
    for environment in storylib.ENVIRONMENTS:
        for preset in storylib.SHOT_PRESETS:
            if environment != "frost_peak" and preset in {"investigate", "threat"}:
                continue  # These two builders require the Frost Peak beacon.
            for variant in range(storylib.VARIANT_COUNT.get(preset, 1)):
                shot = storylib.build_shot(
                    preset,
                    environment,
                    title="Inventory",
                    description="Inventory",
                    mood="calm",
                    variant=variant,
                )
                world = shot["world"]
                asset_ids.update(node["asset_id"] for node in world["nodes"] if "asset_id" in node)
                views.update(view["kind"] for view in shot["views"])
    return asset_ids, views


def registered_components(planner_assets):
    scene_ids = {asset.id for asset in assets.ASSETS}
    characters = [registry.character_info(key) for key in registry.character_ids()]
    by_asset = {character.asset_id: character for character in characters}
    if (
        len(scene_ids) != len(assets.ASSETS)
        or len(by_asset) != len(characters)
        or scene_ids != set(SCENE_LABELS) | set(by_asset)
        or set(SCENE_LABELS) & set(by_asset)
        or set(by_asset) != {asset.id for asset in assets.ASSETS if asset.kind == "character"}
        or planner_assets - scene_ids
    ):
        raise ValueError("Scene registry, character registry, planner and catalog labels disagree")
    for asset in assets.ASSETS:
        actor = by_asset.get(asset.id)
        parameters = {"variant": {"choices": list(asset.variants)}}
        details = {
            "scene_kind": asset.kind,
            "anchor": list(asset.anchor),
            "upright": asset.upright,
            "support_envelope": list(asset.support_envelope) if asset.support_envelope else None,
            "budget": {"max_paths": asset.max_paths, "max_operations": asset.max_ops},
        }
        restrictions = ["Use the registered scene node kind and scene-0.1 validation."]
        sources = [assets.recipe]
        registration = ["scene"]
        if actor:
            name, family = actor.display_name, "characters"
            registration.append("character")
            details.update(
                character_id=actor.character_id, standing_height_units=actor.standing_height_units
            )
            parameters.update(
                registry_actions={"choices": list(actor.scene_actions)},
                scene_action={
                    "choices": ["idle", "look_around", "react"]
                    if actor.character_id == registry.ROWAN_ID
                    else list(actor.scene_actions) if actor.character_id in PROFILES
                    else ["idle", "look_around", "look", "react"]
                },
                expressions={
                    "choices": list(actor.expressions),
                    "default": actor.default_expression,
                },
            )
            sources.extend(
                [
                    registry.character_info,
                    registry.draw_commands_builder,
                    rowan.draw_character
                    if actor.character_id == registry.ROWAN_ID
                    else draw_actor if actor.character_id in PROFILES
                    else mellow_episode.build_drawer,
                ]
            )
            if actor.character_id in PROFILES:
                restrictions.append("Scene renderer only; blocking and storyboards retain their historical actor scope.")
                details["preview_evidence"] = [
                    f"docs/visual-evidence/sprint-b/{actor.character_id}-{kind}.png"
                    for kind in ("neutral", "expressions", "actions")
                ]
            else:
                restrictions.append(
                    "Registry actions are broader than the stationary actions accepted by scene-0.1."
                )
            if actor.character_id == registry.ROWAN_ID:
                parameters["performance.name"] = {"choices": [rowan_performance.NAME]}
                parameters["performance.reaction"] = {"choices": list(rowan_performance.REACTIONS)}
                sources.extend((blocking.compile_blocking, rowan_performance.apply_performance))
                restrictions.append(
                    "Optional notice_and_react uses blocking-0.2 or storyboard rowan.performance "
                    "with a validated walk, stop and final idle. Planner exposure is unchanged."
                )
                details["preview_evidence"] = ["docs/visual-evidence/stage2a/acting.jpg"]
                details["integration_evidence"] = [
                    "docs/visual-evidence/stage2a/farm-medium.jpg",
                    "docs/visual-evidence/stage2a/cold_ridge-medium.jpg",
                ]
            elif actor.character_id == registry.YELLOW_MELLOW_ID:
                parameters["performance.name"] = {"choices": [investigation.NAME]}
                parameters["performance.reaction"] = {"choices": [investigation.REACTION]}
                sources.extend((blocking.compile_blocking, investigation.build_investigation))
                restrictions.append(
                    "Optional investigate_and_react uses blocking-0.2 or storyboard "
                    "rowan.performance with a fixed-facing walk, stop and final idle."
                )
                details["preview_evidence"] = ["docs/visual-evidence/stage2b/acting.jpg"]
                details["integration_evidence"] = [
                    "docs/visual-evidence/stage2b/farm-medium.jpg",
                    "docs/visual-evidence/stage2b/cold-ridge-medium.jpg",
                ]
        else:
            name, family, artwork_sources = SCENE_LABELS[asset.id]
            sources.extend(artwork_sources)
        if asset.id in CINEMATIC_METADATA:
            controls, preview, note = CINEMATIC_METADATA[asset.id]
            parameters.update({f"art_direction.{key}": SCENE_ART[key] for key in controls})
            parameters["transform.scale"] = {"type": "number", "minimum": 0.25, "maximum": 2}
            restrictions.append(note)
            details["preview_evidence"] = [f"docs/visual-evidence/stage1a1/{preview}"]
            details["integration_evidence"] = [
                "docs/visual-evidence/stage1a1/farm-establishing.jpg"
            ]
        if asset.id in COLD_METADATA:
            controls, preview, note = COLD_METADATA[asset.id]
            parameters.update({f"art_direction.{key}": SCENE_ART[key] for key in controls})
            restrictions.append(note)
            details["preview_evidence"] = [f"docs/visual-evidence/stage1c/{preview}"]
            details["integration_evidence"] = ["docs/visual-evidence/stage1c/cold-establishing.jpg"]
        if asset.id in WORLD_ASSETS or asset.id in PROPS or asset.id in EFFECTS:
            item = (WORLD_ASSETS | PROPS | EFFECTS)[asset.id]
            details.update(description=item.description, bounds=list(item.bounds))
            restrictions.extend((item.description, "Decorative artwork with no collision or navigation surface."))
        if asset.id in BUILDINGS:
            building = BUILDINGS[asset.id]
            details.update(
                description=building.description,
                variant_descriptions=dict(building.variants),
                bounds=list(building.bounds),
                doorway_reference_local=list(building.doorway),
            )
            parameters["transform.scale"] = {"type": "number", "minimum": 0.25, "maximum": 2}
            restrictions.extend((
                "Upright fixed three-quarter exterior. Ground origin is at the front foundation.",
                "Dusk Farm staging is demonstrated. Other placements need scene-specific review.",
                "Doorway reference is for staging. Openings and lighting are static.",
            ))
        if asset.id in (
            "abandoned_outpost_skyline_01", "abandoned_outpost_terrain_01",
            "forest_ravine_skyline_01", "forest_ravine_terrain_01",
            "outpost_watch_shelter_01", "ravine_fir_01",
        ):
            kit = "forest_ravine" if "ravine" in asset.id else "abandoned_outpost"
            details["integration_evidence"] = [
                f"docs/visual-evidence/sprint-d/{kit}-{mood}-720.png"
                for mood in frontier_art.MOODS[kit]
            ]
        if asset.id == "barn_01":
            parameters.update(
                {f"art_direction.{key}": SCENE_ART[key] for key in ("warmth", "atmosphere")}
            )
            restrictions.append(
                "Opt-in dusk_graded quiets fine seams; default retains original artwork."
            )
            restrictions.append("doorway_shadow adds one clipped local-time occlusion.")
            details["integration_evidence"] = ["docs/visual-evidence/stage0c/rowan-barn.jpg"]
        if asset.id == "beacon_01":
            details["interaction_sockets"] = {"activation_button_local": list(snowy.BEACON_SOCKET)}
            restrictions.append("ridge_surge adds a single local-frame 44–56 pulse.")
        if asset.id == "answer_light_01":
            restrictions.append("ridge_reveal is dark through local frame 23, then rises and holds.")
        yield component(
            asset.id,
            name,
            family,
            "character" if actor else "scene_asset",
            sources,
            registration=registration,
            variants=asset.variants,
            exposure="preset_only" if asset.id in planner_assets else "unavailable",
            parameters=parameters,
            restrictions=restrictions,
            dependencies=["scene-0.1"],
            details=details,
        )


def procedural_components():
    for family in contract.FAMILIES:
        yield component(
            family,
            family.replace("_", " ").title(),
            "composition",
            "procedural",
            [contract.validate_environment, compiler.compile_environment],
            parameters={
                "seed": {"type": "integer", "minimum": 0, "maximum": 2**32 - 1},
                "composition.density": {"type": "integer", "minimum": 1, "maximum": 3},
                "composition.path_alignment": {"type": "number", "minimum": -1, "maximum": 1},
                "composition.structure": {"type": "number", "minimum": 0, "maximum": 1},
                "composition.framing": {"type": "number", "minimum": 0, "maximum": 1},
                "composition.detail": {"choices": ["standard", "rich"]},
                "art_direction.lighting": {"choices": ["dusk", "overcast"]},
                "art_direction.atmosphere": SCENE_ART["atmosphere"],
                "rowan.enabled": {"type": "boolean"},
                "rowan.action": {"choices": ["idle", "look_around", "react"]},
                "rowan.side": {"choices": ["left", "right"]},
            },
            restrictions=[
                "Select through environment-0.1; generated scene IDs are local to the plan."
            ],
            dependencies=["environment-0.1"],
        )
    for recipe, (paths, operations) in planning.BOUNDS.items():
        yield component(
            f"procedural.{recipe}",
            ("Procedural crate and barrel" if recipe == "prop" else f"Procedural {recipe}"),
            RECIPE_FAMILIES.get(recipe, "nature"),
            "procedural",
            [getattr(recipes, recipe), recipes.geometry, planning.plan_environment],
            restrictions=[
                "Internal recipe selected by the environment family, not a scene asset ID."
            ],
            dependencies=["environment-0.1"],
            details={"budget": {"max_paths": paths, "max_operations": operations}},
        )


def system_components(views):
    if views - set(direction.BEHAVIORS):
        raise ValueError("Planner camera references disagree with runtime camera definitions")
    for key in scene.CAMERAS:
        yield component(
            f"camera.scene.{key}",
            key.replace("_", " ").title(),
            "composition",
            "system",
            [scene.validate_scene, graph.compile_scene],
            variants=[key],
            parameters={},
            restrictions=[
                "Scene-level camera preset; the planner uses storyboard direction overrides."
            ],
            dependencies=["scene-0.1"],
        )
    for key in direction.BEHAVIORS:
        lo, hi = direction.zoom_range(key)
        sources = [direction.compile_direction, direction.zoom_range]
        parameters = {"zoom": {"type": "number", "minimum": lo, "maximum": hi}}
        restrictions = ["Storyboard framing also constrains screen position, lead and offsets."]
        if key == "close_up":
            sources.append(character_staging.cinematic_character_staging)
            parameters["staging.character"] = {"choices": list(registry.blocking_character_ids())}
            parameters["staging.world"] = {"choices": list(character_staging.WORLDS)}
            restrictions.append(
                "Trusted cinematic_character_staging builder emits a validated direction-0.1 "
                "manifest over existing Stage 2A/2B performances. No planner selector."
            )
        yield component(
            f"camera.direction.{key}",
            key.replace("_", " ").title(),
            "composition",
            "system",
            sources,
            variants=[key],
            parameters=parameters,
            exposure="preset_only" if key in views else "unavailable",
            restrictions=restrictions,
            dependencies=["direction-0.1", "storyboard-0.1"],
        )
    yield component(
        "scene.art_direction",
        "Scene lighting and atmosphere",
        "lighting",
        "system",
        [scene.validate_scene, assets.recipe, polish.haze],
        parameters=SCENE_ART,
        exposure="preset_only",
        dependencies=["scene-0.1"],
        restrictions=[
            "Warmth, atmosphere and breeze affect supported recipes only. "
            "The planner sets them through fixed moods."
        ],
    )
    for key, definition in storylib.ENVIRONMENTS.items():
        yield component(
            key,
            definition["display"],
            "composition",
            "system",
            [storylib.build_shot],
            exposure="selectable",
            parameters={"environment": {"choices": [key]}},
            restrictions=["Keyword-selected environment assembled from fixed shot presets."],
            dependencies=["storyboard-0.1"],
        )


def inventory():
    planner_assets, views = planner_usage()
    entries = [
        *registered_components(planner_assets),
        *procedural_components(),
        *system_components(views),
    ]
    return {
        "schema_version": "visual-catalog-0.1",
        "components": sorted(entries, key=lambda entry: entry["id"]),
    }
