# Sprint C workspace inventory

Original Sprint C Codex workspace not accessible; restarting Sprint C from approved published B.1 commit.

The current scratch directory contained the 366-line handoff. Read-only inventory of accessible ReelMaker working trees found the earlier Stage 0–3C worktrees and an A1 checkout and bundle. Searches found no Sprint C request compiler, branch, bundle, or matching film exports. Earlier checkouts were left in place.

The GitHub connector resolved the approved branch to commit `180e25a6f7b14eec939db59a318be7b2734dd1b9` and tree `16b554a6620bf18618d83559ab4de0c098426169`. A separate full-history read-only clone matched both IDs before branching. The local development branch is `sprint-c1-c8-autonomous-reel-production`.

The host is Ubuntu 24.04 with Python 3.12.14 and FFmpeg 6.1.1. Dependency setup uses the repository's setup script or its documented system Cairo path. Qualification records the exact active dependencies.

Sprint C adds a separate bounded JSON contract. It compiles the trusted scene and interaction evaluators into shot spans over continuous beat clocks. Short projects use the existing episode frame encoder and AV pipeline. Long silent projects reuse production chunk assembly. A project-level staging transaction packages verified media, render plans and review evidence.
