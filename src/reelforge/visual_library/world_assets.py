"""Bounded, authored roadside artwork in the scene's local coordinate system."""

from dataclasses import dataclass
from collections.abc import Callable
from functools import lru_cache

from reelforge.environments.artwork import gradient, line
from reelforge.rendering.diagnostic import color, ellipse
from reelforge.rendering.model import DrawPath
from reelforge.visual_library.architecture.buildings import box, plane


def stroke(tint, width, *points):
    return line(points, color(tint), width)


def oval(tint, x, y, rx, ry, opacity=1):
    return DrawPath(ellipse(x, y, rx, ry), color(tint, opacity))


def shadow(width):
    return oval("202a27", 6, -1, width, 4, .32)


def road(variant):
    edge, fill, detail = {
        "packed_dirt": ("77644d", "ac8863", "c3a080"),
        "worn_asphalt": ("68645b", "55575a", "b9a67f"),
        "cobblestone": ("5f5955", "79726a", "aaa093"),
    }[variant]
    commands = [
        plane(edge, (-111, 2), (110, 2), (34, -117), (-23, -117)),
        plane(fill, (-103, 0), (101, 0), (31, -117), (-20, -117)),
        stroke(detail, 1.5, (-99, 0), (-18, -116)),
        stroke(detail, 1.5, (95, 0), (30, -116)),
    ]
    for y in (-97, -81, -60, -34, -9):
        width = 25 + (117 + y) * .62
        if variant == "cobblestone":
            commands.append(stroke(edge, 1.4, (-width, y), (width, y)))
            for offset in (-.6, -.2, .2, .6):
                x = offset * width
                commands.append(stroke(edge, 1.1, (x, y), (x + 4, y - 8)))
        elif variant == "worn_asphalt":
            commands.append(stroke(detail, 2, (3, y), (4, y - 7)))
            commands.append(stroke("42474a", 1, (-width * .7, y), (-width * .48, y - 2), (-width * .4, y + 2)))
        else:
            commands.extend(stroke(detail, 1.6, (x, y), (x + 7, y - 2)) for x in (-width * .58, width * .48))
    return commands


def junction(variant):
    outline = [(-112, -36), (-36, -36), (-21, -113), (24, -113),
               (40, -36), (112, -36), (112, -10), (54, -10)]
    if variant == "crossroads":
        outline += [(67, 25), (-65, 25), (-51, -10)]
    outline += [(-112, -10)]
    return [plane("847668", *[(x, y + 3) for x, y in outline]),
            plane("626364", *outline),
            stroke("c4ae83", 1.7, (-104, -23), (-57, -23)),
            stroke("c4ae83", 1.7, (62, -23), (104, -23)),
            stroke("a89777", 1.5, (1, -102), (2, -76)),
            stroke("a89777", 1.5, (3, -66), (4, -49))]


def sidewalk(variant):
    fill = {"stone": "ad9b87", "concrete": "c5b9a7", "cracked": "a59b88"}[variant]
    commands = [plane("665d56", (-104, -10), (74, -10), (108, -28), (108, -19), (74, 0), (-104, 0)),
                plane(fill, (-104, -10), (74, -10), (108, -28), (-70, -28)),
                stroke("ddd0b7", 1.5, (-103, -10), (74, -10), (106, -27))]
    step = 23 if variant == "stone" else 46
    for x in range(-83, 72, step):
        commands.append(stroke("817668", 1, (x, -11), (x + 30, -27)))
    if variant == "stone":
        commands.append(stroke("817668", 1, (-87, -19), (90, -19)))
    if variant == "cracked":
        commands.append(stroke("645c53", 1.4, (-13, -11), (-8, -16), (-14, -21), (-3, -27)))
    return commands


def bridge(variant):
    worn = variant == "weathered"
    deck = "8b7c62" if worn else "b58a61"
    commands = [shadow(89)]
    for x, y in ((-62, 0), (61, 0), (-33, -50), (42, -50)):
        commands.extend([box(x, y - 17, 7, 17, "594c40"),
                         box(x, y - 17, 2, 15, "917558")])
    commands += [
        plane("684f3c", (-69, -10), (69, -10), (69, -2), (-69, -2)),
        plane(deck, (-69, -10), (69, -10), (49, -62), (-35, -62)),
    ]
    for y in (-18, -27, -36, -45, -54):
        fraction = (-10 - y) / 52
        commands.append(stroke("715945", 1, (-68 + 33 * fraction, y),
                               (68 - 19 * fraction, y)))
    for near, far in ((-64, -33), (64, 46)):
        for fraction in (0, .5, 1):
            x = near + (far - near) * fraction
            y = -10 - 52 * fraction
            height = 23 - 7 * fraction
            commands.append(box(x - 2, y - height, 5, height, "78614c"))
        commands.append(stroke("9b7c5d" if worn else "c09971", 4,
                               (near, -33), (far, -78)))
    if worn:
        commands.extend([stroke("5b5846", 1.5, (-37, -25), (-17, -24), (-10, -26)),
                         stroke("655344", 1, (24, -42), (31, -45), (29, -48))])
    return commands


def tree(variant):
    lean = 31 if variant == "leaning" else -5
    autumn = variant == "autumn"
    dark, mid, light = ("80543f", "b27143", "d49b55") if autumn else ("40584c", "5e7753", "82925d")
    commands = [shadow(34),
                plane("645043", (-13, 0), (-7, -41), (lean - 6, -91), (lean + 7, -92), (8, -34), (13, 0)),
                plane("8d6d52", (-12, -1), (-4, -50), (lean - 4, -85), (lean, -78), (2, -39), (-4, -4)),
                stroke("6d5545", 7, (1, -46), (lean - 23, -84), (lean - 36, -99)),
                stroke("6d5545", 6, (lean, -58), (lean + 30, -90))]
    for x, y, rx, ry in ((-30,-98,28,20),(30,-103,33,23),(-8,-122,41,27),(14,-112,35,27)):
        x += lean
        commands.extend([oval(dark, x, y + 4, rx, ry), oval(mid, x - 4, y - 2, rx - 3, ry - 3)])
    commands.extend([oval(light, lean - 24, -127, 22, 12, .65),
                     oval(light, lean + 5, -138, 22, 11, .55)])
    return commands


def shrubs(variant):
    commands = [shadow(58)]
    masses = ((-40,-11,19,12),(-20,-19,22,18),(7,-16,29,16),(35,-11,18,12))
    if variant == "sparse":
        masses = ((-36,-8,16,9),(-9,-14,15,13),(24,-9,15,9))
        commands.append(stroke("786553", 2, (-23, -2), (-19, -16), (-26, -21)))
    for x, y, rx, ry in masses:
        commands.extend([oval("425948",x,y,rx,ry), oval("647c52",x-3,y-4,rx-4,ry-4),
                         oval("889463",x-5,y-7,rx*.46,ry*.28)])
    return commands


def rocks(variant):
    commands = [shadow(49)]
    for x, y, s in ((15,-6,.85),(-16,0,1),(32,0,.5)):
        if variant == "rounded":
            commands.extend([oval("575c59",x,y-10*s,23*s,12*s),
                             oval("8b8d7e",x-4*s,y-14*s,17*s,8*s),
                             oval("aba798",x-8*s,y-17*s,9*s,4*s)])
        else:
            commands.extend([
                plane("686d66",(x-21*s,y),(x-24*s,y-13*s),(x-6*s,y-26*s),(x+15*s,y-23*s),(x+22*s,y-6*s),(x+16*s,y)),
                plane("a1a091",(x-24*s,y-13*s),(x-6*s,y-26*s),(x+15*s,y-23*s),(x+3*s,y-12*s)),
                plane("525b59",(x+3*s,y-12*s),(x+15*s,y-23*s),(x+22*s,y-6*s),(x+16*s,y),(x-2*s,y)),
            ])
    return commands


def lamp(variant):
    lit = variant == "lit"
    commands = [shadow(15), box(-8,-7,16,7,"54564d"), box(-4,-105,7,98,"464c47"),
                box(-3,-101,2,89,"8c8870"), box(-7,-15,13,9,"666859"),
                plane("4b4b44",(-13,-105),(12,-105),(9,-127),(-10,-127)),
                plane("f1bd70" if lit else "647273",(-9,-109),(8,-109),(6,-124),(-7,-124)),
                plane("525048",(-15,-126),(14,-126),(8,-133),(0,-137),(-8,-133))]
    if lit:
        for radius, alpha in ((24,.045),(18,.08),(12,.13)):
            commands.insert(1,oval("ffca72",0,-117,radius,radius,alpha))
    if variant == "weathered":
        commands.extend([stroke("9c7151",2,(-2,-11),(-1,-24)),stroke("987459",1,(-12,-126),(-7,-128))])
    return commands


def bench(variant):
    trim = {"timber":"b18664","painted":"71877a","weathered":"918069"}[variant]
    commands = [shadow(48)]
    for x in (-38,31):
        commands.extend([box(x,-44,5,38,"5d554b"),box(x-7,-22,5,22,"514b42")])
    commands.extend([box(-46,-43,88,8,trim),box(-46,-33,88,7,trim),
                     plane(trim,(-53,-19),(39,-19),(48,-25),(-44,-25)),
                     box(-53,-19,92,4,"74604e"),
                     stroke("c1ab88",1,(-51,-19),(37,-19),(46,-24))])
    if variant == "weathered":
        commands.extend([stroke("645d51",1,(-42,-40),(-20,-40),(-12,-37)),
                         stroke("746b5a",1,(6,-30),(30,-29))])
    return commands


def crates(variant):
    commands = [shadow(52)]
    top = (7,-28) if variant == "neat" else (16,-28)
    for x,y,w,h in ((-38,0,43,29),(6,0,35,28),(*top,28,22)):
        commands.extend([
            box(x,y-h,w,h,"a17856"),
            plane("755a47",(x+w,y),(x+w+9,y-7),(x+w+9,y-h-7),(x+w,y-h)),
            plane("c09b72",(x,y-h),(x+w,y-h),(x+w+9,y-h-7),(x+9,y-h-7)),
            stroke("715640",1,(x,y-h/2),(x+w,y-h/2)),
            stroke("c09b72",3,(x+3,y-2),(x+w-3,y-h+2)),
            box(x,y-h,3,h,"c39b72"),box(x+w-3,y-h,3,h,"856248"),
        ])
    return commands


def sign(variant):
    commands = [shadow(13),box(-4,-79,8,79,"755c46"),box(-4,-77,2,74,"a4825e")]
    if variant == "blank":
        commands.append(box(-29,-69,58,19,"b4926c"))
    else:
        commands.append(plane("a88c65",(-33,-71),(18,-71),(37,-62),(18,-52),(-33,-52)))
        commands.append(stroke("d7b891",1,(-30,-70),(17,-70),(32,-62)))
    commands.extend([oval("665345",-2,-62,1.6,1.6),oval("665345",3,-62,1.6,1.6)])
    if variant == "weathered":
        commands.append(stroke("6d604c",1.4,(-31,-64),(-20,-63),(-16,-58),(4,-58)))
    return commands


def mist(variant):
    opacity = .22 if variant == "dense" else .12
    return [
        DrawPath(ellipse(x, y, rx, ry),
                 gradient(color("a5aca5", 0), color("b7c0b6", opacity), y-ry, y+ry))
        for x,y,rx,ry in ((-37,-13,62,9),(26,-8,63,8),(0,-4,91,7))
    ]


@dataclass(frozen=True)
class WorldAsset:
    name: str
    family: str
    draw: Callable
    variants: tuple[str, ...]
    bounds: tuple[int, int, int, int]
    budget: tuple[int, int]
    upright: bool
    description: str


WORLD_ASSETS = {
    "road_surface_01": WorldAsset("Tapered road", "infrastructure", road, ("packed_dirt","worn_asphalt","cobblestone"), (-112,-118,112,3),(32,190),False,"Near edge at origin, receding toward y=-117. Dirt tracks, worn lane paint or paving joints."),
    "road_junction_01": WorldAsset("Road junction", "infrastructure", junction, ("t_junction","crossroads"),(-114,-114,114,29),(8,55),False,"Decorative intersecting carriageways. The crossroads opens a second stem toward the camera."),
    "sidewalk_01": WorldAsset("Raised sidewalk", "infrastructure", sidewalk, ("stone","concrete","cracked"),(-105,-29,109,1),(14,75),False,"Near curb at y=0, with flagstones, concrete slabs or a split slab."),
    "small_bridge_01": WorldAsset("Small footbridge", "infrastructure", bridge, ("timber","weathered"),(-85,-81,98,5),(30,165),True,"Low timber span with deck, posts and two rails. Decorative only."),
    "deciduous_tree_01": WorldAsset("Deciduous tree", "nature", tree, ("broad","leaning","autumn"),(-70,-151,100,5),(18,120),True,"Layered canopy with an offset trunk and branch structure. Autumn uses ochre foliage."),
    "shrub_cluster_01": WorldAsset("Shrub cluster", "nature", shrubs, ("lush","sparse"),(-60,-40,65,5),(15,100),True,"Overlapping foliage masses with an open, twigged silhouette in sparse form."),
    "rock_group_01": WorldAsset("Rock group", "nature", rocks, ("rounded","angular"),(-50,-34,56,5),(12,90),True,"Three grounded stones with rounded highlights or broken planar facets."),
    "streetlamp_01": WorldAsset("Roadside streetlamp", "props", lamp, ("unlit","lit","weathered"),(-26,-143,27,5),(14,100),True,"Metal lamp with localized authored glow. It does not light other assets."),
    "bench_01": WorldAsset("Slatted bench", "props", bench, ("timber","painted","weathered"),(-55,-46,56,5),(14,85),True,"Grounded supports and visible seat plane. No sitting interaction."),
    "crate_stack_01": WorldAsset("Crate stack", "props", crates, ("neat","uneven"),(-47,-58,58,5),(25,140),True,"Braced timber boxes with either a square or shifted upper crate."),
    "signpost_01": WorldAsset("Roadside signpost", "props", sign, ("blank","directional","weathered"),(-35,-80,39,5),(8,55),True,"Blank board or directional silhouette, with worn timber in the weathered option."),
    "ground_mist_01": WorldAsset("Ground mist", "effects", mist, ("thin","dense"),(-100,-23,92,5),(3,21),False,"Static low transparent bands. Set painter order explicitly and keep below faces."),
}


@lru_cache(maxsize=32)
def draw_world_asset(identity, variant):
    asset = WORLD_ASSETS[identity]
    if variant not in asset.variants:
        raise ValueError(f"Unknown {identity} variant: {variant}")
    return tuple(asset.draw(variant))
