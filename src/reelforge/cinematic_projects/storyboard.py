"""Bounded, labeled contact sheets from the actual encoded video."""

from reelforge.core.errors import OperationError
from reelforge.media.process import run_bounded

MOBILE_W, MOBILE_H = 360, 640
LABEL = 26
SHOTS_PER_PAGE = 4


def _run(args, cancelled, seconds=90):
    status, out, err = run_bounded(args, timeout=seconds, cancelled=cancelled)
    if status:
        raise OperationError("CINEMATIC_EVIDENCE", err.decode(errors="replace")[-512:])
    return out, err


def black_frames(video, cancelled):
    _, stderr = _run(
        [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-v",
            "info",
            "-xerror",
            "-threads",
            "1",
            "-i",
            str(video),
            "-map",
            "0:v:0",
            "-an",
            "-filter_threads",
            "1",
            "-vf",
            "blackframe=amount=98:threshold=24",
            "-f",
            "null",
            "-",
        ],
        cancelled,
    )
    black = [line for line in stderr.decode(errors="replace").splitlines() if "pblack:" in line]
    if black:
        raise OperationError("CINEMATIC_BLACK_FRAME", f"Found {len(black)} nearly black frames")
    return {"frames_flagged": 0, "minimum_black_area_percent": 98, "luma_threshold": 24}


def write_storyboard(project, video, target, cancelled):
    import cairo

    directory = target / "storyboard"
    directory.mkdir()
    frames = [
        frame for s in project.shots for frame in (s.start, (s.start + s.end) // 2, s.end - 1)
    ]
    selected = "+".join(f"eq(n\\,{frame})" for frame in frames)
    _run(
        [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-v",
            "error",
            "-xerror",
            "-threads",
            "1",
            "-i",
            str(video),
            "-map",
            "0:v:0",
            "-an",
            "-filter_threads",
            "1",
            "-vf",
            f"select={selected}",
            "-fps_mode",
            "passthrough",
            "-threads:v",
            "1",
            "-start_number",
            "0",
            "-n",
            str(directory / "frame-%03d.png"),
        ],
        cancelled,
    )
    for page, start in enumerate(range(0, len(project.shots), SHOTS_PER_PAGE), 1):
        rows = project.shots[start : start + SHOTS_PER_PAGE]
        surface = cairo.ImageSurface(
            cairo.FORMAT_RGB24, 3 * MOBILE_W, len(rows) * (MOBILE_H + LABEL)
        )
        try:
            ctx = cairo.Context(surface)
            ctx.set_source_rgb(0.08, 0.12, 0.14)
            ctx.paint()
            ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(14)
            for row, shot in enumerate(rows):
                for column in range(3):
                    index = 3 * (start + row) + column
                    x, y = column * MOBILE_W, row * (MOBILE_H + LABEL)
                    with cairo.ImageSurface.create_from_png(
                        str(directory / f"frame-{index:03d}.png")
                    ) as png:
                        ctx.save()
                        ctx.translate(x, y + LABEL)
                        ctx.scale(0.5, 0.5)
                        ctx.set_source_surface(png)
                        ctx.rectangle(0, 0, 2 * MOBILE_W, 2 * MOBILE_H)
                        ctx.fill()
                        ctx.restore()
                    ctx.set_source_rgb(0.96, 0.92, 0.83)
                    ctx.move_to(x + 8, y + 18)
                    ctx.show_text(f"{shot.id}  |  frame {frames[index]:04d}")
            surface.write_to_png(str(directory / f"mobile-{page:02d}.png"))
        finally:
            surface.finish()
    return [
        {"frame": frame, "file": f"storyboard/frame-{i:03d}.png"} for i, frame in enumerate(frames)
    ]
