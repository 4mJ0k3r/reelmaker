"""Opt-in material grade for an existing architectural drawing."""

from dataclasses import replace

from reelforge.rendering.model import Color


def grade_architecture(commands, warmth, atmosphere):
    """Preserve construction geometry while quieting siding seams under dusk fill."""

    def shade(paint):
        if isinstance(paint, Color):
            return Color(
                paint.r * 0.90 + 0.063 * warmth,
                paint.g * 0.93 + 0.028,
                paint.b * 0.92 + 0.05 * atmosphere,
                paint.a,
            )
        return replace(paint, stops=tuple((offset, shade(value)) for offset, value in paint.stops))

    result = []
    for command in commands:
        stroke = command.stroke
        if stroke is not None:
            paint = shade(stroke.paint)
            if isinstance(paint, Color) and stroke.width < 0.85:
                paint = replace(paint, a=paint.a * 0.58)
            stroke = replace(stroke, paint=paint)
        result.append(
            replace(
                command,
                fill=shade(command.fill) if command.fill is not None else None,
                stroke=stroke,
            )
        )
    return tuple(result)
