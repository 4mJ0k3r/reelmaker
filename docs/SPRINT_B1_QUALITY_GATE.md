# Sprint B.1 reliability and motion corrections

All work starts from `e3c683320d6a64327b07bd951405d9ff026abb4c`,
tree `3be2a92f943921cdbcd358dda052a646f87c0838`.

Preset files use the established bounded strict loader. It rejects duplicate
keys, malformed UTF-8, nonfinite numbers and excess nesting. Closed interaction
and film validators then reject extra fields and unsupported combinations.

Multi-shot rendering reserves a new output directory, renders in an
inode-owned private subtree, verifies the joined media and timestamps, and
publishes with atomic no-clobber hard links. Failure rolls back only the
files this job published into its original reserved directory. Unrelated
user content and replacement directories survive. The whole sequence
has resource monitoring in addition to each scene render. Cleanup checks
keep the original inode identity, and never reacquire a removed pathname.

The old implementation left its reserved output directory on early failure.
That defect was confirmed by inspection and corrected. The original stale
encoder directory's cause could not be reproduced conclusively. Native
fault tests exercise frame 0, 15 and 29 and confirm encoder process exit,
closed streams, joined reader threads and staging absence. No stale-path
reconciliation or broad prefix-based deletion was added.

Both new characters have five source-owned continuous transition clips.
Each clip is sampled directly at arbitrary integer frames, with grounded
legs solved against explicit foot targets. Idle-to-walk alternates
individual footprints. Walk-to-stop decelerates its gait clock to a
double-support phase. Stationary transitions blend torso and arm posing,
then re-solve the legs. These are fixed three-second transition studies.
Their start states are authored action phases. They do not provide a
general arbitrary-state motion graph.

Generate a continuous transition proof with:

```sh
PYTHONPATH=src:. python -m tools.living_worlds transition scout_01 idle_to_walk --output-dir outputs/mira-transition
```

The interaction camera follows a measured actor/prop center and keeps
the subjects large enough for a 360×640 screen. Film bookends use related
framing, and the final reaction has a short recognition hold. Interaction
contact sampling and original asset artwork are unchanged.

The review archive contains before/after encoded pairs and decoded mobile
frames. The gallery includes the corrected interaction motion previews and
new transition WebPs. Browser interaction testing remains blocked by an
unavailable executable after a corrupt Chromium download. Static link,
metadata and JavaScript checks are included separately from browser tests.
