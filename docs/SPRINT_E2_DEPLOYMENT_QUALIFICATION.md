# E2 deployment qualification

| Gate | Result | Evidence |
| --- | --- | --- |
| Review host preflight and six-second render | PASS | Ubuntu 24.04 x86_64, Python 3.12, native Cairo and FFmpeg H.264/AAC; both packages verified with strict memory admission. |
| Host encoder lifecycle | PASS for tested cases | 41 focused cases on the alternate output path cover cancellation, failure, identity, no-clobber and owned cleanup. |
| Review workspace path | FAIL for unattended operation | Staging names reappeared after observed deletion or publication. |
| Alternate local path | PASS during bounded observation | One smoke and local failure/cleanup tests. Long-term persistence and ordinary-user behavior require separate evidence. |
| Actual constrained Ubuntu VM | NOT TESTED | `TARGET_VM_NOT_TESTED`. No authorized target endpoint or session was available. The review host had eight CPUs of quota and much more available memory. |
| Ordinary user | NOT TESTED | The guest only maps UID/GID 0. An attempted ordinary-user run was denied before rendering. |
| Memory observability | PASS on review host | Raw cgroup, RSS and preflight evidence accompanies the package. The process-tree budget remains 256 MiB with a 64 MiB admission reserve. |

On the authorized target, confirm CPU quota, available RAM, cgroup limit and counters, no swap, native codecs, restricted `/tmp` and durable output capacity. With admission passing, render 6, 15 and 30 seconds sequentially, then consider the silent 60-second case if earlier results justify it. Use an ordinary user and repeat cancellation, failure and occupied-output checks on the actual volume. Record RSS, CPU, wall and storage plus OOM-counter observability. The review-host evidence does not certify the target.
