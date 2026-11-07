#!/usr/bin/env python3
"""Build an original diagnostic SFX registry using bounded PCM16 test tones."""

import argparse
import json
import struct
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reelforge.audio.registry import register_asset
from reelforge.audio.transaction import private_directory

FIXTURES = {
    "test_wood_pulse": (360, 12, 0),
    "test_creek_signal": (660, 36, 9),
}


def build(root):
    root.mkdir(exist_ok=False)
    (root / "registry.json").write_text(
        json.dumps({"schema_version": "audio-assets-0.1", "assets": []}) + "\n"
    )
    with private_directory(root) as source:
        for name, (frequency, frames, rise_frames) in FIXTURES.items():
            path = source / f"{name}.wav"
            samples = frames * 1600
            with wave.open(str(path), "wb") as track:
                track.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
                for first in range(0, samples, 1600):
                    block = bytearray()
                    for index in range(first, first + 1600):
                        phase = (index * frequency + max(0, index - rise_frames * 1600) * 145)
                        triangle = 24000 - 2 * abs(phase % 48000 - 24000)
                        envelope = min(index + 16, samples - index, 960)
                        pcm = (triangle - 12000) * envelope // 1920
                        block.extend(struct.pack("<h", pcm))
                    track.writeframesraw(block)
            register_asset(root, path, name, "sfx")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    build(parser.parse_args().directory)
