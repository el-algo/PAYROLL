import queue
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageDraw
import customtkinter as ctk
from tkinter import filedialog
from payroll.services.generator import generate_payroll_receipts
from payroll.utils.dates import week_custom_format
# from payroll.utils.license_validator import check_license_on_startup

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
 
ACCENT      = "#2d7dd2"
DIVIDER     = "#2a2a2a"
HEADER_BG   = "#111111"
PANEL_BG    = "#1c1c1e"
LOG_BG      = "#141416"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PAYROLL - Generador de Recibos")
        self.geometry("1060x680")
        self.minsize(860, 580)
        self.configure(fg_color="#1a1a1c")
 
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.geometry(f"+{(w - 1060) // 2}+{(h - 680) // 2}")
 
        self.is_running = False
        self.msg_q = queue.Queue()
 
        self.control_path_var = ctk.StringVar(value="")
        self.emails_path_var  = ctk.StringVar(value="")
        self.week_var         = ctk.StringVar(value=week_custom_format())
 
        self._build_layout()
        self._trace_vars()
        self.update_generate_state()
 
    def _build_layout(self):
        # Row map:
        #  0 → header
        #  1 → two file-picker panels
        #  2 → Semana row
        #  3 → action buttons
        #  4 → "Actividad" label
        #  5 → log textbox  ← weight=1 so it expands
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)
 
        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=HEADER_BG, height=64, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.columnconfigure(0, weight=1)
        header.rowconfigure(0, weight=1)
 
        ctk.CTkLabel(
            header,
            text="PAYROLL  ·  Generador de Recibos",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#e0e0e0",
        ).grid(row=0, column=0)
 
        # ── Two file-picker panels (row 1) ────────────────────────────────────
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="ew", padx=32, pady=(24, 0))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.columnconfigure(2, weight=1)
 
        self._make_panel(
            content, "Archivo de control",
            self.control_path_var, self._pick_control
        ).grid(row=0, column=0, sticky="ew", padx=(0, 12))
 
        ctk.CTkFrame(content, fg_color=DIVIDER, width=2).grid(
            row=0, column=1, sticky="ns", pady=6
        )
 
        self._make_panel(
            content, "Archivo de correos",
            self.emails_path_var, self._pick_emails
        ).grid(row=0, column=2, sticky="ew", padx=(12, 0))
 
        # ── Semana (row 2) ────────────────────────────────────────────────────
        week_frame = ctk.CTkFrame(self, fg_color="transparent")
        week_frame.grid(row=2, column=0, sticky="ew", padx=32, pady=(16, 0))
        week_frame.columnconfigure(1, weight=1)
 
        ctk.CTkLabel(
            week_frame,
            text="Semana:",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#cccccc",
            width=90,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
 
        ctk.CTkEntry(
            week_frame,
            textvariable=self.week_var,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color=PANEL_BG,
            border_color=DIVIDER,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0))
 
        # ── Action buttons (row 3) ────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=32, pady=(20, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
 
        self.generate_btn = ctk.CTkButton(
            btn_frame,
            text="⚙  Generar recibos",
            width=220, height=42,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self.on_generate,
            fg_color=ACCENT,
            hover_color="#1a5fa8",
        )
        self.generate_btn.grid(row=0, column=0, padx=(0, 12), sticky="e")
 
        self.send_btn = ctk.CTkButton(
            btn_frame,
            text="✉  Enviar recibos",
            width=220, height=42,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self.on_send,
            fg_color=ACCENT,
            hover_color="#1a5fa8",
        )
        self.send_btn.grid(row=0, column=1, padx=(12, 0), sticky="w")
 
        # ── Log label (row 4) ─────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Actividad",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#888888",
            anchor="w",
        ).grid(row=4, column=0, sticky="w", padx=32, pady=(20, 4))
 
        # ── Log textbox (row 5) ───────────────────────────────────────────────
        self.log = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=LOG_BG,
            border_color=DIVIDER,
            border_width=1,
            corner_radius=8,
            text_color="#a0c8a0",
        )
        self.log.grid(row=5, column=0, sticky="nsew", padx=32, pady=(0, 24))
        self.log.insert("end", "Listo. Selecciona los archivos para comenzar.\n")
 
    def _make_panel(self, parent, label_text, path_var, pick_cmd):
        frame = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=10)
        frame.columnconfigure(0, weight=1)
 
        ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#dddddd",
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(14, 6), sticky="w")
 
        ctk.CTkEntry(
            frame,
            textvariable=path_var,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            placeholder_text="Ningún archivo seleccionado",
            fg_color="#111113",
            border_color=DIVIDER,
        ).grid(row=1, column=0, padx=(16, 8), pady=(0, 14), sticky="ew")
 
        ctk.CTkButton(
            frame,
            text="Buscar",
            width=90, height=34,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=pick_cmd,
            fg_color=ACCENT,
            hover_color="#1a5fa8",
        ).grid(row=1, column=1, padx=(0, 16), pady=(0, 14))
 
        return frame
 
    def _pick_control(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if path:
            self.control_path_var.set(path)
 
    def _pick_emails(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if path:
            self.emails_path_var.set(path)
 
    def _trace_vars(self):
        self.control_path_var.trace_add("write", lambda *_: self.update_generate_state())
        self.emails_path_var.trace_add("write",  lambda *_: self.update_generate_state())
 
    def update_generate_state(self):
        has_control = bool(self.control_path_var.get())
        has_emails  = bool(self.emails_path_var.get())
        self.generate_btn.configure(state="normal" if has_control else "disabled")
        self.send_btn.configure(state="normal" if (has_control and has_emails) else "disabled")
 
    def on_generate(self):
        self.log.insert("end", f"[{_now()}] Generando recibos...\n")
        self.log.see("end")
 
    def on_send(self):
        self.log.insert("end", f"[{_now()}] Enviando recibos...\n")
        self.log.see("end")
 
def _now():
    return datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    # check_license_on_startup()
    App().mainloop()
