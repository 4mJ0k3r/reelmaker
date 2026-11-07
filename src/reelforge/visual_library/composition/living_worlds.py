"""Trusted, native-free world kit builders producing complete scene-0.1 data."""

from reelforge.characters.living import PROFILES
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene
from reelforge.visual_library.frontier_art import MOODS
from reelforge.visual_library.composition.farm import farm_manifest, transform

WORLD_KITS = {
    "village_lane": ("daylight", "evening", "rainy_night"),
    "woodland_creek": ("clear", "misty", "windy"),
}


LEGACY_WORLD_KITS = dict(WORLD_KITS)
WORLD_KITS.update(MOODS)


def node(name, parent, order, identity, variant, x, y, scale=1, *, kind="asset", **fields):
    return dict(id=name, kind=kind, parent=parent, order=order, visible=True,
                transform=transform(x, y, scale), asset_id=identity, variant=variant, **fields)


def world_manifest(kit, mood, *, actor=None, action="idle", expression="neutral", frames=90):
    if kit not in WORLD_KITS or mood not in WORLD_KITS[kit]:
        raise ValueError("Choose a registered world and mood")
    if actor is not None and actor not in PROFILES and actor != "rowan_01":
        raise ValueError("Choose Scout, Mechanic or Rowan")
    scene = farm_manifest()
    scene.update(title=f"{kit.replace('_', ' ').title()} — {mood}", camera="gentle_drift")
    scene["output"]["frames"] = frames
    scene["art_direction"].update(warmth=.24 if mood == "rainy_night" else .72,
                                  atmosphere=.72 if mood in ("misty", "rainy_night") else .35)
    nodes = [n for n in scene["nodes"] if n["kind"] in {"root","layer","background","environment"}]
    if kit == "village_lane":
        if mood != "evening":
            nodes.append(node("grade","sky_plane",1,"living_sky_01",mood,0,0))
        nodes.extend([
            node("lane","terrain",3,"road_surface_01","worn_asphalt",113,660,1.7),
            node("curb","terrain",4,"sidewalk_01","stone",256,518,.8),
            node("cottage","midground",1,"house_01","daylight" if mood == "daylight" else "dusk",94,449,.66),
            node("shop","midground",2,"shop_01","closed" if mood == "daylight" else "open",256,504,.83),
            node("streetlamp","midground",4,"streetlamp_01","unlit" if mood == "daylight" else "lit",185,526,.64),
            node("shop_bench","midground",5,"bench_01","painted",286,536,.65),
            node("side_tree","midground",0,"deciduous_tree_01","broad",12,481,.81),
            node("shop_shrubs","midground",3,"shrub_cluster_01","lush",335,502,.6),
            node("sign","foreground",0,"signpost_01","directional",31,607,.69),
        ])
        if mood == "rainy_night":
            nodes.append(node("rain","foreground",3,"rain_field_01","steady",0,0))
    elif kit in MOODS:
        nodes = [n for n in nodes if n["kind"] in {"root", "layer"}]
        nodes.extend(_frontier_nodes(kit, mood))
    else:
        nodes.extend([
            node("approach","terrain",2,"road_surface_01","packed_dirt",173,662,1.27),
            node("channel","terrain",3,"creek_channel_01","stone_banks",180,513),
            node("left_tree","midground",0,"deciduous_tree_01","leaning",36,518,1.12),
            node("right_tree","midground",1,"deciduous_tree_01","autumn",296,480,.92),
            node("bank_shrubs","midground",2,"shrub_cluster_01","lush",288,499,.83),
            node("span","midground",3,"small_bridge_01","weathered",174,556,1.05),
            node("bank_rocks","midground",4,"rock_group_01","angular",71,541,.8),
            node("sign","midground",5,"signpost_01","weathered",283,559,.68),
            node("front_shrubs","foreground",2,"shrub_cluster_01","sparse",342,620,1.2),
        ])
        if mood == "misty":
            nodes.append(node("mist","foreground",1,"ground_mist_01","thin",157,611,1.5))
        if mood == "windy":
            nodes.append(node("leaf_drift","foreground",1,"wind_leaves_01","gust",0,0))
    if actor is not None:
        info = dict(character=actor, action=action, expression=expression)
        if actor == "rowan_01":
            info = dict(character=actor, action="idle", expression="concerned",
                        direction="right", speed=1.0, intensity=1.0)
            if action != "idle" or expression != "neutral":
                raise ValueError("The kit admits Rowan's default stationary pose")
        nodes.append(node("actor","midground",9,actor,"default",99,581,
                          .46 if actor == "rowan_01" else .78,
                          kind="character", ground_id="ground", character=info))
    scene["nodes"] = nodes
    compile_scene(validate_scene(scene))
    return scene


def _frontier_nodes(kit, mood):
    ground = [
        node("sky", "sky_plane", 0, f"{kit}_skyline_01", mood, 0, 0, kind="background"),
        node("ground", "terrain", 0, f"{kit}_terrain_01", mood, 0, 0, kind="environment"),
    ]
    if kit == "abandoned_outpost":
        ground.extend((
            node("shelter", "midground", 3, "outpost_watch_shelter_01", mood, 246, 511, .91),
            node("streetlamp", "midground", 4, "streetlamp_01",
                 "unlit" if mood == "daylight" else "lit", 237, 546, .85),
            node("fence", "midground", 2, "fence_01", "default", 65, 487, .75),
            node("stone", "foreground", 1, "rock_group_01", "angular", 361, 605, 1.28),
            node("scrub", "foreground", 2, "shrub_cluster_01", "sparse", 15, 622, 1.2),
        ))
        if mood == "storm":
            ground.append(node("rain", "foreground", 3, "rain_field_01", "steady", 0, 0))
        if mood == "sunset":
            ground.append(node("dust", "terrain", 5, "smoke_wisp_01", "windblown", 89, 507, .72))
    else:
        ground.extend((
            node("fir_left", "midground", 1, "ravine_fir_01", "bank", 41, 515, .87),
            node("fir_right", "midground", 2, "ravine_fir_01", "edge", 323, 499, 1.05),
            node("strata", "midground", 3, "rock_group_01", "angular", 57, 544, 1.4),
            node("bough", "foreground", 2, "ravine_fir_01", "edge", 367, 591, 1.27),
            node("shrub", "foreground", 3, "shrub_cluster_01", "sparse", -2, 621, 1.28),
        ))
        if mood != "morning":
            ground.append(node("mist", "terrain", 5, "ground_mist_01", "thin", 102, 548, 1.5))
        else:
            ground.append(node("leaves", "foreground", 5, "wind_leaves_01", "gentle", 0, 0))
    return ground
