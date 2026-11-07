"""
Harness de Emulação de Ambiente Windows 10/11 e Injetor de Falhas (Chaos Engineering).
Intercepta chamadas de sistema, subprocessos (PowerShell WMI, explorer.exe) e injeta
erros de I/O em nível de kernel para simulação realista de discos de sucata e testes de estresse.
"""

import contextlib
import json
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

CAPTURED_EXPLORER_CALLS = []

# Telemetria S.M.A.R.T. Autêntica do Windows PowerShell WMI para Seagate BarraCuda 2TB
MOCK_WINDOWS_PHYSICAL_DISK_JSON = json.dumps([
    {
        "DeviceID": 0,
        "Model": "ST2000DM008-2FR102",
        "SerialNumber": "WFL19824",
        "BusType": "SATA",
        "MediaType": "HDD",
        "Size": 2000398934016,
        "OperationalStatus": "OK",
        "HealthStatus": "Healthy",
        "SpindleSpeed": 7200,
        "Temperature": 34,
        "PowerOnHours": 14280,
    }
])


class MockDirEntry:
    """Wrapper em torno de os.DirEntry para injeção de Chaos Engineering."""

    def __init__(self, real_entry, chaos_injector):
        self._real = real_entry
        self._chaos = chaos_injector
        self.name = real_entry.name
        self.path = real_entry.path

    def is_dir(self, follow_symlinks=False):
        return self._real.is_dir(follow_symlinks=follow_symlinks)

    def is_file(self, follow_symlinks=False):
        return self._real.is_file(follow_symlinks=follow_symlinks)

    def is_symlink(self):
        return self._real.is_symlink()

    def stat(self, follow_symlinks=False):
        p_str = self.path
        self._chaos.files_seen += 1

        if self._chaos.simulate_unplug_after_files > 0 and self._chaos.files_seen >= self._chaos.simulate_unplug_after_files:
            self._chaos.has_unplugged = True
            err = OSError(1167, "The device is not connected.")
            err.winerror = 1167
            raise err

        if "bad_sector_io_error_1117" in p_str or "dead_sector_" in p_str:
            err = OSError(1117, "The request could not be performed because of an I/O device error.")
            err.winerror = 1117
            raise err

        if "bad_sector_crc_error_23" in p_str:
            err = OSError(23, "Data error (cyclic redundancy check).")
            err.winerror = 23
            raise err

        return self._real.stat(follow_symlinks=follow_symlinks)


class MockScandirContext:
    """Context manager retornado pelo os.scandir mockado."""

    def __init__(self, real_context, chaos_injector):
        self._real_context = real_context
        self._chaos = chaos_injector
        self._iter = None

    def __enter__(self):
        self._iter = self._real_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._real_context.__exit__(exc_type, exc_val, exc_tb)

    def __iter__(self):
        return self

    def __next__(self):
        real_entry = next(self._iter)
        return MockDirEntry(real_entry, self._chaos)


class ChaosInjector:
    """
    Injeta erros de hardware em chamadas de I/O de disco para arquivos específicos
    (WinError 1117, WinError 23, WinError 5, WinError 1167).
    """

    def __init__(self, simulate_unplug_after_files: int = 0) -> None:
        self.original_stat = os.stat
        self.original_scandir = os.scandir
        self.files_seen = 0
        self.simulate_unplug_after_files = simulate_unplug_after_files
        self.has_unplugged = False

    def __enter__(self):
        def patched_stat(path, *args, **kwargs):
            p_str = str(path)
            self.files_seen += 1

            if self.simulate_unplug_after_files > 0 and self.files_seen >= self.simulate_unplug_after_files:
                self.has_unplugged = True
                err = OSError(1167, "The device is not connected.")
                err.winerror = 1167
                raise err

            if "bad_sector_io_error_1117" in p_str or "dead_sector_" in p_str:
                err = OSError(1117, "The request could not be performed because of an I/O device error.")
                err.winerror = 1117
                raise err

            if "bad_sector_crc_error_23" in p_str:
                err = OSError(23, "Data error (cyclic redundancy check).")
                err.winerror = 23
                raise err

            return self.original_stat(path, *args, **kwargs)

        def patched_scandir(path):
            real_ctx = self.original_scandir(path)
            return MockScandirContext(real_ctx, self)

        self._patcher_stat = patch("os.stat", side_effect=patched_stat)
        self._patcher_scandir = patch("os.scandir", side_effect=patched_scandir)
        self._patcher_stat.start()
        self._patcher_scandir.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._patcher_scandir.stop()
        self._patcher_stat.stop()


@contextlib.contextmanager
def patch_windows_environment():
    """
    Simula perfeitamente o ambiente Windows 10/11:
    - sys.platform = 'win32'
    - Intercepta chamadas de subprocess.Popen (explorer.exe)
    - Intercepta chamadas de subprocess.run (PowerShell WMI)
    """
    global CAPTURED_EXPLORER_CALLS
    CAPTURED_EXPLORER_CALLS.clear()

    orig_popen = subprocess.Popen
    orig_run = subprocess.run

    def mock_popen(args, *p_args, **p_kwargs):
        cmd_str = args if isinstance(args, str) else " ".join(args)
        if "explorer.exe" in cmd_str:
            CAPTURED_EXPLORER_CALLS.append(cmd_str)
            mock_proc = MagicMock()
            mock_proc.pid = 9999
            mock_proc.poll.return_value = 0
            return mock_proc
        return orig_popen(args, *p_args, **p_kwargs)

    def mock_run(args, *r_args, **r_kwargs):
        cmd_str = args if isinstance(args, str) else " ".join(str(a) for a in args)
        # Se for consulta PowerShell de disco
        if "Get-Disk" in cmd_str or "Get-PhysicalDisk" in cmd_str or "MSStorageDriver_ATAPISmartData" in cmd_str:
            mock_res = MagicMock()
            mock_res.returncode = 0
            mock_res.stdout = MOCK_WINDOWS_PHYSICAL_DISK_JSON
            mock_res.stderr = ""
            return mock_res
        return orig_run(args, *r_args, **r_kwargs)

    with patch("sys.platform", "win32"), \
         patch("subprocess.Popen", side_effect=mock_popen), \
         patch("subprocess.run", side_effect=mock_run):
        yield
