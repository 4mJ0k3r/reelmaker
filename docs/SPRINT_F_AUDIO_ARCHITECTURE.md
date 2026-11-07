# Sprint F audio architecture

The approved E1–E6 baseline is `a6cb1d57b67b681207989a7db43014a787f81f47` with tree `34b7878074a6b15e562bccba97607a2c6695e45b`. The working tree was clean before the F branch was created. Python 3.12.14, Pycairo 1.29.2 and FFmpeg 6.1.1 were checked. The approved Empty Town MP4 has 1,800 H.264 frames and no audio. Its prior verification records the subtitle schedule, exact frame clock and two verified chunks.

## Baseline and extension

The cinematic schema borrows the episode audio structure. The shared cue parser and short AV renderer enforce their own bounds. The trusted registry caps narration duration and the whole WAV file. Mixing uses an explicit 48 kHz sample grid. The existing AAC verifier checks presentation timing, padding, video stream copy and audible alignment. Production assembly verifies silent chunks and their decoded frame sequence.

Keep the legacy render and silent routes intact. Extend staged cinematic projects beyond ten shots for one registered narration only. Keep the existing short cue bounds and short renderer. Snapshot and validate a finished mono or stereo PCM16 WAV in a private workspace before native rendering. Admission accounts for 60 seconds of 48 kHz stereo PCM16 plus a bounded RIFF metadata allowance, the reference and decoded stereo PCM files, and the muxed MP4. Use the existing workspace reserve and process-tree monitor.

Make long episode slices explicitly silent. Verify and assemble them through the existing production path. Mix once on the global sample grid, reject implicit truncation, and stream-copy the assembled video during a single AAC-LC mux. Report exact start and silence padding. Verify the decoded AAC clock, video stream identity and chunk frame identity before atomic publication. Verify the delivered AAC sample clock again when the operator opens the package for verification. Retain the authored frame grid and caption timing. The workflow neither derives scenes from audio nor produces speech.

The review fixture is a deterministic timing signal. A real recording is private operator input and belongs in a private registry outside Git. The historical workspace staging recurrence and real target VM qualification remain open.
