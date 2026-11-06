"""Bounded prop and atmospheric recipes for living-world scenes."""

import math

from reelforge.visual_library.architecture.buildings import box, plane
from reelforge.visual_library.world_assets import WorldAsset, oval, shadow, stroke


def parcel(variant):
    fill = "ae825c" if variant == "wrapped" else "768178"
    return [shadow(11), box(-10, -14, 20, 14, fill),
            plane("665c4c", (10, 0), (15, -5), (15, -18), (10, -14)),
            plane("cfb696", (-10, -14), (10, -14), (15, -18), (-5, -18)),
            box(-2, -14, 4, 14, "d4bb91"), box(2, -11, 5, 4, "ece0bf")]


def cart(variant, rotation=0):
    commands = [shadow(34), stroke("64564a", 4, (-22, -18), (-36, -37), (-51, -41)),
                plane("82634e", (-24,-26), (26,-26), (21,-11), (-19,-11)),
                box(-22, -25, 48, 4, "b69169")]
    if variant == "loaded":
        commands.extend([box(-15,-41,27,15,"9b805d"), box(-7,-41,5,15,"c7a776")])
    for x in (-15, 17):
        commands.extend([oval("36383b", x,-9,9,9), oval("847a66", x,-9,6,6)])
        for angle in (rotation, rotation + math.pi/2):
            dx, dy = 5 * math.cos(angle), 5 * math.sin(angle)
            commands.append(stroke("514e48", 1, (x-dx,-9-dy),(x+dx,-9+dy)))
        commands.append(oval("c0ac8b",x,-9,2,2))
    return commands


def creek(variant):
    return [plane("415653",(-220,9),(-134,-4),(-41,-14),(46,-10),(126,-25),(218,-27),
                  (220,-4),(130,3),(47,16),(-42,15),(-132,22),(-220,34)),
            plane("648287",(-220,14),(-136,0),(-39,-9),(47,-5),(128,-20),(220,-22),
                  (220,-7),(127,-1),(46,12),(-41,11),(-137,17),(-220,28)),
            stroke("a6b6a8",1.4,(-202,18),(-146,9),(-97,6)),
            stroke("8fa7a5",1.2,(-31,1),(13,3),(49,0)),
            stroke("a6b6a8",1.5,(99,-7),(151,-14),(199,-15))]


PROPS = {
    "parcel_01": WorldAsset("Travel parcel", "props", parcel, ("wrapped", "utility"),
                            (-12,-19,18,4), (10,65), True, "Centered base, top grasp at (0, -16)."),
    "handcart_01": WorldAsset("Handcart", "props", cart, ("empty", "loaded"),
                              (-54,-44,42,4), (19,100), True, "Grounded wheels and handle at (-51, -41)."),
    "creek_channel_01": WorldAsset("Creek channel", "nature", creek, ("stone_banks",),
                                   (-221,-29,221,35), (6,85), False, "Authored channel under a decorative span."),
}


def rain(variant, seconds):
    count, speed = {"light": (20, 156), "steady": (38, 220), "heavy": (62, 270)}[variant]
    commands = []
    for index in range(count):
        depth = .7 + .6 * (index % 3) / 2
        y = (index * 83 + seconds * speed * depth) % 645
        x = (index * 137 + seconds * 44 * depth) % 380 - 10
        commands.append(stroke("a2b8bf", .7 * depth, (x, y), (x-3*depth, y-12*depth)))
    return commands


def leaves(variant, seconds):
    count, speed = {"gentle": (7, 22), "gust": (15, 64), "autumn": (11, 32)}[variant]
    commands = []
    for index in range(count):
        phase = seconds * 3 + index * 1.3
        x = (index * 91 + seconds * speed) % 398 - 19
        y = 346 + index * 57 % 220 + math.sin(phase) * 13
        size = 3 + index % 4
        commands.append(plane("d5a45c" if variant == "autumn" else "a7a879",
                              (x-size,y), (x,y-size*.45), (x+size,y+math.cos(phase)*3),
                              (x,y+size*.34)))
    return commands


def smoke(variant, seconds):
    count, drift = {"thin": (3, 6), "rising": (6, 9), "windblown": (6, 38)}[variant]
    commands = []
    for index in range(count):
        u = (seconds * .53 + index / count) % 1
        commands.append(oval("b5bdaf", drift*u, -66*u, 5+13*u, 3+6*u,
                             .26 * math.sin(math.pi*u)))
    return commands


EFFECTS = {
    "rain_field_01": WorldAsset("Depth-layered rain", "effects", rain, ("light","steady","heavy"),
                                 (-20,-20,380,650), (62,124), False, "Animated in logical viewport units."),
    "wind_leaves_01": WorldAsset("Wind-blown leaves", "effects", leaves, ("gentle","gust","autumn"),
                                  (-27,320,391,594), (15,75), False, "Deterministic foliage drift over the midground."),
    "smoke_wisp_01": WorldAsset("Smoke wisps", "effects", smoke, ("thin","rising","windblown"),
                                 (-20,-78,57,10), (6,36), False, "Local emitter at the node origin."),
}


def sky(variant):
    from reelforge.environments.artwork import gradient
    from reelforge.rendering.diagnostic import color
    from reelforge.rendering.model import DrawPath, rectangle

    upper, lower, sun = {
        "daylight": ("597d98", "d4c9a7", "fff2c4"),
        "rainy_night": ("222e44", "64707b", "9aa8b5"),
    }[variant]
    return [DrawPath(rectangle(-100,-100,560,850),
                     gradient(color(upper), color(lower), 0, 435)),
            oval(sun, 90, 235, 13, 13, .82),
            oval(lower, 191, 175, 106, 8, .38),
            oval(lower, 242, 238, 67, 6, .29)]


PROPS["living_sky_01"] = WorldAsset(
    "Village sky grade", "nature", sky, ("daylight", "rainy_night"),
    (-100,-100,460,750), (4,24), False, "Authored sky grade for the Village Lane kit.",
)
