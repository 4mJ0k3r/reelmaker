# Sprint J operator guide

Status: source integration and focused tests exist. Full production execution is
NOT QUALIFIED on the current host: strict admission refuses missing cgroup/OOM telemetry.
Do not disable or monkeypatch guards to obtain a demo. Use a provisioned Ubuntu 24.04
Python 3.12 host with valid memory telemetry for the remaining acceptance gate.

1. Discover: `python tools/reel_production.py capabilities` and `schema`.
2. Copy an example from examples/sprint-j to a PRIVATE directory outside checkout.
3. Prepare your finished recording without overwriting it, only if conversion needed:

```
ffmpeg -nostdin -v error -i supplied.m4a -map 0:a:0 -vn -sn -dn -c:a pcm_s16le -ar 48000 -ac 2 -n prepared.wav
python tools/register_audio.py prepared.wav --id approved_take --role narration --registry /persistent/private-audio
```

Copy the registry's actual SHA-256 into narration.sha256, use provenance
user_finished_recording, start:"0", trim_start:"0", trim_end:null, gain:0.8,
allow_trim:false. Preserve the original. For an engineering signal only:

```
python tools/sprint_j_timing_fixture.py PRIVATE/request.json PRIVATE/synthetic.wav
python tools/register_audio.py PRIVATE/synthetic.wav --id timing_fixture --role narration --registry PRIVATE/audio
```

Mark provenance synthetic_timing_fixture. Tones are NOT voice; no subjective voice
alignment can be accepted from them. Example scripts are deliberately synthetic.

4. Validate, plan and inspect using the same trusted private registry:

```
python tools/reel_production.py --registry PRIVATE/audio validate PRIVATE/request.json
python tools/reel_production.py --registry PRIVATE/audio plan PRIVATE/request.json
python tools/reel_production.py --registry PRIVATE/audio inspect PRIVATE/request.json
```

Inspect requested event intervals, actual shot actions/assets/cameras, forbidden
items, padding and repetition warnings. Plan and inspect currently return the same
resolved timeline; no extra artistic certification is implied.

5. Create a persistent non-symlink output parent, then:

```
python tools/reel_production.py --registry PRIVATE/audio preflight PRIVATE/request.json OUTPUT/new_film
python tools/reel_production.py --registry PRIVATE/audio render PRIVATE/request.json OUTPUT/new_film
python tools/reel_production.py --registry PRIVATE/audio verify OUTPUT/new_film
```

Success requires complete verification.json and visual review of decoded mobile
sheets. On failures use a new name, preserve evidence and investigate ownership.
MEMORY_PREFLIGHT means capacity/observability failed; never lower limits.
TIMING_CONFLICT means review the quantified legal grid suggestion; no mapping applied.
UNIFIED_CONTRACT identifies the invalid field/unsatisfied asset; do not edit source
for a normal production. AUDIO_CHANGED means restore the exact trusted source or
register a new take. OUTPUT_EXISTS preserves an old film. Missing Hindi support or
>60s requests are explicit unsupported cases. CLI exits 2 on structured failure.

Windows/WSL2 and target low-memory VM remain untested. No Windows wrapper delivered.
The historical staging recurrence issue remains unattributed. No GitHub publication.
