"""Start or stop the Windows Streamlit server from the batch launchers."""
import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
PID_FILE = RUNTIME / "streamlit.pid"
APP = ROOT / "app.py"
URL = "http://127.0.0.1:8000"


def existing_pid():
    if not PID_FILE.is_file():
        return None
    pid = PID_FILE.read_text().strip()
    if not pid.isascii() or not pid.isdigit():
        return None
    cmd = (f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine")
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd],
                            capture_output=True, text=True, check=True)
    if str(APP).lower() in result.stdout.lower() and "-m streamlit run" in result.stdout:
        return pid
    return None


def start():
    if not (ROOT / "data/local/interactions.npz").is_file():
        raise RuntimeError("Run setup.bat to prepare the data first.")
    if existing_pid() is None:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 8000))
        RUNTIME.mkdir(exist_ok=True)
        with (RUNTIME / "streamlit.log").open("w") as stdout, (RUNTIME / "streamlit-error.log").open("w") as stderr:
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", str(APP),
                 "--server.address=127.0.0.1", "--server.port=8000", "--server.headless=true"],
                cwd=ROOT, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        PID_FILE.write_text(str(process.pid))
    for _ in range(30):
        try:
            with urllib.request.urlopen(URL + "/_stcore/health", timeout=1) as response:
                if response.read().strip() != b"ok":
                    continue
        except (urllib.error.URLError, TimeoutError):
            time.sleep(1)
            continue
        if not os.getenv("SPOTIFY_NO_BROWSER"):
            webbrowser.open(URL)
        print(URL)
        return
    raise RuntimeError("Streamlit failed to start. Check .runtime/streamlit-error.log.")


def stop():
    pid = existing_pid()
    if pid:
        subprocess.run(["taskkill.exe", "/PID", pid, "/T", "/F"], check=True)
    PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop"])
    try:
        {"start": start, "stop": stop}[parser.parse_args().action]()
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
