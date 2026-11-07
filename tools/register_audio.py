"""Operator-only local PCM16 WAV registration. Story manifests never choose file paths."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from reelforge.audio.registry import register_asset
from reelforge.core.errors import InputError, OperationError
from reelforge.resources.monitor import JobMonitor
from reelforge.resources.deployment import check_workspace

AUDIO_ROOT = Path(__file__).resolve().parents[1] / "assets/audio"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--registry", type=Path, default=AUDIO_ROOT)
    parser.add_argument("--id", required=True)
    parser.add_argument("--role", choices=("narration", "sfx"), required=True)
    args = parser.parse_args()
    try:
        args.registry.mkdir(parents=True, exist_ok=True, mode=0o700)
        check_workspace(args.registry)
        with JobMonitor(workspace=args.registry):
            asset = register_asset(args.registry, args.source, args.id, args.role)
    except (InputError, OperationError, OSError) as exc:
        print(json.dumps({"registered": False, "error": str(exc)}))
        return 2
    print(json.dumps({"registered": True, "asset": asdict(asset)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
