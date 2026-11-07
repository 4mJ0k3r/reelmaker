"""Verify B.1 media and produce encoded comparisons and mobile evidence."""

import argparse
import json
import math
from pathlib import Path
from threading import Event

from reelforge.characters import living
from reelforge.characters.living_transitions import TRANSITIONS, sample_transition
from reelforge.media.process import run_bounded
from reelforge.media.verify import verify_video
from reelforge.productions.workflow import _verify_pts
from reelforge.rendering.backends.cairo import CairoRenderer
from reelforge.rendering.diagnostic import color
from reelforge.resources.monitor import JobMonitor
from reelforge.scenes.transforms import Placement
from reelforge.visual_library.composition.interactions import (
    INTERACTIONS, compile_interaction, sample_interaction,
)
from tools.living_worlds import interaction_request


PAIRS = ("pickup_carry_place","sit_stand","push_cart","the_forgotten_parcel","the_creek_crossing")


def command(args, cancelled):
    code, _, errors = run_bounded(args, timeout=120, cancelled=cancelled)
    if code or errors.strip():
        raise RuntimeError(errors.decode("utf-8", errors="replace"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before-dir",type=Path,required=True)
    parser.add_argument("--output-root",type=Path,default=Path("outputs/sprint-b1"))
    args=parser.parse_args()
    root=args.output_root.resolve()
    evidence=Path("docs/visual-evidence/sprint-b1")
    evidence.mkdir(parents=True,exist_ok=True)
    (evidence/"mobile").mkdir(exist_ok=True)
    (evidence/"motion").mkdir(exist_ok=True)
    (root/"comparisons").mkdir(exist_ok=False)
    metrics={}
    with JobMonitor(workspace=root) as monitor:
        for directory in sorted(p for p in root.iterdir() if p.is_dir()
                                and ((p/"scene.mp4").exists() or (p/"film.mp4").exists())):
            video=directory/("film.mp4" if (directory/"film.mp4").exists() else "scene.mp4")
            report=json.loads(next(directory.glob("*report.json")).read_text())
            frames=report["frames"]
            verification=verify_video(video,width=720,height=1280,frames=frames,cancelled=monitor.cancelled)
            pts=_verify_pts(video,frames,monitor.cancelled)
            shots=report.get("shots",[report])
            memories=[s["memory"] for s in shots]
            if "assembly_memory" in report:
                memories.append(report["assembly_memory"])
            if "sequence_memory" in report:
                memories.append(report["sequence_memory"])
            assert all(m["limit_reason"] is None for m in memories)
            assert all(s["success"] and s["live_surfaces_after"]==s["surface_bytes_after"]==0 for s in shots)
            assert not any(p.name.startswith(".reelforge") for p in directory.iterdir())
            metrics[directory.name]=dict(frames=frames,verified=verification["passed"],pts=pts,
                peak_mib=max(m["estimated_simultaneous_tree_peak_rss_bytes"] for m in memories)/2**20,
                render_wall_seconds=sum(s["wall_seconds"] for s in shots),
                render_cpu_seconds=sum(sum(s["cpu_seconds"].values()) for s in shots))
            preview=evidence/"motion"/f"{directory.name}.webp"
            command(["ffmpeg","-v","error","-threads","1","-i",str(video),
                     "-vf","fps=8,scale=180:320","-an","-c:v","libwebp_anim","-quality","68",
                     "-loop","0","-threads","1","-n",str(preview)],monitor.cancelled)
            if directory.name in PAIRS:
                before=args.before_dir/f"{directory.name}.mp4"
                comparison=root/"comparisons"/f"{directory.name}-before-after.mp4"
                command(["ffmpeg","-v","error","-threads","1","-i",str(before),"-threads","1",
                         "-i",str(video),"-filter_complex_threads","1","-filter_complex",
                         "[0:v]scale=360:640[a];[1:v]scale=360:640[b];[a][b]hstack=inputs=2[v]",
                         "-map","[v]","-an","-c:v","libx264","-preset","veryfast","-crf","20",
                         "-pix_fmt","yuv420p","-threads","1","-movflags","+faststart","-n",str(comparison)],monitor.cancelled)
                verify_video(comparison,width=720,height=640,frames=frames,cancelled=monitor.cancelled)
                for label,source in (("before",before),("after",video)):
                    image=evidence/"mobile"/f"{directory.name}-{label}.png"
                    key=75 if frames<200 else 130
                    command(["ffmpeg","-v","error","-threads","1","-i",str(source),
                             "-vf",f"select=eq(n\\,{key}),scale=360:640","-frames:v","1","-threads","1",
                             "-n",str(image)],monitor.cancelled)
            monitor.sample()
            if monitor.cancelled.is_set():
                raise RuntimeError(f"Evidence cancelled: {monitor.limit_reason}")

    transitions={}
    renderer=CairoRenderer()
    for actor in living.PROFILES:
        for name in TRANSITIONS:
            samples=[sample_transition(actor,name,f) for f in range(90)]
            joints=[living.RIGS[actor].evaluate(s.pose) for s in samples]
            delta=max(math.hypot(b[k].x-a[k].x,b[k].y-a[k].y)
                      for a,b in zip(joints,joints[1:]) for k in a)
            drift=0
            for frame in range(1,90):
                for index,side in enumerate(("far","near")):
                    if samples[frame].planted[index] and samples[frame-1].planted[index]:
                        before,after=joints[frame-1][f"{side}_foot"],joints[frame][f"{side}_foot"]
                        drift=max(drift,math.hypot(after.x-before.x,after.y-before.y))
            hashes={}
            for frame in (0,45,89,45,0):
                commands=tuple(Placement(120,230,1.5).command(c)
                               for c in living.draw_pose(actor,samples[frame].pose,"concerned"))
                with renderer.surface(360,640) as surface:
                    renderer.draw(surface,commands,logical_size=(360,640),background=color("34404b"))
                    digest=surface.pixel_sha256()
                    assert frame not in hashes or hashes[frame]==digest
                    hashes[frame]=digest
            transitions[f"{actor}/{name}"]=dict(max_joint_delta=delta,max_planted_foot_drift=drift,
                                               repeated_pixel_hashes=hashes)
    contacts={}
    for key in ("pickup_carry_place","push_cart"):
        spec=INTERACTIONS[key]
        for actor in spec.actors:
            plan=compile_interaction(interaction_request(key,actor,spec.variants[0]))
            errors=[]
            for frame in range(spec.frames):
                sample=sample_interaction(plan,frame)
                if sample.contact:
                    hand=living.RIGS[actor].evaluate(sample.pose)["near_hand"]
                    dx,dy=(0,-16) if key=="pickup_carry_place" else (-51,-41)
                    errors.append(math.hypot(hand.x-sample.prop[0]-dx,hand.y-sample.prop[1]-dy))
            contacts[f"{key}/{actor}"]=max(errors)
    (root/"verification.json").write_text(json.dumps(dict(media=metrics,transitions=transitions,
                                                           contacts=contacts),indent=2)+"\n")
    print(json.dumps(metrics,indent=2))


if __name__=="__main__":
    main()
