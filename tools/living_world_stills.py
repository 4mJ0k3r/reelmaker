"""Native still evidence for all Sprint B world moods and actor expressions/actions."""

from pathlib import Path

from reelforge.characters.living import ACTIONS, EXPRESSIONS, PROFILES, draw_actor, sample_pose
from reelforge.rendering.backends.cairo import CairoRenderer
from reelforge.rendering.diagnostic import color
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.contract import validate_scene
from reelforge.scenes.graph import compile_scene, scene_frame
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.composition.living_worlds import WORLD_KITS, world_manifest


def main():
    root = Path("docs/visual-evidence/sprint-b")
    root.mkdir(parents=True, exist_ok=True)
    renderer = CairoRenderer()
    with JobMonitor(workspace=root) as monitor:
        def still(name, commands, size, logical, background="313d47"):
            if monitor.cancelled.is_set():
                raise RuntimeError(f"Evidence cancelled: {monitor.limit_reason}")
            with renderer.surface(*size) as surface:
                renderer.draw(surface, commands, logical_size=logical, background=color(background))
                surface.write_png(root / f"{name}.png")
            monitor.sample()

        for identity in PROFILES:
            still(f"{identity}-neutral", tuple(Placement(180,420,2.4).command(c)
                  for c in draw_actor(identity, "idle", "neutral", 0)),
                  (720,1280), (360,640))
            for label, values in (("expressions", EXPRESSIONS), ("actions", ACTIONS)):
                sheet = []
                for index, value in enumerate(values):
                    action, expression, time = ("idle", value, 0) if label == "expressions" else (value, "concerned", .37)
                    pose = sample_pose(identity, action, time)
                    placement = Placement(90 + index * 180 - pose.root.x, 154)
                    sheet.extend(placement.command(c) for c in draw_actor(identity,action,expression,time))
                size = (180*len(values),180)
                still(f"{identity}-{label}", tuple(sheet), size, size)

        for kit, moods in WORLD_KITS.items():
            for mood in moods:
                scene = compile_scene(validate_scene(world_manifest(kit,mood)))
                for size in ((720,1280),(360,640)):
                    still(f"{kit}-{mood}-{size[0]}", scene_frame(scene,40), size, (360,640))
    if monitor.cancelled.is_set():
        raise RuntimeError(f"Evidence cancelled: {monitor.limit_reason}")


if __name__ == "__main__":
    main()
