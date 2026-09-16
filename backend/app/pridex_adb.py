"""ADB-канал панели Pridex: info, USB, screenshot, reboot. Без FastAPI."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

KNOWN_USB: dict[tuple[int, int], str] = {
    (0x10C4, 0xEA60): "LockerBox_USB (CP2102 / Wiegand-LB)",
    (0x0403, 0x6001): "GTUSB (FT232R / GT-7.5)",
    (0x2341, 0x0043): "Arduino Uno",
    (0x0BDA, 0x3460): "USB RGB Camera (Realtek)",
    (0x0BDA, 0x3461): "USB IR Camera (Realtek)",
    (0x27C6, 0x0816): "WingCool TouchScreen",
    (0x2207, 0x0006): "Rockchip ADB (эта панель → ПК)",
}

RFID_VID_PID: frozenset[tuple[int, int]] = frozenset(
    {(0x0403, 0x6001), (0x2341, 0x0043)}
)
LOCK_CONTROLLER_VID_PID = (0x10C4, 0xEA60)
CAMERA_VID_PID: frozenset[tuple[int, int]] = frozenset(
    {(0x0BDA, 0x3460), (0x0BDA, 0x3461)}
)
TOUCH_VID_PID = (0x27C6, 0x0816)

HEALTH_SH = (
    "echo +SOC; cat /sys/class/thermal/thermal_zone0/temp; "
    "echo +GPU; cat /sys/class/thermal/thermal_zone1/temp; "
    "echo +AC; cat /sys/class/power_supply/test_ac/online; "
    "echo +FREQ; cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq; "
    "echo +MAXFREQ; cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq; "
    "echo +LOAD; cat /proc/loadavg; "
    "echo +MEM; cat /proc/meminfo; "
    "echo +WAKE; dumpsys power | grep mWakefulness="
)

PREFS_PATH = (
    "/data/data/ru.inexdigital.panel/shared_prefs/"
    "ru.inexdigital.panel.global.xml"
)
KIOSK_PACKAGE = "ru.inexdigital.panel"


@dataclass
class UsbDevice:
    vid: int
    pid: int
    label: str
    manufacturer: str = ""
    product: str = ""
    path: str = ""

    @property
    def vid_pid(self) -> str:
        return f"{self.vid:04x}:{self.pid:04x}"


@dataclass
class PridexAdbInfo:
    ok: bool
    error: Optional[str] = None
    serial: str = ""
    model: str = ""
    android: str = ""
    build: str = ""
    eth0_ip: str = ""
    eth0_mac: str = ""
    focus: str = ""
    wakefulness: str = ""
    ac_online: bool = False
    thermal: list[dict[str, str]] = field(default_factory=list)
    usb: list[UsbDevice] = field(default_factory=list)
    panel_id: Optional[int] = None
    load: str = ""
    mem_avail: str = ""


class PridexAdbError(Exception):
    pass


def find_adb() -> Optional[Path]:
    root = Path(__file__).resolve().parents[2]
    if sys.platform == "win32":
        candidate = root / "tools" / "platform-tools" / "adb.exe"
        if candidate.exists():
            return candidate
        found = shutil.which("adb.exe") or shutil.which("adb")
        return Path(found) if found else None
    candidate = root / "tools" / "platform-tools" / "adb"
    if candidate.exists():
        return candidate
    found = shutil.which("adb")
    return Path(found) if found else None


def adb_available() -> bool:
    return find_adb() is not None


def _run(
    args: list[str], timeout: float = 25, binary: bool = False
) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        capture_output=True,
        timeout=timeout,
        text=not binary,
        encoding=None if binary else "utf-8",
        errors=None if binary else "replace",
        creationflags=CREATE_NO_WINDOW,
    )


def parse_getprop(text: str) -> dict[str, str]:
    props: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\[([^\]]+)\]: \[(.*)\]$", line)
        if match:
            props[match.group(1)] = match.group(2)
    return props


def parse_usb_host(text: str) -> list[UsbDevice]:
    devices: list[UsbDevice] = []
    block = re.compile(
        r"name=(?P<name>/dev/bus/usb/\S+)\s+"
        r"vendor_id=(?P<vid>\d+)\s+"
        r"product_id=(?P<pid>\d+)\s+"
        r"class=(?P<cls>\d+)\s+"
        r"subclass=(?P<sub>\d+)\s+"
        r"protocol=(?P<proto>\d+)\s+"
        r"manufacturer_name=(?P<mfr>[^\n]+)\s+"
        r"product_name=(?P<prod>[^\n]+)",
        re.S,
    )
    for match in block.finditer(text):
        vid = int(match.group("vid"))
        pid = int(match.group("pid"))
        label = KNOWN_USB.get((vid, pid))
        if not label:
            for (known_vid, _), name in KNOWN_USB.items():
                if known_vid == vid:
                    label = name
                    break
        mfr = match.group("mfr").strip()
        prod = match.group("prod").strip()
        if mfr == "null":
            mfr = ""
        if prod == "null":
            prod = ""
        devices.append(
            UsbDevice(
                vid=vid,
                pid=pid,
                label=label
                or " ".join(x for x in (mfr, prod) if x)
                or "USB device",
                manufacturer=mfr,
                product=prod,
                path=match.group("name"),
            )
        )
    return devices


def parse_focus(text: str) -> str:
    for key in ("mCurrentFocus=", "mFocusedApp=", "mResumedActivity:"):
        for line in text.splitlines():
            if key in line:
                return line.split(key, 1)[-1].strip()
    return ""


def parse_eth0(text: str) -> dict[str, str]:
    mac = ""
    ip = ""
    in_eth = False
    for line in text.splitlines():
        if re.match(r"^\d+:\s*eth0", line):
            in_eth = True
            continue
        if in_eth and re.match(r"^\d+:\s+", line):
            break
        if not in_eth:
            continue
        mm = re.search(r"link/ether\s+(\S+)", line)
        if mm:
            mac = mm.group(1)
        im = re.search(r"inet\s+(\S+)", line)
        if im:
            ip = im.group(1)
    return {"ip": ip, "mac": mac}


def parse_panel_id_from_prefs(xml_text: str) -> Optional[int]:
    match = re.search(
        r'<int name="panel_id" value="(\d+)"\s*/>',
        xml_text,
    )
    if not match:
        return None
    try:
        value = int(match.group(1))
    except ValueError:
        return None
    return value if value >= 1 else None


def _milli_c(raw: str) -> str:
    try:
        value = int(raw.strip())
    except ValueError:
        return ""
    return f"{value / 1000:.1f} °C"


def _tagged(text: str) -> dict[str, str]:
    tags: dict[str, str] = {}
    key = ""
    mem_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("+") and stripped[1:].isalpha():
            key = stripped[1:]
            if key == "MEM":
                mem_lines = []
            continue
        if not key:
            continue
        if key == "MEM":
            mem_lines.append(stripped)
            tags["MEM"] = "\n".join(mem_lines)
        elif key not in tags:
            tags[key] = stripped
    return tags


def parse_health(text: str) -> dict[str, Any]:
    tagged = _tagged(text)
    out: dict[str, Any] = {
        "thermal": [],
        "ac_online": tagged.get("AC", "") == "1",
        "load": " ".join((tagged.get("LOAD") or "").split()[:3]),
        "mem_avail": "",
        "wakefulness": "",
    }
    soc = _milli_c(tagged.get("SOC", ""))
    gpu = _milli_c(tagged.get("GPU", ""))
    if soc:
        out["thermal"].append({"name": "SoC", "temp": soc})
    if gpu:
        out["thermal"].append({"name": "GPU", "temp": gpu})
    for line in (tagged.get("MEM") or "").splitlines():
        if line.startswith("MemAvailable:"):
            kb = line.split()[1]
            try:
                out["mem_avail"] = f"{int(kb) / 1024:.0f} МБ свободно"
            except ValueError:
                out["mem_avail"] = kb
    wake = tagged.get("WAKE", "")
    if "mWakefulness=" in wake:
        out["wakefulness"] = wake.split("=", 1)[-1].strip()
    return out


class PridexAdb:
    def __init__(self, host: str, port: int = 5555) -> None:
        self.host = host.strip()
        self.port = port
        self.target = f"{self.host}:{self.port}"
        adb = find_adb()
        if adb is None:
            raise PridexAdbError("adb не найден")
        self.adb_path = adb

    def _adb(
        self, extra: list[str], timeout: float = 25, binary: bool = False
    ) -> subprocess.CompletedProcess:
        return _run(
            [str(self.adb_path), *extra], timeout=timeout, binary=binary
        )

    def connect(self) -> None:
        proc = self._adb(["connect", self.target], timeout=15)
        msg = ((proc.stdout or "") + (proc.stderr or "")).strip().lower()
        if "connected" not in msg and "already" not in msg:
            raise PridexAdbError(msg or "adb connect не удался")

    def shell(self, command: str, timeout: float = 20) -> str:
        try:
            proc = self._adb(
                ["-s", self.target, "shell", command], timeout=timeout
            )
        except subprocess.TimeoutExpired as exc:
            raise PridexAdbError(f"timeout: {command}") from exc
        out = (proc.stdout or "").strip()
        if proc.returncode != 0 and not out:
            err = (proc.stderr or "").strip()
            raise PridexAdbError(err or f"adb shell exit {proc.returncode}")
        return out

    def collect_info(self) -> PridexAdbInfo:
        self.connect()
        props = parse_getprop(self.shell("getprop", timeout=20))
        eth = parse_eth0(self.shell("ip addr", timeout=10))
        try:
            focus = parse_focus(self.shell("dumpsys window displays", timeout=20))
        except PridexAdbError:
            focus = ""
        try:
            health = parse_health(self.shell(HEALTH_SH, timeout=20))
        except PridexAdbError:
            health = {}
        try:
            usb = parse_usb_host(self.shell("dumpsys usb", timeout=25))
        except PridexAdbError:
            usb = []
        panel_id = None
        try:
            prefs = self.shell(f"cat {PREFS_PATH}", timeout=12)
            panel_id = parse_panel_id_from_prefs(prefs)
        except PridexAdbError:
            panel_id = None
        return PridexAdbInfo(
            ok=True,
            serial=props.get("ro.serialno", ""),
            model=props.get("ro.product.model")
            or props.get("ro.rk.socsub")
            or props.get("ro.hardware", ""),
            android=props.get("ro.build.version.release", ""),
            build=props.get("ro.build.display.id", ""),
            eth0_ip=eth.get("ip", ""),
            eth0_mac=eth.get("mac", ""),
            focus=focus,
            wakefulness=str(health.get("wakefulness") or ""),
            ac_online=bool(health.get("ac_online")),
            thermal=list(health.get("thermal") or []),
            usb=usb,
            panel_id=panel_id,
            load=str(health.get("load") or ""),
            mem_avail=str(health.get("mem_avail") or ""),
        )

    def screenshot_png(self) -> bytes:
        self.connect()
        try:
            proc = self._adb(
                ["-s", self.target, "exec-out", "screencap", "-p"],
                timeout=40,
                binary=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise PridexAdbError("timeout screencap") from exc
        data = proc.stdout or b""
        if not data.startswith(b"\x89PNG"):
            data = data.replace(b"\r\n", b"\n")
        if not data.startswith(b"\x89PNG"):
            err = (proc.stderr or b"").decode("utf-8", "replace")
            raise PridexAdbError(err or "screencap не PNG")
        return data

    def reboot(self) -> None:
        self.connect()
        try:
            self._adb(["-s", self.target, "reboot"], timeout=15)
        except subprocess.TimeoutExpired:
            return


def collect_pridex_info(host: str, port: int = 5555) -> PridexAdbInfo:
    try:
        return PridexAdb(host, port).collect_info()
    except FileNotFoundError:
        return PridexAdbInfo(ok=False, error="adb не найден")
    except subprocess.TimeoutExpired:
        return PridexAdbInfo(ok=False, error="таймаут ADB")
    except PridexAdbError as exc:
        return PridexAdbInfo(ok=False, error=str(exc))
    except OSError as exc:
        return PridexAdbInfo(ok=False, error=str(exc))
