"""Render the sprint's two validated scenes and a layer placement breakdown."""

import json
from pathlib import Path

from reelforge.catalog.inventory import ROOT
from reelforge.rendering.backends.cairo import CairoRenderer
from reelforge.rendering.diagnostic import color
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.contract import load_scene
from reelforge.scenes.graph import compile_scene, evaluate_layers, inspect_scene, scene_frame


def main():
    output = ROOT / "docs/visual-evidence/asset-sprint-a2-a4/integrated-scenes"
    output.mkdir(parents=True, exist_ok=True)
    renderer = CairoRenderer()
    with JobMonitor(workspace=output) as monitor:
        for source in sorted((ROOT / "examples/asset-sprint").glob("*.scene.json")):
            name = source.name.removesuffix(".scene.json")
            scene = compile_scene(load_scene(source))
            frame = 45
            for size in ((720, 1280), (360, 640)):
                with renderer.surface(*size) as surface:
                    renderer.draw(surface, scene_frame(scene, frame), logical_size=(360, 640),
                                  background=color("243e49"))
                    surface.write_png(output / f"{name}-{size[0]}.png")
            placement = inspect_scene(scene, frame)
            placement["layer_draw_paths"] = {layer.id: len(layer.commands)
                                             for layer in evaluate_layers(scene, frame)}
            (output / f"{name}-placement.json").write_text(json.dumps(placement, indent=2) + "\n")
            monitor.sample()
            if monitor.cancelled.is_set():
                raise RuntimeError(f"Evidence render cancelled: {monitor.limit_reason}")


if __name__ == "__main__":
    main()
