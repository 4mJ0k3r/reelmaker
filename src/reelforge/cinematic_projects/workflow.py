"""Adapt the bounded cinematic plan to the existing episode AV renderer."""

from dataclasses import dataclass
from pathlib import Path
from threading import Event

from reelforge.episodes.workflow import encode_episode_frames
from reelforge.reels.workflow import render_av

from .captions import caption_paths
from .sampling import visual_frame
from .schema import VERSION


@dataclass(frozen=True)
class EpisodeSlice:
    project: object
    start: int
    frames: int

    @property
    def title(self):
        return self.project.title

    @property
    def silent(self):
        return self.project.silent

    @property
    def audio(self):
        return self.project.audio


def frame_sampler(project):
    overlays = [(cue, caption_paths(cue)) for cue in project.captions]

    def sample(frame):
        caption = next((paths for cue, paths in overlays if cue.start <= frame < cue.end), ())
        return visual_frame(project, frame) + caption

    return sample


def render_episode_slice(plan: EpisodeSlice, output: Path, *, registry_root: Path,
                         cancelled: Event):
    def render_silent(visual, target, *, encoder_staging, cancelled):
        sample = frame_sampler(visual.project)
        result = encode_episode_frames(
            visual.frames, lambda frame: sample(visual.start + frame), target,
            encoder_staging=encoder_staging, cancelled=cancelled,
        )
        result["global_start_frame"] = visual.start
        result["encoding"] = "Global acting and caption clocks; explicit camera cuts"
        return result

    return render_av(
        plan, output, frames=plan.frames, visual_plan=plan, render_silent=render_silent,
        registry_root=registry_root, cancelled=cancelled, contract_version=VERSION,
        silent=plan.silent,
    )
