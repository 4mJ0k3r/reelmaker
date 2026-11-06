"""Ground-plane marks for authored placement under a left-hand dusk key."""

from reelforge.environments.artwork import path
from reelforge.rendering.diagnostic import color, ellipse
from reelforge.rendering.model import DrawPath, LinearGradient

PROFILES = {
    "foot": (11, 3, 25),
    "trunk": (12, 4.5, 66),
    "prop": (17, 5.5, 37),
}


def dusk_contact(variant):
    radius, height, length = PROFILES[variant]
    cast = path(
        ("M", -radius, 0),
        ("C", radius * 0.4, -height, length * 0.55, 3, length, 13),
        ("C", length * 0.9, 21, length * 0.39, 12, radius * 0.4, height),
        ("C", -radius * 0.4, height * 1.55, -radius, height, -radius, 0),
        ("Z",),
    )
    return (
        DrawPath(
            cast,
            LinearGradient(
                (0, 0),
                (length, 14),
                ((0, color("25303a", 0.32)), (1, color("25303a", 0.035))),
            ),
        ),
        DrawPath(ellipse(0, 1, radius, height), color("262d33", 0.21)),
        DrawPath(ellipse(0, 0, radius * 0.56, height * 0.55), color("292b2d", 0.27)),
    )
