"""Explicit ownership for a single private directory; never reacquire a removed pathname."""

import ctypes
import errno
import os
import shutil
import stat
import tempfile
from pathlib import Path

from .errors import OperationError


class OwnedDirectory:
    """Own one inode through cleanup, with no GC finalizer or previous-job reconciliation."""

    def __init__(self, parent: Path, prefix: str, *, files: frozenset[str] | None = None):
        parent = parent.resolve()
        self._parent_identity = self._key(parent.stat())
        self.path = Path(tempfile.mkdtemp(dir=parent, prefix=prefix))
        self._fd = os.open(self.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        self._identity = self._key(os.fstat(self._fd))
        self._files = files
        self._attempted = False
        self._error: OperationError | None = None

    @staticmethod
    def _key(info: os.stat_result) -> tuple[int, int]:
        return info.st_dev, info.st_ino

    def assert_absent(self) -> None:
        try:
            self.path.lstat()
        except FileNotFoundError:
            return
        except OSError as error:
            raise OperationError(
                "TRANSACTION_CLEANUP", f"Cannot confirm transaction absence: {self.path}"
            ) from error
        raise OperationError(
            "TRANSACTION_CLEANUP", f"Completed transaction path reappeared: {self.path}"
        )

    def confirm_cleanup(self) -> None:
        """Confirm a completed removal without ever attempting deletion."""
        if self._error is not None:
            raise self._error
        if not self._attempted:
            raise OperationError("TRANSACTION_CLEANUP", "Private directory cleanup did not run")
        self.assert_absent()

    def publish_as(self, destination: Path) -> None:
        """Commit a complete package using the Linux no-replacement directory rename."""
        if self._attempted or destination.parent != self.path.parent:
            raise OperationError("TRANSACTION_PUBLISH", "Publish a live directory to a sibling")
        parent_fd = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            source = os.stat(self.path.name, dir_fd=parent_fd, follow_symlinks=False)
            if (self._key(os.fstat(parent_fd)) != self._parent_identity
                    or self._key(source) != self._identity or not stat.S_ISDIR(source.st_mode)):
                raise OperationError("TRANSACTION_IDENTITY", "Private directory identity changed")
            rename = getattr(ctypes.CDLL(None, use_errno=True), "renameat2", None)
            if rename is None:
                raise OperationError("TRANSACTION_PLATFORM", "Linux renameat2 is required")
            rename.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                               ctypes.c_char_p, ctypes.c_uint)
            rename.restype = ctypes.c_int
            if rename(parent_fd, os.fsencode(self.path.name), parent_fd,
                      os.fsencode(destination.name), 1):
                error = ctypes.get_errno()
                if error in (errno.EEXIST, errno.ENOTEMPTY):
                    raise OperationError("OUTPUT_EXISTS", "Choose a new output directory")
                raise OperationError("TRANSACTION_PUBLISH", os.strerror(error))
            self._attempted = True
            os.close(self._fd)
        finally:
            os.close(parent_fd)

    def cleanup(self) -> None:
        if self._attempted:
            self.confirm_cleanup()
            return
        self._attempted = True
        try:
            # Hold the original directory fd until removal completes. A new inode at the
            # same pathname is a different owner, even if its name has our private prefix.
            if self._key(self.path.lstat()) != self._identity or self.path.is_symlink():
                raise OperationError(
                    "TRANSACTION_IDENTITY", f"Private directory identity changed: {self.path}"
                )
            if self._files is not None:
                entries = tuple(self.path.iterdir())
                if any(
                    p.name not in self._files or not p.is_file() or p.is_symlink() for p in entries
                ):
                    raise OperationError(
                        "TRANSACTION_CONTENT", f"Unexpected private directory content: {self.path}"
                    )
                for entry in entries:
                    os.unlink(entry.name, dir_fd=self._fd)
            else:
                # Python's fd-based rmtree does not traverse directory symlinks. It removes
                # only this invocation's owned subtree, after supervised children are reaped.
                if not shutil.rmtree.avoids_symlink_attacks:
                    raise OperationError("TRANSACTION_PLATFORM", "FD-safe cleanup is required")
                for name in os.listdir(self._fd):
                    info = os.stat(name, dir_fd=self._fd, follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        shutil.rmtree(name, dir_fd=self._fd)
                    else:
                        os.unlink(name, dir_fd=self._fd)
            if self._key(self.path.lstat()) != self._identity or self.path.is_symlink():
                raise OperationError("TRANSACTION_IDENTITY", "Directory changed during cleanup")
            os.rmdir(self.path)
            self.assert_absent()
        except (OSError, OperationError) as error:
            self._error = (
                error
                if isinstance(error, OperationError)
                else OperationError(
                    "TRANSACTION_CLEANUP", f"Cannot remove owned directory: {self.path}"
                )
            )
            if self._error is error:
                raise
            raise self._error from error
        finally:
            os.close(self._fd)
