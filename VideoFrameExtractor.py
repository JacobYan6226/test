import os
import sys
import cv2
import threading
import subprocess
import numpy as np
import tkinter as tk
import pytesseract
from tkinter import filedialog, messagebox, ttk

# ──────────────────────────────────────────────
#  跨平台 tesseract 路径（macOS / Windows / Linux）
# ──────────────────────────────────────────────
def _get_tesseract_path():
    """返回 tesseract 二进制路径"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
        if sys.platform == "win32":
            return os.path.join(base, 'tesseract_bin', 'tesseract.exe')
        return os.path.join(base, 'tesseract_bin', 'tesseract')
    # 开发模式
    if sys.platform == "win32":
        return r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    return '/opt/homebrew/bin/tesseract'

def _get_tessdata_path():
    """返回 tessdata 目录"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'tessdata')
    if sys.platform == "win32":
        return r"C:\Program Files\Tesseract-OCR\tessdata"
    return '/opt/homebrew/share/tessdata'

def _open_folder(path: str):
    """跨平台打开文件夹"""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=True)
        else:
            subprocess.run(["xdg-open", path], check=True)
    except Exception:
        pass

pytesseract.pytesseract.tesseract_cmd = _get_tesseract_path()

# ──────────────────────────────────────────────
#  macOS 拖拽支持
# ──────────────────────────────────────────────
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False

# ──────────────────────────────────────────────
#  自定义 Canvas 按钮（解决 macOS tkinter 按钮点击不灵的问题）
# ──────────────────────────────────────────────

class CanvasButton(tk.Canvas):
    """基于 Canvas 的自定义按钮，保证全区域可点击，带 hover/active 效果"""

    def __init__(self, parent, text, command, width=320, height=60,
                 bg="#2E8B57", fg="white", hover="#27AE60",
                 active="#1E6B42", font=None, **kwargs):
        self._command = command
        self._bg     = bg
        self._fg     = fg
        self._hover  = hover
        self._active = active
        self._state  = "normal"   # normal | active | disabled

        font = font or ("Arial", 15, "bold")
        super().__init__(
            parent, width=width, height=height,
            bg=parent.cget("bg"), highlightthickness=0, **kwargs
        )
        self._rounded_rect(0, 0, width, height, radius=10, fill=bg, outline=bg)
        self._text_id = self.create_text(
            width / 2, height / 2, text=text,
            fill=fg, font=font, anchor="center"
        )
        self._draw()

        self.bind("<Enter>",         self._on_enter)
        self.bind("<Leave>",         self._on_leave)
        self.bind("<Button-1>",      self._on_click)
        self.bind("<ButtonRelease>", self._on_release)
        self.config(cursor="hand2")

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """画圆角矩形"""
        r = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2,     y1,
            x2,     y2,
            x1,     y2,
            x1,     y1,
        ]
        for i in range(0, 12, 2):
            cx, cy = (x2 + x1) / 2, (y2 + y1) / 2
            if i == 0:
                points[i : i + 2] = [x1 + r, y1]
            elif i == 2:
                points[i : i + 2] = [x2 - r, y1]
            elif i == 4:
                points[i : i + 2] = [x2, y1 + r]
            elif i == 6:
                points[i : i + 2] = [x2, y2 - r]
            elif i == 8:
                points[i : i + 2] = [x2 - r, y2]
            elif i == 10:
                points[i : i + 2] = [x1 + r, y2]
        # 用两个圆角矩形 + 矩形简化
        self.create_arc(x1,      y1,      x1 + 2*r, y1 + 2*r, start=180, extent=90, fill=kwargs.get("fill"), outline="")
        self.create_arc(x2-2*r, y1,      x2,        y1 + 2*r, start=270, extent=90, fill=kwargs.get("fill"), outline="")
        self.create_arc(x1,      y2-2*r,  x1 + 2*r, y2,       start= 90, extent=90, fill=kwargs.get("fill"), outline="")
        self.create_arc(x2-2*r, y2-2*r,  x2,        y2,       start=  0, extent=90, fill=kwargs.get("fill"), outline="")
        self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=kwargs.get("fill"), outline="")
        self.create_rectangle(x1, y1 + r, x2, y2 - r, fill=kwargs.get("fill"), outline="")

    def _draw(self):
        self.delete("all")
        w, h = int(self.cget("width")), int(self.cget("height"))
        if self._state == "disabled":
            fill = "#BBBBBB"
        elif self._state == "active":
            fill = self._active
        elif self._state == "hover":
            fill = self._hover
        else:
            fill = self._bg
        self._rounded_rect(0, 0, w, h, radius=10, fill=fill, outline=fill)
        self.create_text(w / 2, h / 2, text=self.get("text", ""),
                         fill=self._fg, font=self._font(), anchor="center")

    def _font(self):
        return ("Arial", 15, "bold")

    def get(self, key, default=""):
        # 简单存储，用实例变量
        return getattr(self, f"_{key}", default)

    def config_state(self, state: str):
        self._state = state
        self._draw()

    def _on_enter(self, _):
        if self._state != "disabled":
            self._state = "hover"
            self._draw()

    def _on_leave(self, _):
        self._state = "normal"
        self._draw()

    def _on_click(self, _):
        if self._state != "disabled":
            self._state = "active"
            self._draw()

    def _on_release(self, _):
        if self._state != "disabled":
            self._state = "hover"
            self._draw()
            self._command()

    def configure(self, **kwargs):
        for key, val in kwargs.items():
            if key == "state":
                self.config_state("disabled" if val == "disabled" else "normal")
            elif key == "text":
                self._text = val
                self._draw()


# ──────────────────────────────────────────────
#  主应用
# ──────────────────────────────────────────────

class VideoFrameExtractor:
    _VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".flv", ".m4v"}

    def __init__(self, root):
        self.root = root
        self.root.title("视频截图工具 - 字幕智能识别")
        self.root.geometry("720x600")
        self.root.resizable(False, False)

        self.video_path  = ""
        self.save_path   = ""
        self.running     = False
        self.capture_mode = tk.StringVar(value="subtitle")
        self.capture_mode.trace_add("write", self._on_mode_change)

        self._build_ui()
        self._on_mode_change()

    # ─────────────────────────── UI 构建 ───────────────────────────

    def _build_ui(self):
        tk.Label(
            self.root, text="🎬 字幕截图工具",
            font=("Arial", 20, "bold"), fg="#333333"
        ).pack(pady=(14, 6))

        # ── 视频拖拽区 ──
        frame_dnd = tk.Frame(self.root, bg="#ECEFF1", bd=2, relief="groove")
        frame_dnd.pack(pady=(0, 4), padx=24)
        self.video_label = tk.Label(
            frame_dnd,
            text="📂  将视频拖到此处，或直接点击此处选择",
            width=76, height=4,
            bg="#F8F9FA", fg="#888888",
            font=("Arial", 12),
            wraplength=660, anchor="center", justify="center",
            cursor="hand2",
        )
        self.video_label.pack(padx=4, pady=4)
        self.video_label.bind("<Button-1>", lambda _: self._select_video())

        if _DND_AVAILABLE:
            self.video_label.drop_target_register(DND_FILES)
            self.video_label.dnd_bind("<<Drop>>", self._on_drop)

        # ── 按钮行 ──
        btn_row = tk.Frame(self.root)
        btn_row.pack(pady=4)
        ttk.Button(btn_row, text="选择视频", command=self._select_video, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_row, text="选择保存位置", command=self._select_save_folder, width=18).pack(side=tk.LEFT, padx=8)

        # ── 保存路径 ──
        self.save_label = tk.Label(
            self.root, text="📁 保存位置：默认保存到视频文件旁",
            width=76, height=1, relief="groove",
            font=("Arial", 10), fg="#555555", bg="#FAFAFA"
        )
        self.save_label.pack(pady=(2, 8), padx=24)

        # ── 截图模式 ──
        tk.Label(self.root, text="截图模式", font=("Arial", 12, "bold")).pack(pady=(4, 2))
        mode_frame = tk.Frame(self.root)
        mode_frame.pack()
        ttk.Radiobutton(
            mode_frame, text="字幕出现时截图（OCR 智能识别）",
            variable=self.capture_mode, value="subtitle",
        ).pack(side=tk.LEFT, padx=16)
        ttk.Radiobutton(
            mode_frame, text="固定时间间隔截图",
            variable=self.capture_mode, value="time",
        ).pack(side=tk.LEFT, padx=16)

        # ── 间隔输入（仅固定模式） ──
        self.interval_frame = tk.Frame(self.root)
        tk.Label(self.interval_frame, text="间隔时间（秒）：", font=("Arial", 11)).pack(side=tk.LEFT)
        self.interval_entry = ttk.Entry(self.interval_frame, font=("Arial", 11), width=8)
        self.interval_entry.insert(0, "5")
        self.interval_entry.pack(side=tk.LEFT, padx=4)

        # ── 进度条 ──
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.root, variable=self.progress_var, maximum=100, length=660
        )
        self.progress_bar.pack(pady=(16, 2), padx=24)

        # ── 状态 ──
        self.status_label = tk.Label(
            self.root, text="准备就绪，请先选择视频文件",
            fg="#888888", font=("Arial", 11)
        )
        self.status_label.pack(pady=4)

        # ── Canvas 自定义按钮（解决 macOS 点击问题） ──
        self.start_btn = CanvasButton(
            self.root, text="▶  开 始",
            command=self._toggle_start,
            width=340, height=64,
            bg="#2E8B57", fg="white",
            hover="#27AE60", active="#1E6B42",
            font=("Arial", 16, "bold"),
        )
        self.start_btn.pack(pady=14)

    # ─────────────────────────── 模式切换 ───────────────────────────

    def _on_mode_change(self, *_):
        if self.capture_mode.get() == "time":
            self.interval_frame.pack(pady=6)
        else:
            self.interval_frame.pack_forget()

    # ─────────────────────────── 文件操作 ───────────────────────────

    def _set_video(self, path: str):
        path = path.strip().strip("{}")
        if not os.path.isfile(path):
            return
        ext = os.path.splitext(path)[1].lower()
        if ext not in self._VIDEO_EXTS:
            messagebox.showwarning("格式不支持",
                f"不支持：{ext}\n支持：{', '.join(sorted(self._VIDEO_EXTS))}")
            return
        self.video_path = path
        name = os.path.basename(path)
        self.video_label.config(
            text=f"✅ {name}\n{path}",
            fg="#1A7A37", bg="#EAF7EE"
        )
        self.start_btn.configure(text="▶  开 始")
        self.start_btn.config_state("normal")

    def _select_video(self):
        path = filedialog.askopenfilename(
            filetypes=[("视频文件", "*.mp4 *.mov *.mkv *.avi *.flv *.m4v")]
        )
        if path:
            self._set_video(path)

    def _on_drop(self, event):
        raw = event.data.strip()
        path = raw[1:raw.index("}")] if raw.startswith("{") else raw.split()[0]
        self._set_video(path)

    def _select_save_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.save_label.config(text=f"📁 保存位置：{path}", fg="#333333")

    # ─────────────────────────── OCR 字幕检测 ───────────────────────────

    def _ocr_subtitle(self, frame) -> bool:
        """
        基于 pytesseract 的字幕识别，大幅提升准确率。

        策略：
        - 只截取视频底部 22% 区域（字幕标准位置）
        - 每 6 帧运行一次 OCR，平衡速度与准确率
        - 同时使用中文 + 英文语言包
        - 字符置信度 > 50 才认为是有效文字
        - 至少 3 个有效字符才算有字幕
        - 排除纯数字/纯符号结果（如时间码）
        """
        h, w = frame.shape[:2]
        y0 = int(h * 0.78)
        sub = frame[y0:h, :]

        # 转灰度 + 直方图均衡化（增强文字对比度）
        gray = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
        eq   = cv2.equalizeHist(gray)

        # 放大 2x 再二值化，文字更清晰
        big = cv2.resize(eq, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, binary = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 反转（文字变白，背景变黑）→ OCR 效果更好
        binary = cv2.bitwise_not(binary)

        # OCR：中文优先，备选英文；指定 tessdata 路径
        for lang in ("chi_sim+eng", "eng"):
            try:
                cfg = f"--oem 3 --psm 6 -l {lang} --tessdata-dir {_get_tessdata_path()}"
                data = pytesseract.image_to_data(binary, config=cfg, output_type=pytesseract.Output.DICT)
                break
            except Exception:
                continue
        else:
            return False

        # 统计有效文字块（置信度 > 50）
        confidences = [int(c) for c in data["conf"] if int(c) > 50]
        if len(confidences) < 3:
            return False

        # 过滤：去掉纯数字或纯符号（如 "00:12"）
        texts = [t.strip() for t in data["text"] if t.strip()]
        meaningful = [
            t for t in texts
            if len(t) >= 2 and not t.replace(":", "").replace(".", "").isdigit()
        ]
        if len(meaningful) < 1:
            # 有文字但都是数字，也放过（可能是字幕附带时间码）
            return len(confidences) >= 5

        return True

    # ─────────────────────────── 核心截图逻辑 ───────────────────────────

    def _start_capture(self):
        final_save = self.save_path or os.path.join(
            os.path.dirname(self.video_path), "视频截图"
        )
        os.makedirs(final_save, exist_ok=True)

        cap = cv2.VideoCapture(self.video_path)
        fps          = cap.get(cv2.CAP_PROP_FPS) or 25
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 固定间隔步长
        try:
            interval_sec = float(self.interval_entry.get())
        except ValueError:
            interval_sec = 5.0
        time_step = max(1, int(fps * interval_sec))

        count        = 0
        frame_cnt    = 0
        last_cap_sec = -999.0

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            now_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            if self.capture_mode.get() == "subtitle":
                # 每 6 帧运行一次 OCR，节省 CPU
                if frame_cnt % 6 == 0:
                    if self._ocr_subtitle(frame) and now_sec - last_cap_sec > 1.5:
                        filename = os.path.join(final_save, f"sub_{int(now_sec):05d}s.jpg")
                        cv2.imwrite(filename, frame)
                        count += 1
                        last_cap_sec = now_sec
            else:
                if frame_cnt % time_step == 0:
                    filename = os.path.join(final_save, f"time_{frame_cnt:07d}.jpg")
                    cv2.imwrite(filename, frame)
                    count += 1

            frame_cnt += 1

            # 每 30 帧更新进度
            if frame_cnt % 30 == 0:
                pct = (frame_cnt / total_frames * 100) if total_frames > 0 else 0
                self.root.after(0, self._update_status, count, pct)

        cap.release()
        self.running = False
        self.root.after(0, self._on_finish, count, final_save)

    # ─────────────────────────── UI 回调 ───────────────────────────

    def _update_status(self, count: int, pct: float):
        self.status_label.config(text=f"已保存：{count} 张　进度：{pct:.1f}%", fg="#2E8B57")
        self.progress_var.set(min(pct, 100))

    def _on_finish(self, count: int, save_dir: str):
        self.start_btn.configure(text="▶  开 始")
        self.start_btn.config_state("normal")
        self.status_label.config(text=f"✅ 完成！共 {count} 张", fg="#555555")
        self.progress_var.set(100)
        messagebox.showinfo("完成", f"截图完成！\n共 {count} 张\n保存位置：{save_dir}")
        # 自动打开保存文件夹（跨平台）
        _open_folder(save_dir)

    def _toggle_start(self):
        if not self.running:
            self.running = True
            self.start_btn.configure(text="⏹  停 止")
            self.start_btn.config_state("active")
            self.progress_var.set(0)
            self.status_label.config(text="处理中，请稍候…", fg="#E67E22")
            threading.Thread(target=self._start_capture, daemon=True).start()
        else:
            self.running = False
            self.start_btn.configure(text="▶  开 始")
            self.start_btn.config_state("normal")
            self.status_label.config(text="已停止", fg="#888888")


# ─────────────────────────── 入口 ───────────────────────────

if __name__ == "__main__":
    root = TkinterDnD.Tk() if _DND_AVAILABLE else tk.Tk()
    app = VideoFrameExtractor(root)
    root.mainloop()
