"""Authored panorama and supporting terrain for the two frontier kits."""

from functools import lru_cache

from reelforge.rendering.diagnostic import color
from reelforge.rendering.model import DrawPath, LinearGradient, rectangle
from reelforge.visual_library.architecture.buildings import box, opening, plane
from reelforge.visual_library.world_assets import oval, stroke

MOODS = {
    "abandoned_outpost": ("daylight", "sunset", "storm"),
    "forest_ravine": ("morning", "misty", "night"),
}
# Zenith, horizon, distant ridge, near ridge, terrain, route, route edge.
PALETTES = {
    "daylight": ("536f89", "d8bb91", "949092", "636b73", "686756", "a59a81", "c1b196"),
    "sunset": ("343852", "eab183", "9b777b", "625766", "594d4b", "84736e", "b1947a"),
    "storm": ("27374c", "85959a", "75818a", "495c68", "465059", "727d80", "a1a8a3"),
    "morning": ("526e81", "dbc9a1", "8a9c94", "546c62", "3c534a", "8b8a69", "a4ab80"),
    "misty": ("506777", "c0cecb", "92a7a6", "657e78", "45605c", "83958b", "abb4a0"),
    "night": ("17283e", "657c89", "4d6471", "314957", "263e43", "627474", "859597"),
}
SUPPORT = (-180, 535, 540, 790)


def _pine(x, floor, height, paint):
    width = height * .24
    return plane(paint, (x - 2, floor), (x - 3, floor - 15),
                 (x - width, floor - 13), (x - width * .61, floor - height * .48),
                 (x - width * .42, floor - height * .52), (x, floor - height),
                 (x + width * .45, floor - height * .53), (x + width * .63, floor - height * .46),
                 (x + width, floor - 11), (x + 3, floor - 14), (x + 2, floor))


@lru_cache(maxsize=12)
def skyline(kit, mood):
    top, horizon, distant, near, *_ = PALETTES[mood]
    art = [DrawPath(rectangle(-460, -380, 1280, 1510), LinearGradient(
        (0, 20), (0, 400), ((0, color(top)), (1, color(horizon)))
    ))]
    if mood in ("daylight", "sunset", "morning", "night"):
        x, y, radius = (237, 132, 26) if kit == "abandoned_outpost" else (158, 184, 19)
        art.extend((oval(horizon, x, y, radius * 1.8, radius * 1.8, .32),
                    oval("f4daba" if mood != "night" else "d7e6dc", x, y, radius, radius)))
    if kit == "abandoned_outpost":
        art.extend((
            plane(distant, (-460, 355), (-36, 304), (58, 318), (124, 258), (188, 268),
                  (230, 302), (317, 289), (420, 349), (820, 339), (820, 860), (-460, 860)),
            plane(near, (-460, 407), (-46, 361), (42, 343), (103, 350), (185, 394),
                  (245, 355), (340, 344), (425, 371), (820, 403), (820, 860), (-460, 860)),
            stroke(near, 3, (126, 280), (126, 218)),
            stroke(near, 2, (106, 235), (145, 235)),
            stroke(near, 2, (115, 253), (137, 253)),
        ))
    else:
        art.extend((
            plane(distant, (-460, 312), (-90, 264), (53, 308), (98, 262), (155, 221),
                  (182, 244), (203, 209), (243, 285), (391, 345), (820, 262),
                  (820, 860), (-460, 860)),
            plane(near, (-460, 410), (-38, 338), (78, 383), (154, 414), (239, 366),
                  (377, 312), (820, 372), (820, 860), (-460, 860)),
        ))
        art.extend(_pine(x, 391 + x % 27, 44 + (i * 29) % 54, near)
                   for i, x in enumerate(range(-150, 540, 23)))
    return tuple(art)


@lru_cache(maxsize=12)
def terrain(kit, mood):
    _, _, distant, near, ground, route, edge = PALETTES[mood]
    art = [box(-510, 398, 1390, 705, ground)]
    if kit == "abandoned_outpost":
        art.extend((
            plane(near, (-510, 419), (28, 426), (117, 468), (164, 437), (356, 410),
                  (870, 450), (870, 398), (-510, 398)),
            plane(edge, (162, 403), (177, 405), (142, 464), (151, 499), (275, 546),
                  (582, 905), (-317, 990), (-106, 730), (42, 560), (102, 492), (112, 459)),
            plane(route, (165, 407), (175, 408), (146, 465), (156, 492), (270, 543),
                  (556, 905), (-286, 990), (-91, 730), (51, 560), (110, 491), (116, 458)),
        ))
        for y, x, half in ((476, 127, 1), (512, 144, 2), (555, 179, 3), (618, 211, 4),
                           (714, 242, 5), (838, 283, 7)):
            art.append(plane(edge, (x-half, y), (x+half, y), (x+half+5, y+10),
                             (x-half+2, y+10), opacity=.64))
    else:
        art.extend((
            plane(near, (-510, 398), (-36, 403), (59, 451), (158, 438), (280, 407),
                  (870, 398), (870, 479), (271, 495), (140, 472), (-510, 515)),
            plane("263d46", (-510, 488), (-52, 497), (126, 478), (207, 452), (268, 455),
                  (233, 493), (99, 531), (-510, 748)),
            plane("547b86", (-510, 511), (-42, 505), (137, 482), (230, 455), (252, 459),
                  (215, 484), (81, 519), (-510, 708)),
            plane(edge, (252, 472), (287, 473), (249, 521), (250, 546), (389, 577),
                  (702, 971), (-270, 970), (-10, 665), (125, 566), (214, 524)),
            plane(route, (258, 476), (279, 476), (244, 522), (247, 550), (381, 584),
                  (676, 971), (-240, 970), (2, 672), (133, 570), (223, 523)),
        ))
        for y, x, length in ((493, 42, 65), (511, -19, 52), (479, 162, 38), (466, 200, 25)):
            art.append(stroke("9ebec0", 1.3, (x, y), (x + length, y - 3)))
    # Low-contrast stones and grit. Positions are deterministic and extend beyond the crop.
    for i in range(32):
        x, y = -145 + (i * 97) % 640, 460 + (i * 67) % 401
        size = 2 + (y - 460) * .011
        art.append(oval(distant if i % 3 == 0 else near, x, y, size * 2, size * .48, .52))
    return tuple(art)


@lru_cache(maxsize=3)
def watch_shelter(mood):
    practical = mood != "daylight"
    return (
        oval("272e33", 8, 0, 73, 11, .46),
        plane("423a38", (-41, -81), (-33, -82), (-33, 0), (-41, 0)),
        plane("554843", (30, -85), (39, -82), (39, 0), (30, 0)),
        stroke("62524b", 5, (-37, -16), (34, -74)),
        stroke("4e433f", 4, (-37, -74), (32, -18)),
        plane("303741", (-61, -157), (28, -167), (60, -154), (43, -143), (-57, -139)),
        plane("71625a", (-54, -145), (35, -151), (35, -76), (-54, -70)),
        plane("51494c", (35, -151), (55, -145), (55, -86), (35, -76)),
        *opening(-36, -132, 34, 30, lit=practical),
        *opening(7, -136, 20, 30, lit=False),
        *(stroke("8d796a", 1.5, (-51, y), (30, y - 5)) for y in (-97, -89, -81)),
        stroke("303840", 4, (49, -82), (55, -5)),
        stroke("303840", 4, (64, -87), (73, -10)),
        *(stroke("665b55", 3, (x, y), (x + 16, y - 4))
          for x, y in ((52, -63), (53, -47), (54, -31), (55, -15))),
        stroke("4d565a", 2, (16, -160), (12, -199), (32, -195)),
    )
