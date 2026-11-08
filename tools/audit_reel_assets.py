#!/usr/bin/env python3
"""Report measured asset use for a verified run_reel.py job."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reelforge.mvp.asset_audit import audit_assets
from reelforge.productions.contract import load_production


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path)
    job = parser.parse_args().job
    manifest = job / "production_manifest.json"
    video = job / "final.mp4"
    verification = json.loads((job / "verification.json").read_text())
    digest = sha256(video)
    if not verification.get("passed") or verification.get("sha256") != digest:
        parser.error("Provide a successfully verified run_reel.py job with its original final.mp4")
    manifest_digest = sha256(manifest)
    if verification.get("manifest_sha256") != manifest_digest:
        parser.error("Provide the original manifest from a verified director-v3 job")
    production = load_production(manifest)
    if verification.get("decoded_frames") != production.frames:
        parser.error("Manifest and verified movie frame counts differ")
    result = audit_assets(production)
    result.update(manifest_sha256=manifest_digest, verified_mp4_sha256=digest)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
