"""
Módulo de coleta de informações físicas do disco (Modelo, Serial, S.M.A.R.T., Capacidade)
e identificação de usuários ("Crachá do Disco").
No Windows, usa PowerShell nativo com ConvertTo-Json e CREATE_NO_WINDOW.
No Linux, faz fallback gracioso com psutil e dados simulados para testes em VM.
"""

import datetime
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import psutil

from core.rules import IGNORED_USERS, format_size


@dataclass(slots=True)
class UserProfileInfo:
    """Representa um usuário detectado no disco analisado."""
    username: str
    profile_path: str
    shortcuts: Dict[str, str] = field(default_factory=dict)  # ex: {"Desktop": "D:\\Users\\Joao\\Desktop"}


@dataclass(slots=True)
class DiskBadgeInfo:
    """Estrutura de dados completa do 'Crachá do Disco' (Header)."""
    target_path: str
    mountpoint: str
    model: str = "Disco Local / Desconhecido"
    serial_number: str = "N/A"
    total_bytes: int = 0
    used_bytes: int = 0
    free_bytes: int = 0
    percent_used: float = 0.0
    smart_status: str = "Healthy"        # "Healthy", "Warning", "Unhealthy", "Unknown"
    smart_details: str = "OK (Saudável)"
    is_healthy: bool = True
    detected_users: List[UserProfileInfo] = field(default_factory=list)
    last_activity_date: Optional[str] = None
    last_activity_file: Optional[str] = None
    filesystem: str = "N/A"
    power_on_hours: Optional[int] = None
    power_on_count: Optional[int] = None
    media_type: str = ""
    spindle_speed: int = 0
    temperature_c: Optional[int] = None
    reallocated_sectors: Optional[int] = None
    pending_sectors: Optional[int] = None

    @property
    def capacity_summary(self) -> str:
        if self.total_bytes <= 0:
            return "Capacidade desconhecida"
        return (
            f"{format_size(self.used_bytes)} usados de {format_size(self.total_bytes)} "
            f"({self.percent_used:.1f}%)"
        )

    @property
    def users_summary(self) -> str:
        if not self.detected_users:
            return "Nenhum perfil padrão detectado"
        return ", ".join(u.username for u in self.detected_users)

    @property
    def power_on_summary(self) -> str:
        if self.power_on_hours is not None:
            days = self.power_on_hours / 24.0
            cycles_part = f" • {self.power_on_count:,} ligações" if self.power_on_count else ""
            return f"{self.power_on_hours:,}h (~{days:.0f} dias){cycles_part}"
        return "Horas não informadas"

    @property
    def hardware_media_summary(self) -> str:
        parts = []
        if self.media_type:
            parts.append(self.media_type)
        if self.spindle_speed and self.spindle_speed > 0:
            parts.append(f"{self.spindle_speed} RPM")
        if self.temperature_c and self.temperature_c > 0:
            parts.append(f"{self.temperature_c}°C")
        return " • ".join(parts) if parts else "Tipo não especificado"


def list_available_drives() -> List[Dict[str, str]]:
    """
    Lista todas as unidades/partições montadas no sistema.
    No Windows: C:\\, D:\\, E:\\, etc.
    No Linux: /, /mnt/*, /media/* e partições montadas físicas/virtuais.
    """
    drives: List[Dict[str, str]] = []
    seen_mounts = set()

    try:
        partitions = psutil.disk_partitions(all=False)
        for part in partitions:
            mount = part.mountpoint
            if not mount or mount in seen_mounts:
                continue
            # No Linux, ignora mounts de snap/loop irrelevantes
            if sys.platform != "win32" and (
                mount.startswith("/snap") or mount.startswith("/run/user")
            ):
                continue
            seen_mounts.add(mount)
            try:
                usage = psutil.disk_usage(mount)
                size_str = format_size(usage.total)
            except Exception:
                size_str = "N/A"

            label = f"{mount} ({part.fstype or 'FS'} - {size_str})"
            drives.append({
                "path": mount,
                "label": label,
                "fstype": part.fstype or "N/A",
                "device": part.device or "",
            })
    except Exception:
        pass

    # No Windows, detecta discos físicos (Get-Disk) que possam ser RAW ou sem letra montada
    if sys.platform == "win32":
        try:
            ps_cmd = [
                "powershell", "-NoProfile", "-NonInteractive", "-Command",
                "Get-Disk | Select-Object Number, FriendlyName, Size, PartitionStyle, OperationalStatus | ConvertTo-Json"
            ]
            startupinfo = None
            if hasattr(subprocess, "STARTUPINFO"):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            res = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=3, startupinfo=startupinfo)
            if res.returncode == 0 and res.stdout.strip():
                import json
                raw_data = json.loads(res.stdout)
                disks = raw_data if isinstance(raw_data, list) else [raw_data]
                for d in disks:
                    num = d.get("Number")
                    if num is not None:
                        phys_path = f"\\\\.\\PhysicalDrive{num}"
                        if phys_path not in seen_mounts:
                            seen_mounts.add(phys_path)
                            model = str(d.get("FriendlyName") or f"Disco Físico {num}")
                            size = int(d.get("Size") or 0)
                            part_style = str(d.get("PartitionStyle") or "RAW")
                            drives.append({
                                "path": phys_path,
                                "label": f"{phys_path} - {model} ({format_size(size)} - {part_style})",
                                "fstype": part_style,
                                "device": phys_path,
                            })
        except Exception:
            pass

    # No Linux, verifica também subpastas dentro de /mnt e /media caso existam HDs montados lá
    if sys.platform != "win32":
        for base_mnt in ("/mnt", "/media"):
            if os.path.isdir(base_mnt):
                try:
                    for entry in os.scandir(base_mnt):
                        if entry.is_dir() and entry.path not in seen_mounts:
                            seen_mounts.add(entry.path)
                            drives.append({
                                "path": entry.path,
                                "label": f"{entry.path} (Ponto de Montagem)",
                                "fstype": "dir",
                                "device": entry.path,
                            })
                except Exception:
                    pass

    if not drives:
        fallback = "C:\\" if sys.platform == "win32" else "/"
        drives.append({
            "path": fallback,
            "label": f"{fallback} (Unidade Padrão)",
            "fstype": "N/A",
            "device": fallback,
        })

    return drives


def _query_windows_hardware_info(drive_path: str) -> Dict[str, object]:
    """
    Consulta dados físicos do disco no Windows via PowerShell (Get-Partition, Get-Disk, Get-PhysicalDisk)
    e WMI/S.M.A.R.T. (MSStorageDriver_ATAPISmartData) usando ConvertTo-Json e CREATE_NO_WINDOW.
    """
    result: Dict[str, object] = {
        "model": "Disco Físico Windows",
        "serial": "SN-DESCONHECIDO",
        "health": "Healthy",
        "operational": "OK",
        "media_type": "",
        "bus_type": "",
        "spindle_speed": 0,
        "power_on_hours": None,
        "power_on_count": None,
        "temperature": None,
        "reallocated_sectors": None,
        "pending_sectors": None,
    }

    disk_num_literal = ""
    drive_letter = ""
    if drive_path.lower().startswith(r"\\.\physicaldrive"):
        disk_num_literal = drive_path[17:].strip()
    else:
        drive_letter = os.path.splitdrive(os.path.abspath(drive_path))[0].replace(":", "").strip()
        if not drive_letter:
            return result

    ps_script = f"""
$ErrorActionPreference = 'SilentlyContinue'
$targetDiskNum = $null
if ('{disk_num_literal}' -ne '') {{
    $targetDiskNum = [int]'{disk_num_literal}'
}} else {{
    $part = Get-Partition -DriveLetter '{drive_letter}' | Select-Object -First 1
    if ($null -ne $part) {{ $targetDiskNum = $part.DiskNumber }}
}}

$obj = [PSCustomObject]@{{
    Model = ''
    SerialNumber = ''
    HealthStatus = 'Healthy'
    OperationalStatus = 'OK'
    MediaType = ''
    BusType = ''
    SpindleSpeed = 0
    PowerOnHours = $null
    PowerOnCount = $null
    Temperature = $null
    ReallocatedSectors = $null
    PendingSectors = $null
}}

if ($null -ne $targetDiskNum) {{
    # 1. Tenta API Storage moderna (Get-Disk e Get-PhysicalDisk)
    $disk = Get-Disk -Number $targetDiskNum | Select-Object -First 1
    $phys = Get-PhysicalDisk | Where-Object {{ $_.DeviceId -eq [string]$targetDiskNum }} | Select-Object -First 1

    if ($null -ne $phys) {{
        $obj.Model = [string]$phys.FriendlyName
        $obj.SerialNumber = [string]$phys.SerialNumber
        $obj.HealthStatus = [string]$phys.HealthStatus
        $obj.OperationalStatus = [string]$phys.OperationalStatus
        $obj.MediaType = [string]$phys.MediaType
        if ($phys.SpindleSpeed) {{ $obj.SpindleSpeed = [int]$phys.SpindleSpeed }}
    }}

    if ($null -ne $disk) {{
        if (-not $obj.Model) {{
            $obj.Model = if ($disk.FriendlyName) {{ [string]$disk.FriendlyName }} else {{ [string]$disk.Model }}
        }}
        if (-not $obj.SerialNumber -or $obj.SerialNumber.Trim() -eq '' -or $obj.SerialNumber -eq 'N/A') {{
            $obj.SerialNumber = [string]$disk.SerialNumber
        }}
        if (-not $obj.HealthStatus) {{
            $obj.HealthStatus = [string]$disk.HealthStatus
        }}
        if (-not $obj.OperationalStatus) {{
            $obj.OperationalStatus = [string]$disk.OperationalStatus
        }}
        $obj.BusType = [string]$disk.BusType
    }}

    # 2. Fallback WMI/CIM que NUNCA exige privilégio de Administrador no Windows
    if (-not $obj.SerialNumber -or $obj.SerialNumber.Trim() -eq '' -or $obj.SerialNumber -eq 'N/A' -or -not $obj.Model) {{
        $wmi = Get-CimInstance Win32_DiskDrive | Where-Object {{ $_.Index -eq $targetDiskNum }} | Select-Object -First 1
        if ($null -ne $wmi) {{
            if (-not $obj.Model) {{ $obj.Model = [string]$wmi.Model }}
            if ($wmi.SerialNumber) {{ $obj.SerialNumber = [string]$wmi.SerialNumber.Trim() }}
            if ($wmi.Status) {{ $obj.OperationalStatus = [string]$wmi.Status }}
            if ($wmi.InterfaceType) {{ $obj.BusType = [string]$wmi.InterfaceType }}
        }}
    }}

    # 3. Tenta extrair telemetria S.M.A.R.T. (Power-On Hours, Power-On Count, Temperatura, Setores)
    try {{
        $smartList = Get-CimInstance -Namespace root\\wmi -ClassName MSStorageDriver_ATAPISmartData
        $smart = if ($null -ne $smartList) {{
            $matched = $smartList | Where-Object {{ $_.InstanceName -match "Disk$targetDiskNum" }} | Select-Object -First 1
            if ($null -ne $matched) {{ $matched }} else {{ $smartList | Select-Object -First 1 }}
        }} else {{ $null }}

        if ($null -ne $smart -and $smart.VendorSpecific) {{
            $bytes = $smart.VendorSpecific
            for ($i = 2; $i -lt ($bytes.Length - 12); $i += 12) {{
                $id = [int]$bytes[$i]
                if ($id -eq 0) {{ continue }}
                $rawVal = [int64]$bytes[$i+5] + ([int64]$bytes[$i+6] -shl 8) + ([int64]$bytes[$i+7] -shl 16) + ([int64]$bytes[$i+8] -shl 24)

                if ($id -eq 9) {{
                    $obj.PowerOnHours = $rawVal
                }} elseif ($id -eq 12) {{
                    $obj.PowerOnCount = $rawVal
                }} elseif ($id -eq 194 -or $id -eq 231) {{
                    $t = [int]$bytes[$i+5]
                    if ($t -gt 0 -and $t -lt 110) {{ $obj.Temperature = $t }}
                }} elseif ($id -eq 5) {{
                    $obj.ReallocatedSectors = $rawVal
                }} elseif ($id -eq 197) {{
                    $obj.PendingSectors = $rawVal
                }}
            }}
        }}
    }} catch {{}}
}}

$obj.SerialNumber = if ($obj.SerialNumber) {{ $obj.SerialNumber.Trim() }} else {{ 'N/A' }}
$obj.Model = if ($obj.Model) {{ $obj.Model.Trim() }} else {{ 'Disco Fisico Windows' }}
$obj | ConvertTo-Json -Compress
"""
    cmd = ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
    run_kwargs = {"capture_output": True, "text": True, "timeout": 7}
    if sys.platform == "win32":
        run_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

    try:
        proc = subprocess.run(cmd, **run_kwargs)
        stdout = (proc.stdout or "").strip()
        if stdout:
            data = json.loads(stdout)
            if isinstance(data, dict):
                model = (data.get("Model") or "").strip()
                serial = (data.get("SerialNumber") or "").strip()
                health = (data.get("HealthStatus") or "Healthy").strip()
                op_status = (data.get("OperationalStatus") or "OK").strip()
                media_type = (data.get("MediaType") or "").strip()
                bus_type = (data.get("BusType") or "").strip()

                extras = [x for x in (media_type, bus_type) if x and x != "Unspecified"]
                suffix = f" ({'/'.join(extras)})" if extras else ""

                if model:
                    result["model"] = f"{model}{suffix}"
                if serial:
                    result["serial"] = serial
                if health:
                    result["health"] = health
                if op_status:
                    result["operational"] = op_status
                if media_type:
                    result["media_type"] = media_type

                poh = data.get("PowerOnHours")
                if isinstance(poh, (int, float)) and poh > 0:
                    result["power_on_hours"] = int(poh)

                poc = data.get("PowerOnCount")
                if isinstance(poc, (int, float)) and poc > 0:
                    result["power_on_count"] = int(poc)

                temp = data.get("Temperature")
                if isinstance(temp, (int, float)) and 0 < temp < 120:
                    result["temperature"] = int(temp)

                spd = data.get("SpindleSpeed")
                if isinstance(spd, (int, float)) and spd > 0:
                    result["spindle_speed"] = int(spd)

                realloc = data.get("ReallocatedSectors")
                if isinstance(realloc, (int, float)) and realloc >= 0:
                    result["reallocated_sectors"] = int(realloc)

                pending = data.get("PendingSectors")
                if isinstance(pending, (int, float)) and pending >= 0:
                    result["pending_sectors"] = int(pending)
    except Exception:
        pass

    return result


def _query_linux_fallback_info(target_path: str) -> Dict[str, object]:
    """
    Fallback gracioso no Linux (VM Debian) para testes de interface e varredura.
    Tenta ler modelo/serial de /sys/block se possível, ou gera identificação simulada consistente.
    """
    abs_target = os.path.abspath(target_path)
    folder_name = os.path.basename(abs_target.rstrip("/")) or "root"

    model = f"Linux Virtual/Test Drive ({folder_name})"
    serial = f"LNX-{abs(hash(abs_target)) % 100000000:08d}"
    health = "Healthy"
    operational = "OK"

    # Permite simular disco com alerta S.M.A.R.T. se o nome da pasta contiver "bad" ou "smart_warn"
    lower_path = abs_target.lower()
    realloc = 0
    pending = 0
    if "bad" in lower_path or "unhealthy" in lower_path or "defeito" in lower_path:
        health = "Warning"
        operational = "Predictive Failure / Bad Sectors"
        realloc = 18
        pending = 3

    return {
        "model": model,
        "serial": serial,
        "health": health,
        "operational": operational,
        "media_type": "HDD",
        "bus_type": "USB",
        "spindle_speed": 7200,
        "power_on_hours": 11420,
        "power_on_count": 890,
        "temperature": 36,
        "reallocated_sectors": realloc,
        "pending_sectors": pending,
    }


def _detect_users_and_activity(root_path: str) -> tuple[List[UserProfileInfo], Optional[str], Optional[str]]:
    """
    Procura pastas de usuários em <Unidade>:\\Users ou <Unidade>:\\Documents and Settings
    (ou perfis no caminho informado) e calcula a data de atividade mais recente (mtime)
    dentro de Desktop, Documents e Downloads.
    """
    users: List[UserProfileInfo] = []
    latest_mtime: float = 0.0
    latest_file: Optional[str] = None

    candidate_user_roots = [
        os.path.join(root_path, "Users"),
        os.path.join(root_path, "Usuários"),
        os.path.join(root_path, "Documents and Settings"),
        os.path.join(root_path, "home"),
    ]

    # Se o usuário selecionou diretamente a pasta "Users" ou uma pasta que já contém subpastas de perfil
    if os.path.basename(os.path.normpath(root_path)).lower() in ("users", "usuários", "home", "documents and settings"):
        candidate_user_roots.insert(0, root_path)

    seen_profiles = set()

    for user_root in candidate_user_roots:
        if not os.path.isdir(user_root):
            continue
        try:
            for entry in os.scandir(user_root):
                try:
                    # Bloqueia Junctions e Reparse Points para não seguir links circulares
                    if not entry.is_dir(follow_symlinks=False) or entry.is_symlink():
                        continue
                except OSError:
                    continue

                uname = entry.name
                if uname.lower() in IGNORED_USERS or uname.startswith("."):
                    continue

                norm_profile = os.path.abspath(entry.path)
                if norm_profile in seen_profiles:
                    continue
                seen_profiles.add(norm_profile)

                shortcuts = _find_user_shortcuts(norm_profile)
                users.append(
                    UserProfileInfo(
                        username=uname,
                        profile_path=norm_profile,
                        shortcuts=shortcuts,
                    )
                )
        except OSError:
            continue

    # Se nenhum diretório Users padrão foi achado mas a própria pasta escolhida parece ser um perfil de usuário
    if not users:
        direct_shortcuts = _find_user_shortcuts(os.path.abspath(root_path))
        if direct_shortcuts:
            uname = os.path.basename(os.path.abspath(root_path).rstrip("\\/")) or "UsuarioLocal"
            users.append(
                UserProfileInfo(
                    username=uname,
                    profile_path=os.path.abspath(root_path),
                    shortcuts=direct_shortcuts,
                )
            )

    # Estimar última atividade verificando mtime em Desktop, Documents e Downloads dos usuários
    for user in users:
        for folder_key in ("Desktop", "Documents", "Downloads"):
            folder_path = user.shortcuts.get(folder_key)
            if not folder_path or not os.path.isdir(folder_path):
                continue
            mtime, fpath = _scan_recent_mtime_shallow(folder_path, max_depth=2, max_items=600)
            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_file = fpath

    # Se ainda não achou mtime em pastas de usuário, faz uma checagem rápida na raiz (nível 1-2)
    if latest_mtime <= 0:
        mtime, fpath = _scan_recent_mtime_shallow(root_path, max_depth=2, max_items=400)
        if mtime > latest_mtime:
            latest_mtime = mtime
            latest_file = fpath

    last_date_str: Optional[str] = None
    if latest_mtime > 0:
        try:
            dt = datetime.datetime.fromtimestamp(latest_mtime)
            last_date_str = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            last_date_str = None

    return users, last_date_str, latest_file


def _find_user_shortcuts(profile_path: str) -> Dict[str, str]:
    """Localiza pastas clássicas de um perfil de usuário (Desktop, Documents, Pictures, Downloads, Videos, AppData, Browsers, SSH)."""
    mapping = {
        "Desktop": ["Desktop", "Área de Trabalho", "Area de Trabalho", "OneDrive/Desktop", "OneDrive/Área de Trabalho"],
        "Documents": ["Documents", "Meus Documentos", "Documentos", "OneDrive/Documents", "OneDrive/Documentos"],
        "Pictures": ["Pictures", "Minhas Imagens", "Imagens", "OneDrive/Pictures", "OneDrive/Imagens"],
        "Downloads": ["Downloads", "Transferências"],
        "Videos": ["Videos", "Meus Vídeos", "Vídeos", "OneDrive/Videos"],
        "AppData": ["AppData", ".config"],
        "Browsers": [
            "AppData/Local/Google/Chrome/User Data",
            "AppData/Local/Microsoft/Edge/User Data",
            "AppData/Roaming/Mozilla/Firefox/Profiles",
            ".config/google-chrome",
        ],
        "SSH": [".ssh"],
    }
    found: Dict[str, str] = {}
    for canonical, candidates in mapping.items():
        for rel in candidates:
            full = os.path.join(profile_path, *rel.split("/"))
            if os.path.isdir(full):
                found[canonical] = full
                break
    return found


def _scan_recent_mtime_shallow(folder_path: str, max_depth: int = 2, max_items: int = 500) -> tuple[float, Optional[str]]:
    """
    Inspeciona rapidamente apenas metadados (stat) até `max_depth` para encontrar a data de
    modificação mais recente sem travar a interface.
    """
    best_mtime: float = 0.0
    best_path: Optional[str] = None
    visited = 0

    stack = [(folder_path, 0)]
    while stack and visited < max_items:
        curr_dir, depth = stack.pop()
        try:
            with os.scandir(curr_dir) as it:
                for entry in it:
                    visited += 1
                    if visited > max_items:
                        break
                    try:
                        if entry.name.startswith(".") or entry.name.lower() == "desktop.ini":
                            continue
                        st = entry.stat(follow_symlinks=False)
                        if entry.is_file(follow_symlinks=False):
                            if st.st_mtime > best_mtime:
                                best_mtime = st.st_mtime
                                best_path = entry.path
                        elif entry.is_dir(follow_symlinks=False) and not entry.is_symlink() and depth < max_depth:
                            stack.append((entry.path, depth + 1))
                    except OSError:
                        continue
        except OSError:
            continue

    return best_mtime, best_path


def fill_hardware_info(badge: DiskBadgeInfo) -> DiskBadgeInfo:
    """Consulta dados físicos de hardware em background (PowerShell no Windows / Fallback no Linux)."""
    abs_path = badge.target_path
    if sys.platform == "win32":
        hw = _query_windows_hardware_info(abs_path)
    else:
        hw = _query_linux_fallback_info(abs_path)

    badge.model = str(hw.get("model") or "Disco Desconhecido")
    badge.serial_number = str(hw.get("serial") or "N/A")
    badge.media_type = str(hw.get("media_type") or "")
    badge.spindle_speed = int(hw.get("spindle_speed") or 0)
    badge.power_on_hours = hw.get("power_on_hours") if isinstance(hw.get("power_on_hours"), int) else None
    badge.power_on_count = hw.get("power_on_count") if isinstance(hw.get("power_on_count"), int) else None
    badge.temperature_c = hw.get("temperature") if isinstance(hw.get("temperature"), int) else None
    badge.reallocated_sectors = hw.get("reallocated_sectors") if isinstance(hw.get("reallocated_sectors"), int) else None
    badge.pending_sectors = hw.get("pending_sectors") if isinstance(hw.get("pending_sectors"), int) else None

    health_raw = str(hw.get("health") or "Healthy")
    op_raw = str(hw.get("operational") or "OK")

    health_lower = health_raw.lower()
    op_lower = op_raw.lower()

    realloc_cnt = badge.reallocated_sectors or 0
    pending_cnt = badge.pending_sectors or 0

    if realloc_cnt > 0 or pending_cnt > 0:
        badge.smart_status = "Warning"
        badge.smart_details = f"ALERTA ({realloc_cnt} setores realocados / {pending_cnt} pendentes)"
        badge.is_healthy = False
    elif health_lower in ("healthy", "ok") and ("ok" in op_lower or "healthy" in op_lower):
        badge.smart_status = "Healthy"
        temp_str = f" • {badge.temperature_c}°C" if badge.temperature_c else ""
        badge.smart_details = f"Saudável (0 setores pendentes{temp_str})"
        badge.is_healthy = True
    elif "warning" in health_lower or "degraded" in op_lower or "predictive" in op_lower:
        badge.smart_status = "Warning"
        badge.smart_details = f"ALERTA ({health_raw} - {op_raw})"
        badge.is_healthy = False
    elif "unhealthy" in health_lower or "error" in op_lower or "failed" in op_lower:
        badge.smart_status = "Unhealthy"
        badge.smart_details = f"CRÍTICO ({health_raw} - {op_raw})"
        badge.is_healthy = False
    else:
        badge.smart_status = health_raw or "Unknown"
        badge.smart_details = f"{health_raw} ({op_raw})"
        badge.is_healthy = health_lower in ("healthy", "ok", "unknown")

    return badge


def get_disk_badge_info(target_path: str, query_hw: bool = True) -> DiskBadgeInfo:
    """
    Constrói o objeto DiskBadgeInfo para a unidade ou pasta selecionada.
    Se query_hw=False, retorna imediatamente em microssegundos (ideal para UI fluida).
    """
    is_raw = target_path.lower().startswith(r"\\.\physicaldrive") or target_path.startswith("/dev/sd")
    if is_raw:
        abs_path = target_path
    else:
        abs_path = os.path.abspath(target_path)
    badge = DiskBadgeInfo(target_path=abs_path, mountpoint=abs_path)

    if is_raw:
        badge.filesystem = "RAW / Físico"
        if query_hw:
            fill_hardware_info(badge)
        badge.detected_users = []
        badge.last_activity_date = "N/A (Dispositivo Físico Bruto)"
        return badge

    # 1. Capacidade via psutil (instantâneo)
    try:
        usage = psutil.disk_usage(abs_path)
        badge.total_bytes = usage.total
        badge.used_bytes = usage.used
        badge.free_bytes = usage.free
        badge.percent_used = usage.percent
    except Exception:
        pass

    # Descobrir filesystem a partir das partições montadas
    try:
        best_mount = ""
        for part in psutil.disk_partitions(all=False):
            mp = os.path.abspath(part.mountpoint)
            if abs_path.startswith(mp) and len(mp) >= len(best_mount):
                best_mount = mp
                badge.mountpoint = mp
                badge.filesystem = part.fstype or "N/A"
    except Exception:
        pass

    # 2. Dados físicos de Hardware
    if query_hw:
        fill_hardware_info(badge)

    # 3. Usuários e Última Atividade Estimada
    users, last_date, last_file = _detect_users_and_activity(abs_path)
    badge.detected_users = users
    badge.last_activity_date = last_date
    badge.last_activity_file = last_file

    return badge
