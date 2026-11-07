# E1 staging reliability

The fetched approved D8–D9 branch matched commit `ee1787c3fa322a88ca77c1c5bb6b0032a371f89b` and tree `2b0826c6d8aee314b604d0b859568e76798a41db`. The D8–D9 tip and D7B ancestor were both verified. The prior independent qualification and the existing transaction, resource and CLI behavior were reviewed. The baseline hosted [Visual catalog run](https://github.com/4mJ0k3r/reelmaker/actions/runs/42378215990) succeeded. Its test selections overlap.

## Separate controls

A fresh standard-library-only lifecycle created directories, removed the work directory and renamed the stage. Inotify and inode snapshots showed the old names reappearing in the active workspace. The separate `/var/tmp` control on the visible overlay stayed clear for ten seconds. The control executes no ReelMaker code or media process.

The same six-second native project was traced separately, sequentially, with workspace and alternate output parents. Both produced an independently checked 180-frame package with the same encoded SHA-256. The workspace trace returned 3 for recurrence and the alternate returned 0. The stage's published identity and later name identity, producer and parent PIDs, child reaping, timestamps and inotify events are in the raw evidence. The visible mount namespace was `mnt:[4026532284]`. Unexpected paths were preserved.

The reproduction shows that ReelMaker execution is unnecessary for this behavior on the active path. Inotify supplies events without the writer PID. The guest view and prior denied ptrace probe could not distinguish a synchronizer, workspace restoration, overlay behavior or another writer. Creator and root cause remain **unresolved**. No transaction cleanup changes were warranted by these controls.

## Operational configuration

Use a user-controlled, durable local output parent outside a synchronized workspace and outside `/tmp`, with a fresh destination for each job. The alternate `/var/tmp` path was a bounded local experiment. Confirm retention separately before choosing any production volume. Check parent identity and preflight on that exact volume. Treat recurrence as an ownership investigation and preserve the unexpected paths. The operator must choose the output path explicitly.

The alternate root passed the short smoke and occupied destination hash check. Forty-one focused transaction, native fault and encoder cleanup tests passed under that filesystem, including cancellation and preservation of a replacement sentinel. The guest maps only UID/GID 0. The attempted ordinary-user setup failed at ownership and group changes, so ordinary-user behavior is **NOT TESTED**. Unattended deployment remains open.
