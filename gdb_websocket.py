import io
import os
import pty
import signal
import subprocess
from typing import cast

from pygdbmi.gdbcontroller import DEFAULT_GDB_LAUNCH_COMMAND
from pygdbmi.constants import DEFAULT_GDB_TIMEOUT_SEC
from pygdbmi.IoManager import IoManager


class GdbController:
    gdb: IoManager
    gdb_process: subprocess.Popen

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

        self.using_mi = True

    def read(
        self,
        timeout_sec: float = DEFAULT_GDB_TIMEOUT_SEC,
        raise_error_on_timeout=True,
        using_mi: bool = True,
    ):
        """
        If we are using MI right now, get and parse GDB response. Otherwise, read
        bytes directly from the pty connected to the gdb instance. See
        `IoManager.get_gdb_response()` for details about flags
        """
        if using_mi:
            return self.gdb.get_gdb_response(timeout_sec, raise_error_on_timeout)
        return self.tui_stdout.read()

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
