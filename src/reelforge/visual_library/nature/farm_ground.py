"""An authored, curved farm track on an existing scene support plane."""

from dataclasses import replace

from reelforge.environments.artwork import gradient, path, polygon
from reelforge.rendering.diagnostic import color, ellipse
from reelforge.rendering.model import DrawPath

from .dusk import tone

SUPPORT = (-200, -76, 200, 220)

# Coordinates measured from the local ground anchor. The far end meets a doorway.
TRACK = (
    ("M", 61, -84),
    ("C", 70, -68, 55, -47, 31, -34),
    ("C", -24, -5, -39, 24, -30, 54),
    ("C", -23, 82, 2, 111, 49, 163),
    ("L", 138, 265),
    ("L", -142, 265),
    ("C", -86, 174, -100, 135, -89, 96),
    ("C", -77, 51, -91, 26, -44, -13),
    ("C", -14, -39, 40, -51, 57, -84),
    ("Z",),
)


def farm_track(warmth, variant):
    field = path(
        ("M", -340, -113),
        ("C", -207, -113, -142, -126, -82, -116),
        ("C", -13, -102, 51, -130, 115, -124),
        ("C", 183, -128, 251, -111, 340, -119),
        ("L", 340, 400),
        ("L", -340, 400),
        ("Z",),
    )
    track = path(*TRACK)
    commands = [
        DrawPath(field, gradient(tone("667467", "7a7d59", warmth), color("273d39"), -115, 220)),
        DrawPath(
            path(
                ("M", -340, -96),
                ("C", -228, -114, -116, -103, -53, -101),
                ("C", -27, -100, -14, -93, 12, -85),
                ("C", -68, -91, -145, -64, -220, -69),
                ("L", -340, -45),
                ("Z",),
            ),
            color("9a996e", 0.32),
        ),
        DrawPath(
            path(
                ("M", 46, -89),
                ("C", 144, -107, 230, -75, 340, -88),
                ("L", 340, 68),
                ("C", 189, 49, 162, 3, 53, -22),
                ("Z",),
            ),
            gradient(color("797f56", 0.86), color("425641", 0.3), -88, 65),
        ),
        DrawPath(
            path(
                ("M", -320, 40),
                ("C", -222, -6, -187, 37, -107, 18),
                ("C", -124, 76, -152, 106, -95, 164),
                ("L", -190, 298),
                ("L", -320, 298),
                ("Z",),
            ),
            color("293f38", 0.63),
        ),
        DrawPath(
            path(
                ("M", 45, -38),
                ("C", 116, -29, 147, -6, 222, -9),
                ("C", 262, -13, 301, -4, 340, 12),
                ("L", 340, 44),
                ("C", 273, 16, 221, 29, 160, 21),
                ("C", 100, 15, 77, -12, 45, -38),
                ("Z",),
            ),
            color("a19b6a", 0.16),
        ),
        DrawPath(
            path(
                ("M", 42, 90),
                ("C", 117, 63, 173, 105, 235, 92),
                ("C", 272, 83, 304, 106, 340, 98),
                ("L", 340, 294),
                ("L", 74, 294),
                ("C", 120, 238, 124, 180, 42, 90),
                ("Z",),
            ),
            gradient(color("273d3b", 0.13), color("293a37", 0.59), 90, 294),
        ),
        DrawPath(track, gradient(tone("a49c81", "c5a47c", warmth), color("74614d"), -84, 204)),
        DrawPath(
            path(
                ("M", 60, -84),
                ("C", 58, -53, 7, -44, -32, -10),
                ("C", -88, 38, -55, 74, -67, 111),
                ("C", -73, 148, -76, 188, -105, 239),
                ("L", -147, 267),
                ("L", -135, 132),
                ("L", -90, 3),
                ("Z",),
            ),
            color("534f3c", 0.28),
            clip=track,
        ),
        DrawPath(
            path(
                ("M", 61, -79),
                ("C", 49, -48, 0, -28, -21, 1),
                ("C", -48, 35, -22, 93, 51, 170),
                ("L", 103, 261),
                ("L", 72, 261),
                ("C", 23, 178, -34, 106, -43, 53),
                ("C", -49, 10, -17, -22, 26, -49),
                ("Z",),
            ),
            color("dbc294", 0.22),
            clip=track,
        ),
    ]
    for x, y, size in (
        (-45, 23, 2),
        (-51, 34, 2.8),
        (-33, 35, 1.4),
        (-50, 103, 3.6),
        (-45, 108, 2),
        (-54, 112, 4),
        (6, 126, 2.2),
        (13, 131, 4.4),
        (27, 143, 2.4),
        (-65, 178, 5.2),
        (-57, 186, 3),
    ):
        commands.append(
            DrawPath(ellipse(x, y, size, size * 0.31), color("544938", 0.36), clip=track)
        )
    # Grass occurs in clumps with open intervals, mostly off the traveled surface.
    for x, y, s in (
        (-121, 11, 0.55),
        (-93, 62, 0.78),
        (-106, 69, 1),
        (53, 26, 0.63),
        (62, 44, 0.82),
        (89, 72, 1.12),
        (102, 80, 0.73),
        (-156, 118, 1.52),
        (-125, 137, 1.45),
        (143, 157, 1.55),
        (-157, 179, 2.15),
        (152, 197, 1.8),
    ):
        commands.append(
            polygon(
                tuple(
                    (x + a * s, y + b * s)
                    for a, b in (
                        (-8, 0),
                        (-13, -8),
                        (-5, -4),
                        (-4, -12),
                        (0, -5),
                        (6, -10),
                        (4, -3),
                        (10, -5),
                        (6, 0),
                    )
                ),
                color("99a06a", 0.36),
            )
        )
    if variant == "left_bend":
        # The field and its edge wear mirror together. Cast shadows are separate decals.
        return tuple(
            replace(command, transform=replace(command.transform, sx=-1)) for command in commands
        )
    return tuple(commands)
