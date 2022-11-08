import io
import os
import pty
import signal
from typing import cast

from pygdbmi.gdbcontroller import DEFAULT_GDB_LAUNCH_COMMAND
from pygdbmi.constants import DEFAULT_GDB_TIMEOUT_SEC
from pygdbmi.IoManager import IoManager


class GdbController:
    gdb: IoManager
    gdb_pid: int
    using_mi: bool

    # stdin/out that the gdb instance is using (really just a pseudoterminal)
    # Writing and reading may seem flipped, but remember we are observing the pty
    tui_stdin: io.BufferedWriter
    tui_stdout: io.BufferedReader

    # # Pty information for console input/output (os opposed to MI)
    # tui_pty_master: int
    # tui_pty_slave: int

    def __init__(self) -> None:
        self.tui_pty_master, self.tui_pty_slave = pty.openpty()
        gdb_tui_tty_name = os.ttyname(self.tui_pty_slave)

        self.tui_stdin = os.fdopen(self.tui_pty_master, mode="wb")
        self.tui_stdout = os.fdopen(self.tui_pty_master, mode="rb")

        startup_commands = [
            f"new-ui console {gdb_tui_tty_name}",
            "set pagination off",
            "set debuginfod enabled on",
        ]
        startup_commands_str = [f"-iex={c}" for c in startup_commands]
        command = [*DEFAULT_GDB_LAUNCH_COMMAND, *startup_commands_str]
        command = DEFAULT_GDB_LAUNCH_COMMAND
        print(command)

        pid, termfd = pty.fork()

        if pid == 0:
            # Child: start gdb
            os.execvp(command[0], command)

        # Parent: record the info
        self.gdb_pid = pid

        # Create in/out off of pty and IoManager to interact w/ gdb through MI
        self.gdb = IoManager(
            os.fdopen(termfd, mode="wb"),
            os.fdopen(termfd, mode="rb"),
            None,
        )

        self.using_mi = True

    def terminate(self):
        """
        Kill the GDB process we're controlling and ensure that future calls to read and
        write will fail.
        """
        if self.gdb is not None:
            os.kill(self.gdb_pid, signal.SIGKILL)
            self.gdb = None  # type: ignore
            self.gdb_pid = -1
            self.mi_stdin = None  # type: ignore
            self.mi_stdout = None  # type: ignore

    def set_mi(self, using_mi: bool) -> None:
        """Set whether we are using GDB's MI to influence what read and write do."""
        self.using_mi = using_mi

    def read(
        self, timeout_sec: float = DEFAULT_GDB_TIMEOUT_SEC, raise_error_on_timeout=True
    ):
        """
        If we are using MI right now, get and parse GDB response. Otherwise, read
        bytes directly from the pty connected to the gdb instance. See
        `IoManager.get_gdb_response()` for details about flags
        """
        if self.using_mi:
            return self.gdb.get_gdb_response(timeout_sec, raise_error_on_timeout)
        return self.tui_stdout.read()

    def write(
        self,
        data: str | list[str] | bytes,
        timeout_sec=DEFAULT_GDB_TIMEOUT_SEC,
        raise_error_on_timeout: bool = True,
        read_response: bool = True,
    ):
        """
        If we are using MI right now, write using pygdmi. Otherwise, write
        bytes directly to the pty connected to the gdb instance. See
        `IoManager.write()` for details about flags
        """
        if self.using_mi:
            mi_cmd_to_write = cast(str | list[str], data)
            print(mi_cmd_to_write)
            return self.gdb.write(
                mi_cmd_to_write,
                timeout_sec,
                raise_error_on_timeout,
                read_response,
            )
        # It's only a list of commands if we're using MI, but we're not
        data = cast(bytes, data)
        return self.tui_stdin.write(data)


# async def watch_gdb(gdb: IoManager) -> None:
#     while True:
#         gdb._buffer_incomplete_responses
