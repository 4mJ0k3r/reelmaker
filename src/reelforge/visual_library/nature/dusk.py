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
    horizon = tone("a2a6b2", "edb188", warmth)
    ramp = LinearGradient(
        (0, -16),
        (0, 386),
        (
            (0, tone("25384c", "394458", warmth)),
            (0.38, tone("596f87", "797b92", warmth)),
            (0.74, tone("8d98ad", "c89990", warmth)),
            (1, horizon),
        ),
    )
    veil = LinearGradient(
        (30, 172),
        (286, 248),
        ((0, color("f2c3aa", 0.43)), (0.65, color("d99f97", 0.17)), (1, color("a68aab", 0))),
    )
    haze = LinearGradient(
        (0, 236),
        (0, 386),
        ((0, color("efc39b", 0)), (1, color("f3c994", 0.34 * atmosphere))),
    )
    return (
        DrawPath(rectangle(-220, -200, 850, 1050), ramp),
        DrawPath(rectangle(-150, 236, 650, 180), haze),
        DrawPath(
            path(
                ("M", -50, 123),
                ("C", 21, 114, 67, 153, 138, 146),
                ("C", 194, 139, 214, 164, 281, 171),
                ("C", 192, 180, 146, 170, 98, 168),
                ("C", 40, 165, 0, 143, -50, 151),
                ("Z",),
            ),
            veil,
        ),
        DrawPath(
            path(
                ("M", 91, 217),
                ("C", 135, 202, 159, 209, 184, 213),
                ("C", 220, 219, 242, 211, 306, 227),
                ("C", 255, 229, 210, 224, 173, 226),
                ("C", 149, 223, 112, 219, 91, 217),
                ("Z",),
            ),
            veil,
        ),
        DrawPath(ellipse(92, 276, 12.5, 12.5), tone("e6dac8", "ffe4b5", warmth)),
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
        tone("7d8594", "bc9a96", atmosphere),
        tone("596f80", "998c90", atmosphere),
        tone("445b63", "777c78", atmosphere),
    )
    return tuple(
        DrawPath(
            path(*profile, ("L", 340, 300), ("L", -330, 300), ("Z",)),
            LinearGradient(
                (0, -70), (0, 65), ((0, tint), (1, tone("9d8f89", "cfaa93", atmosphere, 0.89)))
            ),
        )
        for profile, tint in zip((far, middle, near), colors, strict=True)
    )
