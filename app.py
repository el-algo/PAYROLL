import threading
import queue
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw
import customtkinter as ctk
from tkinter import filedialog
from payroll.services.generator import generate_payroll_receipts
from payroll.services.sender import send_payroll_emails
from payroll.utils.dates import week_custom_format, get_paydate
# from payroll.utils.license_validator import check_license_on_startup

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT    = "#2d7dd2"
DIVIDER   = "#2a2a2a"
HEADER_BG = "#111111"
PANEL_BG  = "#2e2e31"
LOG_BG    = "#141416"


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
        self.payroll_path_var  = ctk.StringVar(value="")
        self.week_var         = ctk.StringVar(value=week_custom_format())
        self.pay_date_var     = ctk.StringVar(value=get_paydate())

        self._build_layout()
        self._trace_vars()
        self.update_generate_state()

    def _build_layout(self):
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=1)
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

        # ── Two-column content area (row 1) ───────────────────────────────────
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="ew", padx=32, pady=(24, 0))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.columnconfigure(2, weight=1)

        # Section labels (same style as "Actividad")
        ctk.CTkLabel(
            content, text="Generar recibos",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#888888", anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        ctk.CTkLabel(
            content, text="Enviar recibos",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#888888", anchor="w",
        ).grid(row=0, column=2, sticky="w", pady=(0, 4))

        # File panels
        self._make_panel(
            content, "Archivo de control",
            self.control_path_var, self._pick_control,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkFrame(content, fg_color=DIVIDER, width=2).grid(
            row=1, column=1, rowspan=3, sticky="ns", pady=6
        )

        self._make_panel(
            content, "Archivo generado de recibos de nómina",
            self.payroll_path_var, self._pick_payroll,
        ).grid(row=1, column=2, sticky="ew", padx=(12, 0))

        # Week entry inside left column (row 2)
        week_panel = ctk.CTkFrame(content, fg_color=PANEL_BG, corner_radius=10)
        week_panel.grid(row=2, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))
        week_panel.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            week_panel, text="Semana:",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#dddddd", width=90, anchor="w",
        ).grid(row=0, column=0, padx=(16, 8), pady=14, sticky="w")

        ctk.CTkEntry(
            week_panel,
            textvariable=self.week_var,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="#111113",
            border_color=DIVIDER,
        ).grid(row=0, column=1, padx=(0, 16), pady=14, sticky="ew")

        # Pay date entry inside left column (row 3)
        pay_date_panel = ctk.CTkFrame(content, fg_color=PANEL_BG, corner_radius=10)
        pay_date_panel.grid(row=3, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))
        pay_date_panel.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            pay_date_panel, text="Fecha de pago:",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#dddddd", width=90, anchor="w",
        ).grid(row=0, column=0, padx=(16, 8), pady=14, sticky="w")

        ctk.CTkEntry(
            pay_date_panel,
            textvariable=self.pay_date_var,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="#111113",
            border_color=DIVIDER,
        ).grid(row=0, column=1, padx=(0, 16), pady=14, sticky="ew")

        # ── Action buttons (row 2) ────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=32, pady=(20, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        self.generate_btn = ctk.CTkButton(
            btn_frame,
            text="Generar recibos",
            width=220, height=42,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self.on_generate,
            fg_color=ACCENT,
            hover_color="#1a5fa8",
        )
        self.generate_btn.grid(row=0, column=0, padx=(0, 12), sticky="")

        self.send_btn = ctk.CTkButton(
            btn_frame,
            text="Enviar recibos",
            width=220, height=42,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self.on_send,
            fg_color=ACCENT,
            hover_color="#1a5fa8",
        )
        self.send_btn.grid(row=0, column=1, padx=(12, 0), sticky="")

        # ── Log label (row 3) ─────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Actividad",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#888888",
            anchor="w",
        ).grid(row=3, column=0, sticky="w", padx=32, pady=(20, 4))

        # ── Log textbox (row 4) ───────────────────────────────────────────────
        self.log = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=LOG_BG,
            border_color=DIVIDER,
            border_width=1,
            corner_radius=8,
            text_color="#a0c8a0",
        )
        self.log.grid(row=4, column=0, sticky="nsew", padx=32, pady=(0, 24))
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
        path = filedialog.askopenfilename(
            title="Selecciona el archivo de control",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )
        if path:
            self.control_path_var.set(path)

    def _pick_payroll(self):
        path = filedialog.askopenfilename(
            title="Selecciona el archivo generado de recibos de nómina",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )
        if path:
            self.payroll_path_var.set(path)

    def _trace_vars(self):
        for var in (self.control_path_var, self.payroll_path_var):
            var.trace_add("write", lambda *_: self.update_generate_state())

    def update_generate_state(self):
        has_control = bool(self.control_path_var.get()) and Path(self.control_path_var.get()).is_file()
        has_payroll = bool(self.payroll_path_var.get()) and Path(self.payroll_path_var.get()).is_file()
        self.generate_btn.configure(state="disabled" if (self.is_running or not has_control) else "normal")
        self.send_btn.configure(state="disabled" if (self.is_running or not (has_control and has_payroll)) else "normal")

    def append_log(self, text: str):
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.update_idletasks()

    def on_generate(self):
        control_path = self.control_path_var.get().strip()
        if not control_path or not Path(control_path).is_file():
            self.append_log("Selecciona el archivo de control primero.")
            return

        week     = self.week_var.get().strip()
        pay_date = self.pay_date_var.get().strip()
        out_filename = f"{week.replace('/', '-')}.xlsx"

        self.append_log(f"[{_now()}] Generando recibos para la semana {week}…")
        self.is_running = True
        self.update_generate_state()

        t = threading.Thread(
            target=self._worker_generate,
            args=(control_path, out_filename, week, pay_date),
            daemon=True,
        )
        t.start()
        self.after(100, self._drain_queue)

    def _worker_generate(self, path: str, out_filename: str, week: str, pay_date: str):
        try:
            generate_payroll_receipts(
                path,
                progress_cb=lambda msg: self.msg_q.put(("log", msg)),
                out_filename=out_filename,
                week=week,
                pay_date=pay_date,
            )
            self.msg_q.put(("log", "Proceso finalizado."))
            self.msg_q.put(("done", True))
        except Exception as e:
            self.msg_q.put(("log", f"✗ Error: {e}"))
            self.msg_q.put(("done", False))

    def on_send(self):
        payroll_path = self.payroll_path_var.get().strip()
        control_path = self.control_path_var.get().strip()

        self.append_log(f"[{_now()}] Enviando recibos…")
        self.is_running = True
        self.update_generate_state()

        t = threading.Thread(
            target=self._worker_send,
            args=(payroll_path, control_path),
            daemon=True,
        )
        t.start()
        self.after(100, self._drain_queue)

    def _worker_send(self, payroll_path: str, control_path: str):
        try:
            send_payroll_emails(
                payroll_path,
                control_path,
                progress_cb=lambda msg: self.msg_q.put(("log", msg)),
            )
            self.msg_q.put(("done", True))
        except Exception as e:
            self.msg_q.put(("log", f"✗ Error: {e}"))
            self.msg_q.put(("done", False))

    def _drain_queue(self):
        try:
            while True:
                kind, payload = self.msg_q.get_nowait()
                if kind == "log":
                    self.append_log(payload)
                elif kind == "done":
                    self.is_running = False
                    self.update_generate_state()
        except queue.Empty:
            if self.is_running:
                self.after(120, self._drain_queue)


def _now():
    return datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    # check_license_on_startup()
    App().mainloop()
