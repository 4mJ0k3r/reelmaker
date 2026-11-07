"""Generate deterministic calibration tones for tests. This is not narration speech."""

import argparse
import array
import math
import sys
import wave
from pathlib import Path


def write_fixture(path: Path, *, rate=48000, channels=2, samples=None):
    samples = rate * 60 if samples is None else samples
    with path.open("xb") as raw, wave.open(raw, "wb") as wav:
        wav.setparams((channels, 2, rate, samples, "NONE", "not compressed"))
        for start in range(0, samples, 4096):
            block = array.array("h")
            for i in range(start, min(start + 4096, samples)):
                # Continuous phase plus slow amplitude variation through the chunk seam.
                left = int((5700 + 900 * math.sin(2 * math.pi * i / (rate * 7)))
                           * math.sin(2 * math.pi * 237 * i / rate))
                block.append(left)
                if channels == 2:
                    block.append(int(4200 * math.sin(2 * math.pi * 349 * i / rate)))
            if sys.byteorder != "little":
                block.byteswap()
            wav.writeframesraw(block.tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    write_fixture(parser.parse_args().output)
