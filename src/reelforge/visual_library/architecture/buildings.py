"""Ground-anchored, left-keyed architecture for fixed three-quarter views."""

from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache

from reelforge.environments.artwork import gradient, line, polygon
from reelforge.rendering.diagnostic import color, ellipse
from reelforge.rendering.model import DrawPath, LinearGradient, rectangle


@dataclass(frozen=True)
class Building:
    name: str
    description: str
    variants: tuple[tuple[str, str], ...]
    draw: Callable[[str], tuple[DrawPath, ...]]
    doorway: tuple[int, int]
    bounds: tuple[int, int, int, int]
    budget: tuple[int, int]
    farm_variant: str


def plane(hex_color, *points, opacity=1):
    return polygon(points, color(hex_color, opacity))


def box(x, y, width, height, hex_color):
    return DrawPath(rectangle(x, y, width, height), color(hex_color))


def contact(width, reach):
    return [
        DrawPath(
            ellipse(22, -3, reach, 14),
            LinearGradient(
                (-width, 0), (22 + reach, 0),
                ((0, color("212b2a", 0.36)), (1, color("212b2a", 0))),
            ),
        ),
        DrawPath(ellipse(1, -1, width, 5), color("272d29", 0.44)),
    ]


def opening(x, y, width, height, *, lit=False, panes=True):
    """Recess, glazing, diagonal reflection and a heavy lower sill."""
    commands = [
        box(x - 3, y - 3, width + 6, height + 5, "433b39"),
        box(x, y, width, height, "e7ae64" if lit else "405963"),
        plane("ffe1a5" if lit else "9cb4b5",
              (x + 2, y + 2), (x + width - 2, y + 2),
              (x + 2, y + height - 5), opacity=0.53),
    ]
    if panes:
        commands += [
            box(x + width / 2 - 1, y, 2, height, "655245"),
            box(x, y + height / 2 - 1, width, 2, "655245"),
        ]
    return commands + [
        box(x - 5, y + height, width + 10, 3, "d0a986"),
        box(x - 3, y + height + 3, width + 6, 2, "58483e"),
    ]


def house(variant):
    dusk = variant == "dusk"
    worn = variant == "weathered"
    upper, lower, side, roof, edge = {
        "daylight": ("d9bb92", "b89577", "8a776c", "607276", "98a29b"),
        "dusk": ("bf9b77", "94735d", "696168", "4e5a6b", "8a8790"),
        "weathered": ("ada486", "797662", "626359", "62665f", "99927a"),
    }[variant]
    c = contact(76, 92)
    c += [
        plane("4d4948", (-78, -7), (68, -7), (111, -28), (111, -21), (68, 0), (-78, 0)),
        plane(side, (65, -4), (108, -25), (108, -116), (65, -94)),
        DrawPath(rectangle(-76, -94, 141, 89), gradient(color(upper), color(lower), -93, -4)),
        plane(upper, (-76, -94), (-6, -150), (65, -94)),
        plane("4d4847", (27, -129), (27, -158), (40, -165), (40, -136)),
        plane("97715c", (15, -127), (15, -158), (27, -158), (27, -127)),
        plane("be9376", (12, -159), (27, -159), (42, -166), (27, -166)),
        plane(roof, (-6, -154), (39, -177), (115, -119), (70, -96)),
        plane(edge, (-6, -154), (39, -177), (43, -174), (-6, -151)),
        plane("463d3c", (-86, -93), (-6, -156), (73, -94), (70, -88),
              (-6, -147), (-82, -88)),
        line(((-82, -94), (-6, -153), (69, -94), (114, -117)), color(edge), 2),
        box(-75, -93, 5, 87, "d2ad87"),
        box(59, -93, 6, 87, "a78870"),
        box(-70, -90, 129, 4, "554239"),
    ]
    for y in (-76, -64, -52, -40, -28, -16):
        c += [
            line(((-70, y), (59, y)), color("5e5046", 0.28)),
            line(((65, y), (107, y - 21)), color("443f45", 0.35)),
        ]
    for step in (0.25, 0.48, 0.70):
        x, y = -6 + 76 * step, -154 + 58 * step
        c.append(line(((x, y), (x + 45, y - 23)), color(edge, 0.48)))
    c += opening(-16, -121, 19, 13, lit=False, panes=False)
    c += opening(-61, -72, 32, 35, lit=dusk)
    c += opening(27, -72, 23, 31, lit=dusk)
    c += [
        plane("3e4547", (78, -77), (96, -86), (96, -56), (78, -47)),
        plane("b49d83", (76, -47), (98, -58), (98, -54), (76, -43)),
        box(-14, -84, 34, 79, "544038"),
        box(-9, -80, 24, 75, "87614d" if worn else "526661"),
        box(-6, -75, 18, 27, "dba665" if dusk else "38494a"),
        box(8, -41, 3, 3, "d4af71"),
        plane("c29b78", (-19, -5), (23, -5), (29, 0), (-24, 0)),
        plane("685447", (-19, -87), (17, -87), (29, -79), (-28, -79)),
        line(((-28, -79), (29, -79)), color("ba9476"), 2),
    ]
    if worn:
        c += [
            plane("78634f", (-68, -69), (-23, -49), (-23, -44), (-68, -64)),
            plane("a88e6d", (23, -41), (54, -65), (54, -61), (23, -36)),
            plane("6a6b50", (-74, -8), (-74, -27), (-59, -24), (-57, -15), (-37, -9)),
            plane("808268", (41, -118), (53, -117), (62, -121), (79, -120), (55, -108)),
            line(((35, -30), (40, -26), (39, -21), (49, -17)), color("57534a"), 2),
        ]
    return tuple(c)


def storefront(variant):
    open_shop = variant == "open"
    worn = variant == "weathered"
    wall, return_wall, cloth, stripe = {
        "open": ("bd987a", "6a6462", "a36249", "dfb88b"),
        "closed": ("b59a80", "67646a", "536f70", "a5b1a1"),
        "weathered": ("a99e82", "656759", "75694f", "b4a37c"),
    }[variant]
    c = contact(90, 105)
    c += [
        plane("474441", (-88, -6), (78, -6), (116, -26), (116, -19), (78, 0), (-88, 0)),
        plane(return_wall, (77, -5), (116, -25), (116, -122), (77, -102)),
        DrawPath(rectangle(-86, -106, 163, 101),
                 gradient(color(wall), color("8a7364"), -106, -3)),
        plane("586165", (-89, -108), (77, -108), (120, -130), (-46, -130)),
        plane("484849", (77, -108), (120, -130), (120, -122), (77, -100)),
        box(-89, -108, 166, 7, "6e5749"),
        line(((-88, -109), (76, -109), (119, -131)), color("c5a384"), 2),
        box(-71, -97, 132, 18, "574841"),
        box(-68, -95, 126, 13, "caa985" if open_shop else "a99780"),
        # A painted emblem and decorative rules read as a sign without simulated text.
        plane("674c3e", (-8, -90), (-2, -95), (4, -90), (-2, -85)),
        box(-45, -90, 30, 2, "8a6f5a"),
        box(12, -90, 30, 2, "8a6f5a"),
        plane("4a4e4c", (88, -75), (105, -83), (105, -53), (88, -45)),
        plane("9b8e7d", (86, -45), (107, -55), (107, -51), (86, -41)),
        box(-75, -78, 141, 72, "4d4240"),
    ]
    if open_shop:
        c += opening(-65, -67, 68, 43, lit=True)
        c += [
            box(-61, -39, 25, 11, "af7956"), box(-52, -47, 9, 9, "956249"),
            box(-24, -37, 19, 9, "987755"), box(-20, -47, 10, 10, "c18c5d"),
            box(20, -76, 33, 69, "302e32"), box(24, -72, 23, 61, "514044"),
            box(26, -69, 19, 4, "b98658"),
        ]
    else:
        c += [
            box(-67, -68, 74, 51, "706f67" if worn else "687b80"),
            box(19, -77, 36, 71, "635746"),
            box(24, -73, 26, 67, "85816b" if worn else "4c6266"),
            box(43, -39, 3, 3, "c4a470"),
        ]
        for y in range(-64, -16, 6):
            c.append(box(-66, y, 72, 1.5, "4a5353"))
        if worn:
            c += [
                plane("926f53", (-69, -59), (12, -30), (10, -24), (-70, -52)),
                plane("b29570", (19, -46), (55, -60), (55, -54), (19, -39)),
                plane("6a6c51", (-86, -5), (-86, -29), (-80, -18), (-66, -10), (-57, -5)),
            ]
    c += [
        box(-83, -78, 7, 73, "a9886f"),
        box(67, -78, 8, 73, "8f7564"),
        plane("b09175", (-76, -6), (66, -6), (74, 0), (-84, 0)),
        plane(cloth, (-79, -81), (67, -81), (78, -67), (-92, -67)),
    ]
    for i in range(6 if not worn else 5):
        x = -77 + i * 25
        c.append(plane(stripe, (x, -81), (x + 9, -81),
                       (-89 + i * 29 + 11, -67), (-89 + i * 29, -67)))
    c += [
        plane("66514a" if worn else cloth, (-92, -67), (78, -67), (77, -62),
              (56, -61), (-18, -62), (-53, -60 if worn else -62), (-91, -62)),
        line(((-92, -67), (78, -67)), color(stripe), 1.1),
    ]
    return tuple(c)


BUILDINGS = {
    "house_01": Building(
        "Gable cottage", "A timber cottage with a slate roof, chimney and recessed entry.",
        (("daylight", "Clear glass and warm siding"),
         ("dusk", "Lit windows and cool slate fill"),
         ("weathered", "Boarded windows, moss and worn siding")),
        house, (3, 0), (-87, -179, 116, 14), (80, 480), "dusk",
    ),
    "shop_01": Building(
        "Wayside storefront", "A low roadside shop with a striped awning and a display bay.",
        (("open", "Lit display bay and recessed open-looking entry"),
         ("closed", "Metal roller shutter and closed door"),
         ("weathered", "Boarded shutters, worn awning and moss")),
        storefront, (37, 0), (-92, -132, 128, 14), (80, 480), "open",
    ),
}


@lru_cache(maxsize=6)
def draw_building(asset_id, variant):
    building = BUILDINGS[asset_id]
    if variant not in dict(building.variants):
        raise ValueError(f"Unknown {asset_id} variant: {variant}")
    return building.draw(variant)
