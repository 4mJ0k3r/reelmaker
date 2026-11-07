"""Global narration for the long cinematic route, using the existing media stages."""

from reelforge.audio.processing import mix_pcm, mux_audio, verify_audio
from reelforge.audio.registry import AudioRegistry, MAX_NARRATION_FILE_BYTES, digest
from reelforge.core.errors import OperationError
from reelforge.productions.workflow import VIDEO_ALLOWANCE
from reelforge.reels.contract import cue_schedule
from reelforge.reels.workflow import cancelled_check
from reelforge.resources.deployment import check_workspace
from reelforge.stories.audio_contract import SAMPLES_PER_FRAME

MUX_ALLOWANCE = VIDEO_ALLOWANCE + 2 * 1024**2


def check_narration_storage(parent, frames, *, write_probe=True):
    # Silent chunks, their concat, the mux, two stereo float PCM files and the WAV snapshot.
    needed = (2 * VIDEO_ALLOWANCE + MUX_ALLOWANCE + MAX_NARRATION_FILE_BYTES
              + (frames * SAMPLES_PER_FRAME + 1024) * 16 + 64 * 1024**2)
    return check_workspace(parent, minimum_free_bytes=needed, write_probe=write_probe)


def prepare_narration(project, registry_root, private, cancelled):
    private.mkdir()
    resolved = AudioRegistry(registry_root).resolve(
        project.audio, project.frames, cancelled=cancelled, validation_root=private
    )
    if tuple(cue_schedule(resolved)) != project.audio_cues:
        raise OperationError("AUDIO_CHANGED", "Narration identity or timing changed after planning")
    (track,) = resolved
    snapshot = private / track.asset.id / "input.wav"
    snapshot_hash = digest(snapshot)
    if snapshot_hash != track.asset.sha256:
        raise OperationError("AUDIO_CHANGED", "Validated narration snapshot differs from the registry")
    return track, snapshot


def mux_narration(track, snapshot, frames, silent, output, private, cancelled):
    cancelled_check(cancelled)
    if digest(snapshot) != track.asset.sha256:
        raise OperationError("AUDIO_CHANGED", "Narration snapshot changed before mixing")
    reference = private / "reference.f32"
    decoded = private / "decoded.f32"
    mix_pcm((track,), frames, {track.asset.id: snapshot}, reference, cancelled=cancelled)
    cancelled_check(cancelled)
    mux_audio(silent, reference, output, frames, cancelled=cancelled)
    if output.stat().st_size > MUX_ALLOWANCE:
        raise OperationError("REEL_STORAGE", "Global narrated MP4 exceeds its size allowance")
    cancelled_check(cancelled)
    verification = verify_audio(
        silent, output, reference, decoded, (track,), frames, cancelled=cancelled
    )
    start = track.cue.start_frame * SAMPLES_PER_FRAME
    verification["narration"] = {
        "asset_id": track.asset.id,
        "source_sha256": track.asset.sha256,
        "snapshot_sha256": digest(snapshot),
        "source_sample_rate": track.asset.sample_rate,
        "source_channels": track.asset.channels,
        "source_samples_per_channel": track.asset.samples,
        "start_frame": track.cue.start_frame,
        "start_sample": start,
        "source_end_sample_48k": track.source_end_sample_48k,
        "narration_samples_48k": track.output_samples,
        "leading_silence_samples": start,
        "trailing_silence_samples": frames * SAMPLES_PER_FRAME - start - track.output_samples,
        "muxes": 1,
    }
    if verification["narration"]["snapshot_sha256"] != track.asset.sha256:
        raise OperationError("AUDIO_CHANGED", "Narration snapshot changed during mixing")
    return verification
