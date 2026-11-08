"""Native sample evidence for registered assets in a compiled silent production."""

from collections import defaultdict
from dataclasses import replace

from reelforge.direction.sampling import direction_frame
from reelforge.productions.contract import FRAMES_PER_SEGMENT, Production
from reelforge.rendering.diagnostic import color

SAMPLES = (15, 45, 75)


def audit_assets(production: Production) -> dict:
    """Measure a pixel contribution by muting one asset ID at a time.

    The camera, character sample, transforms and remaining painter order stay fixed.
    Visibility across unsampled frames is deliberately left unmeasured.
    """
    from reelforge.rendering.backends.cairo import CairoRenderer

    renderer = CairoRenderer()
    shots, referenced, active, confirmed = [], set(), set(), set()
    with renderer.surface(720, 1280) as surface:
        def digest(direction, frame):
            renderer.draw(
                surface, direction_frame(direction, frame),
                background=color("243e49"), logical_size=(360, 640),
            )
            return surface.pixel_sha256()

        for shot_index, segment in enumerate(production.segments):
            direction = segment.storyboard.direction
            compiled = direction.compiled
            hierarchy = {node.id: node for node in compiled.hierarchy}
            by_asset = defaultdict(list)
            for node in compiled.scene.nodes:
                if node.asset_id is not None:
                    by_asset[node.asset_id].append(node)

            samples = {frame: digest(direction, frame) for frame in SAMPLES}
            rows = []
            for asset_id, nodes in sorted(by_asset.items()):
                ids = {node.id for node in nodes if hierarchy[node.id].visible}
                changed = []
                if ids:
                    muted = replace(compiled, hierarchy=tuple(
                        replace(node, visible=False) if node.id in ids else node
                        for node in compiled.hierarchy
                    ))
                    comparison = replace(direction, compiled=muted)
                    changed = [frame for frame in SAMPLES
                               if digest(comparison, frame) != samples[frame]]
                    active.add(asset_id)
                if changed:
                    confirmed.add(asset_id)
                referenced.add(asset_id)
                rows.append({
                    "registered_asset_id": asset_id,
                    "instances": [{"node": n.id, "variant": n.variant,
                                   "active": n.id in ids} for n in nodes],
                    "active_frames": FRAMES_PER_SEGMENT if ids else 0,
                    "sampled_render_use": (
                        "pixel_contribution_confirmed" if changed else
                        "no_contribution_in_samples" if ids else "referenced_only"
                    ),
                    "sample_frames_with_contribution": changed,
                })
            start = shot_index * FRAMES_PER_SEGMENT
            shots.append({"segment": segment.id, "scene": segment.storyboard.title,
                          "start_frame": start, "end_frame_exclusive": start + FRAMES_PER_SEGMENT,
                          "assets": rows})
    return {
        "measurement": "Exact source-render pixel ablation at 720x1280 before H.264 encoding",
        "sample_frames_per_shot": list(SAMPLES),
        "referenced_asset_ids": sorted(referenced),
        "active_asset_ids": sorted(active),
        "pixel_confirmed_asset_ids": sorted(confirmed),
        "unique_referenced_count": len(referenced),
        "unique_active_count": len(active),
        "unique_pixel_confirmed_count": len(confirmed),
        "shots": shots,
    }
