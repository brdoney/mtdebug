import io
import os
import pty
from select import select
import subprocess
from threading import Lock
from typing import cast

from pygdbmi.gdbcontroller import DEFAULT_GDB_LAUNCH_COMMAND
from pygdbmi.constants import DEFAULT_GDB_TIMEOUT_SEC, GdbTimeoutError
from pygdbmi.IoManager import IoManager


class GdbController:
    gdb: IoManager
    gdb_process: subprocess.Popen

    gdbmi_lock: Lock
    """Lock to protect from multiple threads (spawned by flask for each request) issuing
    and reading the results of multiple MI commands concurrently. This will lead to race
    conditions where pygdmi never sees the "done" response for one command and thus
    times out, because a concurrent command has that "done" message in its response."""

    # stdin/out that the gdb instance is using (really just a pseudoterminal)
    # Writing and reading may seem flipped, but remember we are observing the pty
    # NOTE: Only one thread should and does read these at a time currently, but
    # if this changes, then a lock needs to be added
    tui_stdin: io.FileIO
    tui_stdout: io.FileIO

    def __init__(self) -> None:
        self.tui_pty_master, self.tui_pty_slave = pty.openpty()
        gdb_tui_tty_name = os.ttyname(self.tui_pty_slave)
        gdb_tui_pty_name = os.ttyname(self.tui_pty_master)
        print(gdb_tui_pty_name, gdb_tui_tty_name)

        self.gdbmi_lock = Lock()

        self.tui_stdin = os.fdopen(self.tui_pty_master, mode="wb", buffering=0)
        self.tui_stdout = os.fdopen(self.tui_pty_master, mode="rb", buffering=0)

        # Need to start separate TUI on startup + some QOL improvements
        startup_commands = [
            f"new-ui console {gdb_tui_tty_name}",
            "set pagination off",
            "set non-stop on",
            "set debuginfod enabled on",
        ]
        startup_commands_str = [f"-iex={c}" for c in startup_commands]
        command = [*DEFAULT_GDB_LAUNCH_COMMAND, *startup_commands_str]

        # Talk to GDB MI through pipes (like pygdbmi)
        self.gdb_process = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        # Create in/out off of pty and IoManager to interact w/ gdb through MI
        self.gdb = IoManager(
            self.gdb_process.stdin,  # type: ignore
            self.gdb_process.stdout,  # type: ignore
            self.gdb_process.stderr,  # type: ignore
        )

        # Has to be set using mi syntax, which -iex doesn't support?
        # This is so that we can still control other threads while waiting for a mutex
        self.gdb.write("-gdb-set mi-async on")

    def read(
        self,
        timeout_sec: float = DEFAULT_GDB_TIMEOUT_SEC,
        raise_error_on_timeout=True,
        using_mi: bool = True,
    ):
        """
        If we are using MI right now, get and parse GDB response. Otherwise, read
        bytes directly from the pty connected to the gdb instance. See
        `IoManager.get_gdb_response()` for details about flags.

        If `using_mi=False` and the timeout is 0, then this will block until a
        response is ready.
        """
        if using_mi:
            self.gdbmi_lock.acquire()
            try:
                output = self.gdb.get_gdb_response(timeout_sec, raise_error_on_timeout)
            except GdbTimeoutError as e:
                # The operation timed out, but we need other things to continue;
                # this is important for mutexes, where a lock operation will timeout
                # and continue until another thread (which we need to control) continues
                self.gdbmi_lock.release()
                raise e

            self.gdbmi_lock.release()
            return output

        if timeout_sec <= 0:
            return self.tui_stdout.read(1024)

        # Wait for at most `timeout_sec` to read from stdout
        r, _, _ = select([self.tui_stdout], [], [], timeout_sec)

        if self.tui_stdout in r:
            # If there are bytes ready, this will just return them
            # (won't wait for full 1024)
            return self.tui_stdout.read(1024)
        elif raise_error_on_timeout:
            raise GdbTimeoutError(
                f"Did not get response from gdb pty after {timeout_sec} seconds"
            )
        else:
            return None

    def write(
        self,
        data: str | list[str] | bytes,
        timeout_sec=DEFAULT_GDB_TIMEOUT_SEC,
        raise_error_on_timeout: bool = True,
        read_response: bool = True,
        using_mi: bool = True,
    ):
        """
        If we are using MI right now, write using pygdmi. Otherwise, write
        bytes directly to the pty connected to the gdb instance. See
        `IoManager.write()` for details about flags
        """
        if using_mi:
            mi_cmd_to_write = cast(str | list[str], data)
            print(mi_cmd_to_write)

            self.gdbmi_lock.acquire()
            try:
                output = self.gdb.write(
                    mi_cmd_to_write,
                    timeout_sec,
                    raise_error_on_timeout,
                    read_response,
                )
            except GdbTimeoutError as e:
                # The operation timed out, but we need other things to continue;
                # this is important for mutexes, where a lock operation will timeout
                # and continue until another thread (which we need to control) continues
                self.gdbmi_lock.release()
                raise e

            self.gdbmi_lock.release()
            return output

        # We only accept one command (as bytes) at a time for TUI
        data = cast(bytes, data)

        print("Writing:", data)
        bytes_written = self.tui_stdin.write(data)
        print(bytes_written)

        return bytes_written
