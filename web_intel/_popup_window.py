"""
Popup window — singleton, listens on a local socket for JSON messages.
"""
import sys
import json
import socket
import threading
import tkinter as tk
from datetime import datetime

SOCKET_PORT = 47291

BG       = "#0d1117"
BG_HEAD  = "#161b22"
BG_ERR   = "#1a0a0a"
C_ACCENT = "#58a6ff"
C_WHITE  = "#e6edf3"
C_GREEN  = "#3fb950"
C_MUTED  = "#484f58"
C_RED    = "#f85149"
C_TIME   = "#30363d"

W, H_FULL, H_MINI = 260, 150, 28


class StatsPopup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.configure(bg=BG_HEAD)
        sw = self.root.winfo_screenwidth()
        self.root.geometry(f"{W}x{H_FULL}+{sw - W - 16}+16")

        self.total_tokens = self.total_cost = 0
        self.call_count = 0
        self.collapsed = False
        self.error_expanded = False

        self._build_ui()
        self._make_draggable()
        threading.Thread(target=self._listen, daemon=True).start()

    def _build_ui(self):
        # ── Header ──
        self.header = tk.Frame(self.root, bg=BG_HEAD, pady=0)
        self.header.pack(fill="x")

        tk.Label(self.header, text="⚡", bg=BG_HEAD, fg="#f0883e",
                 font=("Helvetica", 9)).pack(side="left", padx=(8, 2), pady=5)
        tk.Label(self.header, text="web_intel", bg=BG_HEAD, fg=C_WHITE,
                 font=("Helvetica", 9, "bold")).pack(side="left", pady=5)

        tk.Button(self.header, text="✕", bg=BG_HEAD, fg=C_MUTED, activebackground=BG_HEAD,
                  activeforeground=C_RED, font=("Helvetica", 9), bd=0,
                  cursor="hand2", command=self.root.destroy).pack(side="right", padx=6, pady=4)
        tk.Button(self.header, text="▾", bg=BG_HEAD, fg=C_MUTED, activebackground=BG_HEAD,
                  activeforeground=C_WHITE, font=("Helvetica", 9), bd=0,
                  cursor="hand2", command=self._toggle_collapse).pack(side="right", pady=4)

        # ── Divider ──
        tk.Frame(self.root, bg="#21262d", height=1).pack(fill="x")

        # ── Body ──
        self.body = tk.Frame(self.root, bg=BG, padx=10, pady=7)
        self.body.pack(fill="both", expand=True)

        self.url_var    = tk.StringVar(value="Ready")
        self.tokens_var = tk.StringVar(value="—")
        self.cost_var   = tk.StringVar(value="—")
        self.total_var  = tk.StringVar(value="0 calls · $0.0000")
        self.time_var   = tk.StringVar(value="")

        tk.Label(self.body, textvariable=self.url_var, bg=BG, fg=C_ACCENT,
                 font=("Helvetica", 8), anchor="w", wraplength=240).pack(fill="x")

        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(4, 0))
        tk.Label(row, textvariable=self.tokens_var, bg=BG, fg=C_WHITE,
                 font=("Helvetica", 9, "bold"), anchor="w").pack(side="left")
        tk.Label(row, textvariable=self.cost_var, bg=BG, fg=C_GREEN,
                 font=("Helvetica", 9, "bold"), anchor="e").pack(side="right")

        tk.Frame(self.body, bg="#21262d", height=1).pack(fill="x", pady=4)

        foot = tk.Frame(self.body, bg=BG)
        foot.pack(fill="x")
        tk.Label(foot, textvariable=self.total_var, bg=BG, fg=C_MUTED,
                 font=("Helvetica", 7), anchor="w").pack(side="left")
        tk.Label(foot, textvariable=self.time_var, bg=BG, fg=C_TIME,
                 font=("Helvetica", 7), anchor="e").pack(side="right")

        # ── Error row (hidden) ──
        self.err_frame = tk.Frame(self.root, bg=BG)
        self.err_btn_var = tk.StringVar()
        err_btn = tk.Label(self.err_frame, textvariable=self.err_btn_var,
                           bg=BG, fg=C_RED, font=("Helvetica", 7, "bold"),
                           cursor="hand2", anchor="w", padx=10, pady=3)
        err_btn.pack(fill="x")
        err_btn.bind("<Button-1>", self._toggle_error)
        self.err_detail_var = tk.StringVar()
        self.err_detail = tk.Label(self.err_frame, textvariable=self.err_detail_var,
                                   bg=BG_ERR, fg="#ff7b72", font=("Helvetica", 7),
                                   anchor="w", wraplength=250, justify="left", padx=10, pady=4)

    def _toggle_collapse(self):
        self.collapsed = not self.collapsed
        x, y = self.root.winfo_x(), self.root.winfo_y()
        if self.collapsed:
            self.body.pack_forget()
            self.err_frame.pack_forget()
            self.root.geometry(f"{W}x{H_MINI}+{x}+{y}")
        else:
            self.body.pack(fill="both", expand=True)
            self.root.geometry(f"{W}x{H_FULL}+{x}+{y}")

    def _toggle_error(self, _=None):
        self.error_expanded = not self.error_expanded
        x, y = self.root.winfo_x(), self.root.winfo_y()
        if self.error_expanded:
            self.err_detail.pack(fill="x")
            self.root.geometry(f"{W}x{H_FULL + 55}+{x}+{y}")
        else:
            self.err_detail.pack_forget()
            self.root.geometry(f"{W}x{H_FULL}+{x}+{y}")

    def _make_draggable(self):
        self._dx = self._dy = 0
        self.root.bind("<ButtonPress-1>", lambda e: setattr(self, '_dx', e.x) or setattr(self, '_dy', e.y))
        self.root.bind("<B1-Motion>", lambda e: self.root.geometry(
            f"+{self.root.winfo_x()+e.x-self._dx}+{self.root.winfo_y()+e.y-self._dy}"))

    def _listen(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", SOCKET_PORT))
        srv.listen(5)
        while True:
            try:
                conn, _ = srv.accept()
                data = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                conn.close()
                for line in data.decode().splitlines():
                    line = line.strip()
                    if line:
                        self.root.after(0, self._handle, json.loads(line))
            except Exception:
                pass

    def _handle(self, msg):
        t = msg.get("type")
        if t == "stats":
            p, c = msg.get("prompt_tokens", 0), msg.get("completion_tokens", 0)
            total = p + c
            cost = (p * 0.00000015) + (c * 0.0000006)
            self.total_tokens += total
            self.total_cost += cost
            self.call_count += 1
            url = msg.get("url", "")
            self.url_var.set(url[:38] + "..." if len(url) > 41 else url)
            self.tokens_var.set(f"{total:,} tokens  ({p:,}↑ {c:,}↓)")
            self.cost_var.set(f"${cost:.5f}")
            self.total_var.set(f"{self.call_count} calls · ${self.total_cost:.4f}")
            self.time_var.set(datetime.now().strftime("%H:%M:%S"))
            if self.collapsed:
                self._toggle_collapse()
        elif t == "error":
            m = msg.get("message", "error")
            self.err_btn_var.set(f"❌ {m[:40]}{'...' if len(m)>40 else ''}  ▾")
            self.err_detail_var.set(f"{msg.get('url','')}\n{msg.get('detail', m)}")
            self.err_frame.pack(fill="x")
            self.error_expanded = False
            self.err_detail.pack_forget()
            if self.collapsed:
                self._toggle_collapse()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    StatsPopup().run()
