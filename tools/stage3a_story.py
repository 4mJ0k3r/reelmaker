"""Generate the admitted Stage 3A episode manifest at a fresh path."""

import argparse
import json
from pathlib import Path

from reelforge.visual_library.composition.cinematic_story import cinematic_story


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--story",
        choices=("the_other_light", "the_other_light_refined"),
        default="the_other_light",
    )
    args = parser.parse_args()
    document = cinematic_story(args.story)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(document, output, indent=2, allow_nan=False)
        output.write("\n")


if __name__ == "__main__":
    main()
