"""Render both world kits at full and mobile resolution through the Cairo scene renderer."""

import argparse
from pathlib import Path

from reelforge.rendering.backends.cairo import CairoRenderer
from reelforge.rendering.diagnostic import color
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.visual_library.composition.living_worlds import MOODS, world_manifest


def previews(output):
    output.mkdir(parents=True, exist_ok=True)
    renderer = CairoRenderer()
    for kit, moods in MOODS.items():
        for mood in moods:
            scene = compile_scene(validate_scene(world_manifest(kit, mood, actor="scout_01")))
            commands = scene_frame(scene, 45)
            for width, height in ((720, 1280), (360, 640)):
                with renderer.surface(width, height) as target:
                    renderer.draw(target, commands, background=color("243e49"),
                                  logical_size=(360, 640))
                    with (output / f"{kit}-{mood}-{width}.png").open("xb") as handle:
                        target.write_png(handle)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    previews(parser.parse_args().output)
