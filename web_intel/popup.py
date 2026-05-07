"""
popup.py — sends JSON to the singleton popup via socket.
If popup isn't running, spawns it first.
"""
import sys
import json
import socket
import subprocess
import os

SOCKET_PORT = 47291
_script = os.path.join(os.path.dirname(__file__), "_popup_window.py")


def _send(msg: dict):
    try:
        # Try sending to existing popup
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(("127.0.0.1", SOCKET_PORT))
        s.sendall((json.dumps(msg) + "\n").encode())
        s.close()
    except ConnectionRefusedError:
        # Popup not running — spawn it, wait a moment, retry
        subprocess.Popen(
            [sys.executable, _script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        import time
        time.sleep(0.8)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect(("127.0.0.1", SOCKET_PORT))
            s.sendall((json.dumps(msg) + "\n").encode())
            s.close()
        except Exception:
            pass
    except Exception:
        pass


def log_usage(url: str, prompt_tokens: int, completion_tokens: int):
    _send({"type": "stats", "url": url,
           "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens})


def log_error(url: str, message: str, detail: str = ""):
    _send({"type": "error", "url": url,
           "message": message, "detail": detail or message})


if __name__ == "__main__":
    # python -m web_intel.popup
    from web_intel._popup_window import StatsPopup
    StatsPopup().run()
