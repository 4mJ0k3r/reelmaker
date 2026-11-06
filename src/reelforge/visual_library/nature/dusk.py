"""Hand-shaped atmosphere and ridgelines on the 360 × 640 logical canvas."""

from reelforge.environments.artwork import path
from reelforge.rendering.diagnostic import color, ellipse
from reelforge.rendering.model import Color, DrawPath, LinearGradient, rectangle


def tone(cool, warm, amount, alpha=1):
    a, b = color(cool), color(warm)
    return Color(
        a.r + (b.r - a.r) * amount,
        a.g + (b.g - a.g) * amount,
        a.b + (b.b - a.b) * amount,
        alpha,
    )


def dusk_sky(warmth, atmosphere):
    ramp = LinearGradient(
        (43, -30),
        (96, 399),
        (
            (0, tone("25384c", "29394e", warmth)),
            (0.37, tone("4b647f", "596781", warmth)),
            (0.68, tone("8190a2", "978aa0", warmth)),
            (0.86, tone("9b9eae", "c6a2a1", warmth)),
            (1, tone("b9b0a9", "edb991", warmth)),
        ),
    )
    air = LinearGradient(
        (92, 218),
        (92, 387),
        (
            (0, color("eab294", 0)),
            (0.55, color("efb391", 0.08)),
            (1, color("f7c58b", 0.42 * atmosphere)),
        ),
    )
    high_cloud = path(
        ("M", -48, 132),
        ("C", 9, 117, 23, 133, 62, 136),
        ("C", 91, 138, 105, 124, 139, 134),
        ("C", 173, 145, 198, 135, 232, 155),
        ("C", 185, 149, 160, 166, 124, 155),
        ("C", 96, 147, 64, 164, 25, 156),
        ("C", -5, 154, -25, 150, -48, 155),
        ("Z",),
    )
    low_cloud = path(
        ("M", 68, 223),
        ("C", 99, 215, 131, 207, 163, 213),
        ("C", 193, 215, 207, 203, 238, 209),
        ("C", 263, 212, 290, 217, 331, 211),
        ("C", 304, 226, 273, 220, 244, 223),
        ("C", 221, 225, 194, 232, 167, 225),
        ("C", 129, 218, 111, 230, 68, 223),
        ("Z",),
    )
    return (
        DrawPath(rectangle(-220, -200, 850, 1050), ramp),
        DrawPath(rectangle(-150, 218, 650, 216), air),
        DrawPath(
            high_cloud,
            LinearGradient(
                (-20, 119),
                (211, 160),
                (
                    (0, color("33465d", 0.34)),
                    (0.39, color("52617a", 0.25)),
                    (0.66, color("d4a29e", 0.18)),
                    (1, color("e0ae9b", 0)),
                ),
            ),
        ),
        DrawPath(
            low_cloud,
            LinearGradient(
                (82, 213),
                (313, 223),
                (
                    (0, color("edbd9b", 0.02)),
                    (0.31, color("edbd9b", 0.35)),
                    (0.64, color("cda2a6", 0.14)),
                    (1, color("ae9caa", 0)),
                ),
            ),
        ),
        DrawPath(
            ellipse(92, 276, 22, 20),
            LinearGradient(
                (92, 256),
                (92, 296),
                ((0, color("ffe0a5", 0)), (0.5, color("ffe0a5", 0.13)), (1, color("ffe0a5", 0))),
            ),
        ),
        DrawPath(ellipse(92, 276, 12.5, 12.5), tone("e6dac8", "ffe6b6", warmth)),
    )


def dusk_hills(variant, atmosphere):
    """Local horizon at y=0. Profiles differ in slope, spacing and overlap."""
    if variant == "rolling":
        far = (
            ("M", -330, -29),
            ("C", -235, -33, -212, -51, -174, -59),
            ("C", -117, -73, -91, -29, -53, -23),
            ("C", -15, -15, 25, -49, 71, -46),
            ("C", 115, -43, 163, -17, 208, -20),
            ("L", 340, -24),
        )
        middle = (
            ("M", -330, -5),
            ("C", -251, -14, -203, -36, -149, -33),
            ("C", -95, -30, -54, 13, 0, 7),
            ("C", 63, -1, 79, -24, 128, -22),
            ("C", 183, -19, 230, 21, 340, 8),
        )
    else:
        far = (
            ("M", -330, -42),
            ("C", -230, -35, -177, -8, -116, -21),
            ("C", -72, -35, -43, -66, -10, -69),
            ("C", 45, -76, 69, -32, 109, -27),
            ("C", 154, -18, 204, -41, 340, -37),
        )
        middle = (
            ("M", -330, -11),
            ("C", -263, -12, -161, 17, -110, 5),
            ("C", -57, -9, -17, -27, 23, -22),
            ("C", 80, -17, 121, 21, 177, 17),
            ("C", 214, 16, 266, -8, 340, 2),
        )
    near = (
        ("M", -330, 24),
        ("C", -239, 32, -180, 11, -125, 13),
        ("C", -74, 16, -33, 34, 24, 34),
        ("C", 97, 35, 138, 7, 198, 10),
        ("C", 246, 12, 287, 26, 340, 25),
    )
    colors = (
        ("898598", "bc9b9c", "b9a5a3"),
        ("59697a", "918b93", "a69992"),
        ("3e545e", "666f70", "877d73"),
    )
    commands = []
    for profile, (cool, warm, foot) in zip((far, middle, near), colors, strict=True):
        plane = path(*profile, ("L", 340, 300), ("L", -330, 300), ("Z",))
        commands.append(
            DrawPath(
                plane,
                LinearGradient(
                    (-122, -65),
                    (117, 98),
                    (
                        (0, tone(cool, warm, atmosphere * 0.78)),
                        (0.51, tone(cool, foot, 0.38 + 0.28 * atmosphere)),
                        (1, tone(warm, foot, atmosphere)),
                    ),
                ),
            )
        )
    commands.append(
        DrawPath(
            path(
                ("M", -170, 19),
                ("C", -124, 4, -90, 8, -58, 19),
                ("C", -11, 34, 36, 30, 69, 24),
                ("C", 103, 17, 131, 4, 161, 8),
                ("C", 119, 22, 87, 45, 37, 53),
                ("C", -37, 61, -68, 28, -170, 30),
                ("Z",),
            ),
            LinearGradient(
                (-108, 16), (123, 63), ((0, color("bfa286", 0.19)), (1, color("bfa286", 0)))
            ),
            clip=commands[-1].path,
        )
    )
    return tuple(commands)
