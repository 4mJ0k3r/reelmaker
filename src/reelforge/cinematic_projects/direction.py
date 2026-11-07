"""Bounded native-free diagnostics for the resolved existing cinematic cameras."""
from dataclasses import asdict

from reelforge.characters import living

from .sampling import acting_at, camera_for


def composition_audit(project):
    rows = []
    previous = None
    for shot in project.shots:
        cameras = []
        subjects = {"actor": []}
        if shot.beat.partner:
            subjects["partner"] = []
        for frame in range(shot.start, shot.end):
            local = frame - shot.beat.start
            actor = acting_at(shot.beat, local)
            partner = acting_at(shot.beat, local, partner=True) if shot.beat.partner else None
            camera = camera_for(shot, actor, frame, partner=partner)
            cameras.append(asdict(camera))
            transform = camera.transform(1)
            for name, state in (("actor", actor), ("partner", partner)):
                if state is None:
                    continue
                x, y = state.point(state.pose.root.x, state.pose.root.y)
                identity = shot.beat.actor if name == "actor" else shot.beat.partner.actor
                height = living.PROFILES[identity].height if identity in living.PROFILES else 158
                subjects[name].append((transform.tx + x * transform.sx,
                                       transform.ty + y * transform.sy,
                                       transform.ty + (state.anchor.y - height * state.anchor.scale)
                                       * transform.sy))
        signature = (shot.camera, shot.focus, shot.motion)
        repeated = signature == previous
        rows.append({
            "shot": shot.id, "intent": shot.intent, "camera": shot.camera,
            "focus": shot.focus, "motion": shot.motion,
            "repeats_previous_composition": repeated,
            "intentional_hold": shot.hold,
            "review_repetition": repeated and not shot.hold,
            "camera_samples": [cameras[i] for i in (0, 45, 89)],
            "camera_envelope": {k: [min(c[k] for c in cameras), max(c[k] for c in cameras)]
                                for k in ("x", "y", "zoom")},
            "mobile_metrics": {name: {
                "root_x_range": [min(s[0] for s in samples), max(s[0] for s in samples)],
                "root_y_range": [min(s[1] for s in samples), max(s[1] for s in samples)],
                "estimated_head_top_range": [min(s[2] for s in samples), max(s[2] for s in samples)],
                "root_inside_horizontal_safe_area": all(36 <= s[0] <= 324 for s in samples),
            } for name, samples in subjects.items()},
        })
        previous = signature
    return {"logical_mobile_size": [360, 640], "frames_sampled": project.frames,
            "scope": "All admitted camera frames; root anchors and approximate standing head top. "
                     "Metrics are diagnostics, not full silhouette/occlusion or artistic approval.",
            "shots": rows}
