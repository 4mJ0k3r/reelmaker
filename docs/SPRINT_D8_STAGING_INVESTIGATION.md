# D8 staging and ownership investigation

## Observed recurrence — root cause still unresolved

A real six-second Cairo/FFmpeg cinematic job was run under the opt-in bounded
lifecycle collector, followed by observations at return, +1s and +2s.
`outputs/d8-d9/native-lifecycle.json` has all 48 monotonic events (zero dropped).
The original cinematic stage was device 27 / inode 263843. It was atomically
published as trace-success; the original name was absent immediately after
rename. At +1s and +2s the old name existed with inode 263885 on device 27.
The destination retained the original inode. Thus the later old-name directory
was not the original owned inode. Its mtime preceded the publication while its
ctime followed publication. Exact nanosecond observations are in the trace.

The encoder and supervised media tools were reaped before work cleanup.
The producer observed no procfs descendants at return. The work and nested
AV transaction paths were absent in the recorded delayed samples. No foreign
or recreated path was removed by the observer. Birth time was unavailable.

These observations reject the simple hypothesis that the original stage was
never renamed. They do not identify the new directory's creator. An external
workspace/filesystem view restoration is consistent with the inode/mtime/ctime
pattern, but is an inference, not a proven platform root cause. Hidden namespace
processes, external synchronization or another host component cannot be ruled
out with this guest view. No claim that recurrence is fixed is made.

`tools/trace_cinematic.py PROJECT OUTPUT TRACE.json --observe-seconds 2`
executes the existing production CLI, not an alternate renderer. The trace
records original identities, publication/removal events, child start/reap,
return, and delayed observations. It is capped at 4096 events and a ten-second
observation window. Exit 3 means a delayed recurrence was observed, even when
the production itself returned success. Existing traces predate that summary
field; their complete raw observations are retained.

## Separate reproducible ownership defect — corrected

Failure injection exposed a real composition-of-transactions defect: a child
AV transaction could detect a replaced staging directory and report a cleanup
identity error, but the outer cinematic work owner would then recursively
remove the enclosing work tree. That could remove replacement content despite
the child's refusal. It is separate from the unexplained historical recurrence.

The cinematic wrapper now closes and preserves the work tree when a child
reports cleanup uncertainty, then returns CINEMATIC_OWNERSHIP with its path.
Long chunk rendering propagates that cleanup uncertainty. OwnedDirectory's
explicit preserve operation never deletes or later reconciles the path.
The incomplete top-level result is not published. New unit and real native
replacement tests prove that the replacement sentinel survives. This is a
minimal refusal/preservation fix, not a prefix sweep or a root-cause claim for
historical recurrence. Preserved directories may consume storage; admission
still applies and an operator must investigate before manual recovery.

## Fault evidence and limitations

Existing transaction tests retain target-race, report-write, verification,
source-stage replacement, allowlist and malformed audio checks. New native
cases exercise actual Cairo/FFmpeg first/middle/final frame failure, startup
failure, nonzero encoder exit, cooperative cancellation, nested replacement,
and SIGTERM during an active encode. Native encoder starts/reaps and owned
path outcomes are captured; test artifacts distinguish simulated package-
boundary faults from real media-process faults. No uncontrolled concurrent
stress runs or arbitrary cleanup is used.

Release impact: unresolved post-return recurrence prevents an unconditional
cleanup/deployment certification. Verified media and local development review
can proceed with explicit qualification limits. Preserve unexpected paths,
keep jobs sequential and destinations unique, retain trace/identity evidence,
monitor persistent storage, and investigate the host view; never delete by a
familiar prefix or adopt a replaced inode as an old job's property.
