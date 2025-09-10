# backend/app/features/sys_exec/service.py
from __future__ import annotations
import asyncio, os, platform, time, shlex, sys
from pathlib import Path
from typing import List, Optional, Tuple

# 可自訂：允許的根目錄與副檔名白名單
ALLOWED_ROOTS = [
    Path(r"C:\Users\CHENG\Desktop\Jessie").resolve(),   # Windows 範例
    Path("/opt/power-system-hmi").resolve(),            # Linux 範例
]
ALLOWED_EXTS = {".bat", ".cmd", ".ps1", ".exe", ".py", ".sh"}

def _is_under_allowed_roots(path: Path) -> bool:
    try:
        rp = path.resolve(strict=False)
    except Exception:
        return False
    for root in ALLOWED_ROOTS:
        try:
            rp.relative_to(root)
            return True
        except Exception:
            continue
    return False

def _build_cmd(exe_path: Path, args: List[str]) -> Tuple[List[str], dict]:
    """
    根據 OS 建立正確的呼叫方式（不透過 shell，避免注入）
    """
    sys_platform = platform.system().lower()
    creationflags = 0
    startupinfo = None

    if sys_platform == "windows":
        # .ps1 用 PowerShell 執行；.bat/.cmd 用 cmd；.exe 直接；.py 用 python
        ext = exe_path.suffix.lower()
        if ext == ".ps1":
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(exe_path), *args]
        elif ext in (".bat", ".cmd"):
            cmd = ["cmd", "/c", str(exe_path), *args]
        elif ext == ".py":
            cmd = [sys.executable, str(exe_path), *args]
        else:
            cmd = [str(exe_path), *args]

        # 隱藏視窗（可由呼叫端選擇）
        creationflags = 0x08000000  # CREATE_NO_WINDOW
        startupinfo = None
        return cmd, {"creationflags": creationflags, "startupinfo": startupinfo}
    else:
        # Linux/macOS
        ext = exe_path.suffix.lower()
        if ext == ".sh":
            cmd = ["/bin/bash", str(exe_path), *args]
        elif ext == ".py":
            cmd = [sys.executable, str(exe_path), *args]
        else:
            cmd = [str(exe_path), *args]
        return cmd, {}


async def run_external(file_path: str) -> int:
    import subprocess
    exe = Path(file_path).expanduser().resolve()

    if not exe.exists():
        raise FileNotFoundError(f"檔案不存在: {file_path}")

    # 決定可執行命令
    if platform.system().lower() == "windows":
        cmd = [sys.executable, str(exe)] if exe.suffix.lower() == ".py" else [str(exe)]
        # 在 thread 裡用同步 Popen，避免 Selector loop 的限制
        proc = await asyncio.to_thread(
            subprocess.Popen,
            cmd,
            cwd=str(exe.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=0x08000000  # 隱藏視窗
        )

        # 非阻塞地讀取輸出：把 blocking 的 read 放到 thread
        async def read_stream(stream):
            while True:
                chunk = await asyncio.to_thread(stream.readline)
                if not chunk:
                    break
                yield chunk

        async for line in read_stream(proc.stdout):
            print(line.decode().rstrip())

        rc = await asyncio.to_thread(proc.wait)
    return rc

