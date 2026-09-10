import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import re
import shutil
import sys
import yt_dlp

__appname__ = "LDownlai"
__version__ = "1.1.0"
__author__ = "L'Abdouszlai"
__copyright__ = f"Copyright (c) 2026 {__author__}"

if getattr(sys, 'frozen', False):
    BASE = os.path.dirname(sys.executable)
    MEI = sys._MEIPASS
else:
    BASE = os.path.dirname(os.path.abspath(__file__))
    MEI = BASE

FFMPEG = os.path.join(BASE, "bin", "ffmpeg.exe")
if not os.path.exists(FFMPEG):
    FFMPEG = os.path.join(MEI, "bin", "ffmpeg.exe")
    if not os.path.exists(FFMPEG):
        FFMPEG = None

ICON = os.path.join(BASE, "app.ico")
if not os.path.exists(ICON):
    ICON = os.path.join(MEI, "app.ico")


def _find_js_runtime():
    for name in ("deno", "node"):
        exe = name + (".exe" if os.name == "nt" else "")
        for base in (BASE, MEI):
            p = os.path.join(base, "bin", exe)
            if os.path.isfile(p):
                return name, p
        w = shutil.which(name)
        if w:
            return name, w
    if os.name == "nt":
        candidates = (
            r"C:\Program Files\nodejs\node.exe",
            os.path.expandvars(r"%ProgramFiles%\nodejs\node.exe"),
            os.path.expandvars(r"%ProgramW6432%\nodejs\node.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\nodejs\node.exe"),
        )
        for p in candidates:
            if os.path.isfile(p):
                return "node", p
    return None, None


JS_RUNTIME_NAME, JS_RUNTIME_PATH = _find_js_runtime()

YT_CLIENTS = ["web_embedded", "mweb"]

YTDLP_JS_OPTS = {}
if JS_RUNTIME_NAME:
    cfg = {"path": JS_RUNTIME_PATH} if JS_RUNTIME_PATH else {}
    YTDLP_JS_OPTS["js_runtimes"] = {JS_RUNTIME_NAME: cfg}
    YTDLP_JS_OPTS["remote_components"] = ["ejs:github"]
YTDLP_JS_OPTS["extractor_args"] = {
    "youtube": {"player_client": YT_CLIENTS},
}

BG = "#0d1117"
BG2 = "#161b22"
BG3 = "#21262d"
FG = "#e6edf3"
FG2 = "#8b949e"
ACCENT = "#58a6ff"
ERR = "#f85149"
GREEN = "#3fb950"
BORDER = "#30363d"

QUALITY_VIDEO = {
    "Best (4K/1080p)": "bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
}

QUALITY_AUDIO = {
    "Best (320kbps)": "320",
    "256kbps": "256",
    "192kbps": "192",
    "128kbps": "128",
    "96kbps": "96",
}

PREVIEW_URL = None
preview_thread = None


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(__appname__)
        self.root.geometry("580x520+500+200")
        self.root.minsize(540, 480)
        self.root.configure(bg=BG)
        if os.path.exists(ICON):
            self.root.iconbitmap(default=ICON)

        self.busy = False
        self.cancel_flag = False

        self._setup_style()
        self._build()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_style(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure(".", background=BG, foreground=FG, fieldbackground=BG2,
                     troughcolor=BG2, selectbackground=ACCENT,
                     font=("Segoe UI", 10))
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=FG)
        s.configure("TEntry", fieldbackground=BG3, foreground=FG,
                     insertcolor=FG, bordercolor=BORDER)
        s.map("TEntry", bordercolor=[("focus", ACCENT)])
        s.configure("TCombobox", fieldbackground=BG3, foreground=FG,
                     arrowcolor=FG, selectbackground=BG3)
        s.map("TCombobox", fieldbackground=[("readonly", BG3)],
              foreground=[("readonly", FG)])
        s.configure("TButton", background=BG3, foreground=FG,
                     bordercolor=BORDER)
        s.map("TButton", background=[("active", BG2), ("pressed", ACCENT)])
        s.configure("Accent.TButton", background=ACCENT, foreground=BG)
        s.map("Accent.TButton",
              background=[("active", "#79c0ff"), ("pressed", "#1f6feb")])
        s.configure("Cancel.TButton", background=ERR, foreground=FG,
                     bordercolor=ERR)
        s.map("Cancel.TButton", background=[("active", "#da3633")])
        s.configure("Horizontal.TProgressbar", background=ACCENT,
                     troughcolor=BG3, bordercolor=BORDER)
        s.configure("Card.TFrame", background=BG2, bordercolor=BORDER,
                     borderwidth=1, relief="solid")
        s.configure("Header.TLabel", font=("Segoe UI", 18, "bold"),
                     foreground=FG)
        s.configure("Sub.TLabel", font=("Segoe UI", 8), foreground=FG2)
        s.configure("Small.TLabel", font=("Segoe UI", 9), foreground=FG2)

    def _build(self):
        m = ttk.Frame(self.root)
        m.pack(fill="both", expand=True, padx=16, pady=(12, 14))

        hdr = ttk.Frame(m)
        hdr.pack(fill="x", pady=(0, 12))
        ttk.Label(hdr, text=__appname__, style="Header.TLabel").pack(side="left")
        ttk.Label(hdr, text=f"v{__version__}  by {__author__}",
                  style="Sub.TLabel").pack(side="right")

        url_frame = ttk.Frame(m)
        url_frame.pack(fill="x", pady=(0, 10))
        self.url_var = tk.StringVar()
        self.url_var.trace_add("write", self._on_url_change)
        entry = ttk.Entry(url_frame, textvariable=self.url_var,
                          font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, ipady=5)
        entry.bind("<Return>", lambda _: self._start())
        paste_btn = ttk.Button(url_frame, text="Paste", command=self._do_paste,
                               width=6)
        paste_btn.pack(side="right", padx=(8, 0))

        opt_frame = ttk.Frame(m)
        opt_frame.pack(fill="x", pady=(0, 10))
        self.fmt_var = tk.StringVar(value="MP4")
        ttk.Radiobutton(opt_frame, text="MP4", variable=self.fmt_var,
                        value="MP4", command=self._swap).pack(side="left")
        ttk.Radiobutton(opt_frame, text="MP3", variable=self.fmt_var,
                        value="MP3", command=self._swap).pack(side="left",
                                                              padx=(16, 0))
        ttk.Label(opt_frame, text="Quality:", style="Small.TLabel").pack(
            side="left", padx=(24, 8))
        self.qvar = tk.StringVar()
        self.qcombo = ttk.Combobox(opt_frame, textvariable=self.qvar,
                                   state="readonly", width=20)
        self.qcombo.pack(side="left")
        self._swap()

        pv = ttk.Frame(m, style="Card.TFrame")
        pv.pack(fill="x", pady=(0, 10), ipadx=8, ipady=8)
        self.info_var = tk.StringVar(value="")
        self.info_label = ttk.Label(pv, textvariable=self.info_var,
                                    style="Small.TLabel", background=BG2,
                                    wraplength=500, justify="left")
        self.info_label.pack(anchor="w", padx=4, pady=4)

        btn_frame = ttk.Frame(m)
        btn_frame.pack(fill="x", pady=(0, 10))
        btn_inner = ttk.Frame(btn_frame)
        btn_inner.pack(anchor="center")
        self.dbtn = ttk.Button(btn_inner, text="Download",
                               style="Accent.TButton",
                               command=self._start, width=18)
        self.dbtn.pack(side="left", padx=(0, 8))
        self.pbtn = ttk.Button(btn_inner, text="Playlist as MP3",
                               command=self._plist, width=16)
        self.pbtn.pack(side="left", padx=(0, 8))
        self.cbtn = ttk.Button(btn_inner, text="Cancel",
                               style="Cancel.TButton",
                               command=self._cancel, width=8, state="disabled")
        self.cbtn.pack(side="left")

        self.out = os.path.join(os.path.expanduser("~"), "Downloads")
        self.out_btn = ttk.Button(
            m, text=f"Save to: ...\\{os.path.basename(self.out)}",
            command=self._pick)
        self.out_btn.pack(fill="x", pady=(0, 8))

        self.pbar = ttk.Progressbar(m, mode="determinate")
        self.pbar.pack(fill="x", pady=(0, 6))
        self.stat_var = tk.StringVar(value="Ready")
        ttk.Label(m, textvariable=self.stat_var, style="Small.TLabel").pack(
            anchor="w")
        ttk.Label(m, text="yt-dlp + ffmpeg",
                  foreground="#444", font=("Segoe UI", 7)).pack(
            side="bottom", anchor="e", pady=(4, 0))

    def _do_paste(self):
        try:
            self.url_var.set(self.root.clipboard_get())
        except tk.TclError:
            pass

    def _on_url_change(self, *_):
        global PREVIEW_URL, preview_thread
        url = self.url_var.get().strip()
        if url == PREVIEW_URL or not url:
            return
        PREVIEW_URL = url
        if preview_thread and preview_thread.is_alive():
            return
        preview_thread = threading.Thread(target=self._fetch_preview,
                                          args=(url,), daemon=True)
        preview_thread.start()

    def _fetch_preview(self, url):
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }
        opts.update(YTDLP_JS_OPTS)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if info.get("_type") == "playlist":
                entries = info.get("entries", [])
                if entries:
                    title = info.get("title", "Playlist")
                    count = info.get("playlist_count", len(entries))
                    text = f"Playlist: {title}\n{count} videos"
                else:
                    text = "Empty playlist"
            else:
                title = info.get("title", "")
                duration = info.get("duration", 0)
                minutes, seconds = divmod(duration, 60)
                dur_str = f"{minutes}:{seconds:02d}" if duration else ""
                channel = info.get("channel", info.get("uploader", ""))
                text = f"{title}\n{channel}"
                if dur_str:
                    text += f"  |  {dur_str}"
            self.root.after(0, lambda t=text: self._show_preview(t))
        except Exception:
            self.root.after(0, lambda: self._show_preview(""))

    def _show_preview(self, text):
        if text:
            self.info_var.set(text)
        else:
            self.info_var.set("")

    def _swap(self):
        if self.fmt_var.get() == "MP4":
            items = list(QUALITY_VIDEO.keys())
        else:
            items = list(QUALITY_AUDIO.keys())
        self.qcombo["values"] = items
        self.qvar.set(items[0])

    def _pick(self):
        d = filedialog.askdirectory(initialdir=self.out)
        if d:
            self.out = d
            self.out_btn.configure(
                text=f"Save to: ...\\{os.path.basename(d)}")

    def _validate_url(self):
        url = self.url_var.get().strip()
        if not url:
            raise ValueError("Please enter a URL")
        return url

    def _cancel(self):
        self.cancel_flag = True

    def _progress_hook(self, d):
        if self.cancel_flag:
            raise yt_dlp.utils.DownloadError("Cancelled")
        if d["status"] == "downloading":
            raw = d.get("_percent_str", "0%").strip()
            pct = re.sub(r"[^\d.]", "", raw)
            try:
                value = float(pct)
                self.root.after(0, lambda v=value:
                                self.pbar.configure(value=v))
            except ValueError:
                pass
            speed = d.get("_speed_str", "")
            eta = d.get("_eta_str", "")
            parts = [raw]
            if speed:
                parts.append(f"at {speed}")
            if eta:
                parts.append(f"ETA: {eta}")
            status = " ".join(parts)
            self.root.after(0, lambda s=status: self.stat_var.set(s))
        elif d["status"] == "finished":
            self.root.after(0, lambda: self.stat_var.set("Processing..."))
        elif d["status"] == "error":
            self.root.after(0,
                            lambda: self.stat_var.set("Error during download"))

    def _execute(self, opts, is_playlist=False):
        self.busy = True
        self.cancel_flag = False
        self.dbtn.configure(state="disabled")
        self.pbtn.configure(state="disabled")
        self.cbtn.configure(state="normal")
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url_var.get().strip()])
            if self.cancel_flag:
                self.root.after(0, lambda: self._done(False, "Cancelled"))
            else:
                msg = ("Playlist saved" if is_playlist
                       else "Download complete")
                self.root.after(0, lambda: self._done(True, msg))
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if "Cancelled" in msg:
                msg = "Cancelled"
            self.root.after(0, lambda m=msg: self._done(False, m))
        except Exception as e:
            self.root.after(0, lambda m=str(e): self._done(False, m))

    def _done(self, success, msg):
        self.busy = False
        self.pbar["value"] = 0
        self.dbtn.configure(state="normal")
        self.pbtn.configure(state="normal")
        self.cbtn.configure(state="disabled")
        self.stat_var.set(msg)

    def _build_opts(self, fmt, quality, template, is_playlist=False):
        opts = {
            "outtmpl": template,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": False,
            "ignoreerrors": is_playlist,
            "extract_flat": False,
            "windowsfilenames": True,
            "restrictfilenames": True,
            "updatetime": False,
        }
        opts.update(YTDLP_JS_OPTS)
        if FFMPEG and os.path.exists(FFMPEG):
            opts["ffmpeg_location"] = FFMPEG
        if is_playlist:
            opts["yes_playlist"] = True
        else:
            opts["noplaylist"] = True
        if fmt == "MP3":
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": QUALITY_AUDIO.get(quality, "320"),
            }]
        else:
            opts["format"] = QUALITY_VIDEO.get(quality,
                                               "bestvideo+bestaudio/best")
            opts["merge_output_format"] = "mp4"
        return opts

    def _start(self):
        if self.busy:
            return
        try:
            url = self._validate_url()
        except ValueError as e:
            self.stat_var.set(str(e))
            return
        self.url_var.set(url)
        template = os.path.join(self.out, "%(title)s.%(ext)s")
        opts = self._build_opts(self.fmt_var.get(), self.qvar.get(), template)
        self.pbar["value"] = 0
        self.stat_var.set("Starting...")
        threading.Thread(target=self._execute, args=(opts,), daemon=True).start()

    def _plist(self):
        if self.busy:
            return
        try:
            url = self._validate_url()
        except ValueError as e:
            self.stat_var.set(str(e))
            return
        self.url_var.set(url)
        template = os.path.join(
            self.out, "%(playlist_title)s",
            "%(playlist_index)02d - %(title)s.%(ext)s")
        opts = self._build_opts("MP3", "Best (320kbps)", template,
                                is_playlist=True)
        self.pbar["value"] = 0
        self.stat_var.set("Downloading playlist...")
        threading.Thread(target=self._execute, args=(opts, True),
                         daemon=True).start()

    def _on_close(self):
        if self.busy:
            if messagebox.askyesno("Quit?",
                                   "Download in progress. Cancel and quit?"):
                self.cancel_flag = True
                self.root.destroy()
            return
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
