"""Turn bounded caption lines into native Cairo glyph contours once per render."""

from reelforge.core.errors import OperationError
from reelforge.rendering.diagnostic import color
from reelforge.rendering.model import DrawPath, PathOp, Transform, rectangle

# Logical 360 x 640 coordinates. Margins avoid the typical right and bottom UI zones.
STYLES = {
    "subtitle": (24, 487, 288, 19, "fcf4dd", "acbfb8", True),
    "chapter": (24, 103, 288, 26, "fff0d2", "e2ae60", False),
    "lower_third": (24, 430, 264, 18, "fff2db", "8eb6a9", False),
}


def caption_paths(caption):
    import cairo

    x, y, width, font_size, foreground, accent, center = STYLES[caption.style]
    baseline = y + font_size + 10
    spacing = font_size + 6
    height = 23 + font_size + (len(caption.lines) - 1) * spacing
    commands = [
        DrawPath(rectangle(x, y, width, height), color("182429")),
        DrawPath(rectangle(x, y, 3, height), color(accent)),
    ]
    # Recording surface creates outlines without allocating a second raster frame.
    surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
    try:
        context = cairo.Context(surface)
        context.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        op_names = ("M", "L", "C", "Z")
        for line in caption.lines:
            context.set_font_size(font_size)
            extents = context.text_extents(line)
            scale = min(1.0, (width - 28) / max(extents.width, 1))
            if font_size * scale < 11:
                raise OperationError("CAPTION_LAYOUT", "Shorten the caption for the safe area")
            glyphs, _, _ = context.get_scaled_font().text_to_glyphs(0, 0, line)
            if not glyphs or any(g.index == 0 for g in glyphs):
                raise OperationError("CAPTION_GLYPH", "DejaVu Sans lacks a required glyph")
            context.new_path()
            context.move_to(0, 0)
            context.text_path(line)
            # Pycairo path iteration is the public API. The first move anchors the contours.
            ops = tuple(PathOp(op_names[code], tuple(points))
                        for code, points in context.copy_path())
            if not any(op.kind in ("L", "C") for op in ops):
                raise OperationError("CAPTION_GLYPH", "Caption produced no visible outlines")
            left = x + (width - extents.width * scale) / 2 if center else x + 14
            commands.append(DrawPath(
                ops, color(foreground),
                transform=Transform(left - extents.x_bearing * scale, baseline,
                                    sx=scale, sy=scale),
            ))
            baseline += spacing
    finally:
        surface.finish()
    return tuple(commands)
