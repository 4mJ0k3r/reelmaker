"""One continuous silent encode, one global PCM mix and accepted audiovisual transaction."""

import time
from collections.abc import Callable
from pathlib import Path
from threading import Event

from reelforge.core.errors import OperationError
from reelforge.direction.sampling import direction_frame
from reelforge.reels.workflow import cancelled_check, render_av

from .contract import Episode, frame_origin


def render_episode_video(
    plan: Episode, output: Path, *, encoder_staging: Path, cancelled: Event
) -> dict:
    def sample(frame):
        segment, local = frame_origin(plan, frame)
        return direction_frame(segment.direction, local)

    return encode_episode_frames(
        plan.frames, sample, output, encoder_staging=encoder_staging, cancelled=cancelled
    )


def encode_episode_frames(
    frames: int, sample: Callable, output: Path, *, encoder_staging: Path, cancelled: Event
) -> dict:
    """Encode bounded trusted frames through the shared episode renderer."""
    from reelforge.media.encoder import FFmpegEncoder
    from reelforge.media.verify import verify_video
    from reelforge.rendering.backends.cairo import CairoRenderer, backend_versions
    from reelforge.rendering.diagnostic import color
    from reelforge.scenes.assets import cost

    output.mkdir(exist_ok=False)
    started = time.perf_counter()
    renderer = CairoRenderer()
    source = {}
    max_paths = max_ops = 0
    with FFmpegEncoder(
        output / "scene.mp4",
        width=720,
        height=1280,
        frames=frames,
        staging_directory=encoder_staging,
        cancelled=cancelled,
        timeout=300,
    ) as encoder:
        with renderer.surface(720, 1280) as surface:
            for frame in range(frames):
                cancelled_check(cancelled)
                commands = sample(frame)
                paths, ops = cost(commands)
                max_paths, max_ops = max(max_paths, paths), max(max_ops, ops)
                renderer.draw(
                    surface, commands, background=color("243e49"), logical_size=(360, 640)
                )
                source[str(frame)] = surface.pixel_sha256()
                encoder.write_surface(surface)
    encoded_seconds = time.perf_counter() - started
    verification = verify_video(
        output / "scene.mp4", width=720, height=1280, frames=frames, cancelled=cancelled
    )
    if renderer.active_surfaces or renderer.allocated_bytes:
        raise OperationError("SURFACE_LEAK", "Episode retained a Cairo surface")
    return {
        "success": True,
        "frames": frames,
        "versions": backend_versions(),
        "source_pixel_sha256": source,
        "verification": verification,
        "encoded_fps": frames / encoded_seconds,
        "render_encode_seconds": encoded_seconds,
        "maximum_paths": max_paths,
        "maximum_ops": max_ops,
        "live_surfaces_after": 0,
        "surface_bytes_after": 0,
        "encoder_cleanup_deferred_to_job_owner": True,
        "editorial_cuts": list(range(90, frames, 90)),
        "encoding": (
            "One continuous stream; absolute video PTS, local visual clocks at explicit cuts"
        ),
    }


def render_episode(
    plan: Episode, output: Path, *, registry_root: Path, cancelled: Event | None = None
) -> dict:
    return render_av(
        plan,
        output,
        frames=plan.frames,
        visual_plan=plan,
        render_silent=render_episode_video,
        registry_root=registry_root,
        cancelled=cancelled,
        contract_version=plan.report_contract,
        silent=plan.silent,
    )
