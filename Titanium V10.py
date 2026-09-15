from __future__ import annotations

import queue
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from titanium import ANDROID_API, APP_NAME, VERSION
from titanium.analyzer import Finding, analyze_source
from titanium.builder import AndroidBuilder
from titanium.core import ANDROID_LICENSE_URL, ConfigStore, Paths, ToolchainManager


class App:
    def __init__(self, root):
        self.root = root
        self.p = Paths()
        self.store = ConfigStore(self.p.config)
        self.q = queue.Queue()
        self.logs: list[tuple[str, str]] = []
        self.t = ToolchainManager(self.p, self.emit)
        self.b = AndroidBuilder(self.p, self.t, self.emit)
        self.vars = {
            k: tk.StringVar()
            for k in [
                "app_name", "package", "version_name", "version_code", "min_sdk", "target_sdk",
                "source_type", "source", "output_dir", "export_format", "build_mode", "orientation",
                "keystore", "store_password", "key_alias", "key_password",
            ]
        }
        self.flags = {k: tk.BooleanVar() for k in ["camera", "microphone", "location", "sign_release"]}
        self.mode = tk.StringVar(value="Simple")
        self.status = tk.StringVar(value="Checking build engine...")
        self.preflight_status = tk.StringVar(value="Project not analyzed yet")
        self._first_run_shown = False

        defaults = {
            "app_name": "MyApp",
            "package": "com.swir.myapp",
            "version_name": "1.0.0",
            "version_code": "1",
            "min_sdk": "24",
            "target_sdk": str(ANDROID_API),
            "source_type": "Folder",
            "output_dir": str(Path.home() / "Desktop"),
            "export_format": "APK",
            "build_mode": "Debug",
            "orientation": "unspecified",
        }
        for k, v in defaults.items():
            self.vars[k].set(v)

        self.ui()
        self.load()
        self.apply_mode()
        self.root.after(100, self.drain)
        self.refresh()
        self.root.after(700, self.first_run_wizard)

    def emit(self, kind, text):
        self.q.put((kind, str(text)))

    def drain(self):
        try:
            while True:
                kind, text = self.q.get_nowait()
                if kind == "status":
                    self.status.set(text)
                    continue
                level = "DETAIL" if kind == "detail" else "INFO"
                if text.startswith("ERROR:"):
                    level = "ERROR"
                elif text.startswith("SUCCESS:"):
                    level = "SUCCESS"
                elif "warning" in text.lower():
                    level = "WARNING"
                stamp = datetime.now().strftime("%H:%M:%S")
                line = f"[{stamp}] {level:<7} {text}"
                self.logs.append((level, line))
                self.console.config(state="normal")
                self.console.insert("end", line + "\n")
                self.console.see("end")
                self.console.config(state="disabled")
        except queue.Empty:
            pass
        self.root.after(100, self.drain)

    def ui(self):
        self.root.title(f"{APP_NAME} {VERSION}")
        self.root.geometry("1100x800")
        self.root.minsize(920, 680)

        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x")
        title = ttk.Frame(header)
        title.pack(side="left", fill="x", expand=True)
        ttk.Label(title, text=APP_NAME, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(title, text=f"v{VERSION}  •  HTML / ZIP / URL → APK / AAB").pack(anchor="w")

        mode_box = ttk.Frame(header)
        mode_box.pack(side="right")
        ttk.Label(mode_box, text="Interface mode").pack(anchor="e")
        mode = ttk.Combobox(mode_box, textvariable=self.mode, values=["Simple", "Advanced"], state="readonly", width=12)
        mode.pack(anchor="e")
        mode.bind("<<ComboboxSelected>>", lambda _e: self.apply_mode())

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill="both", expand=True, pady=10)
        build = ttk.Frame(self.notebook, padding=12)
        engine = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(build, text="Build")
        self.notebook.add(engine, text="Build Engine")
        build.columnconfigure(0, weight=1)

        quick = ttk.LabelFrame(build, text="App", padding=10)
        quick.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        quick.columnconfigure(0, weight=1)
        quick.columnconfigure(1, weight=1)
        for col, (label, key) in enumerate([("App name", "app_name"), ("Package", "package")]):
            ttk.Label(quick, text=label).grid(row=0, column=col, sticky="w", padx=(0, 12))
            ttk.Entry(quick, textvariable=self.vars[key]).grid(row=1, column=col, sticky="ew", padx=(0, 12), pady=(3, 0))

        source = ttk.LabelFrame(build, text="Web source", padding=10)
        source.grid(row=1, column=0, sticky="ew", pady=8)
        source.columnconfigure(1, weight=1)
        source_type = ttk.Combobox(source, textvariable=self.vars["source_type"], values=["Folder", "ZIP", "URL"], state="readonly", width=10)
        source_type.grid(row=0, column=0, sticky="w")
        source_type.bind("<<ComboboxSelected>>", lambda _e: self._source_type_changed())
        ttk.Entry(source, textvariable=self.vars["source"]).grid(row=0, column=1, sticky="ew", padx=8)
        self.browse_button = ttk.Button(source, text="Browse", command=self.browse_source)
        self.browse_button.grid(row=0, column=2)
        ttk.Label(source, textvariable=self.preflight_status).grid(row=1, column=0, columnspan=3, sticky="w", pady=(8, 0))

        self.advanced_panel = ttk.LabelFrame(build, text="Advanced build settings", padding=10)
        self.advanced_panel.grid(row=2, column=0, sticky="ew", pady=8)
        self.advanced_panel.columnconfigure(0, weight=1)
        self.advanced_panel.columnconfigure(1, weight=1)

        fields = [
            ("Version name", "version_name"), ("Version code", "version_code"),
            ("Min SDK", "min_sdk"), ("Target SDK", "target_sdk"),
        ]
        for i, (label, key) in enumerate(fields):
            row, col = divmod(i, 2)
            ttk.Label(self.advanced_panel, text=label).grid(row=row * 2, column=col, sticky="w", padx=(0, 12))
            ttk.Entry(self.advanced_panel, textvariable=self.vars[key]).grid(row=row * 2 + 1, column=col, sticky="ew", padx=(0, 12), pady=(2, 7))

        options = ttk.Frame(self.advanced_panel)
        options.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        for col, (key, vals) in enumerate([
            ("export_format", ["APK", "AAB"]),
            ("build_mode", ["Debug", "Release"]),
            ("orientation", ["unspecified", "portrait", "landscape"]),
        ]):
            ttk.Combobox(options, textvariable=self.vars[key], values=vals, state="readonly", width=15).grid(row=0, column=col, sticky="w", padx=(0, 8))
        for col, key in enumerate(["camera", "microphone", "location"]):
            ttk.Checkbutton(options, text=key.title(), variable=self.flags[key]).grid(row=1, column=col, sticky="w", pady=(8, 0))

        signing = ttk.LabelFrame(self.advanced_panel, text="Release signing — passwords are never saved", padding=8)
        signing.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        for col in range(3):
            signing.columnconfigure(col, weight=1)
        ttk.Checkbutton(signing, text="Sign release", variable=self.flags["sign_release"]).grid(row=0, column=0, sticky="w")
        ttk.Entry(signing, textvariable=self.vars["keystore"]).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        ttk.Button(signing, text="Keystore", command=self.browse_keystore).grid(row=1, column=3, padx=(6, 0), pady=(5, 0))
        for col, (key, label) in enumerate([
            ("store_password", "Store password"), ("key_alias", "Key alias"), ("key_password", "Key password")
        ]):
            ttk.Label(signing, text=label).grid(row=2, column=col, sticky="w", pady=(7, 0))
            ttk.Entry(signing, textvariable=self.vars[key], show="*" if "password" in key else "").grid(row=3, column=col, sticky="ew", padx=(0, 5))

        output = ttk.LabelFrame(build, text="Output", padding=10)
        output.grid(row=3, column=0, sticky="ew", pady=8)
        output.columnconfigure(0, weight=1)
        ttk.Entry(output, textvariable=self.vars["output_dir"]).grid(row=0, column=0, sticky="ew")
        ttk.Button(output, text="Choose folder", command=self.browse_output).grid(row=0, column=1, padx=(8, 0))

        actions = ttk.Frame(build)
        actions.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        actions.columnconfigure(1, weight=1)
        ttk.Button(actions, text="ANALYZE PROJECT", command=self.start_analysis).grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=6)
        self.build_button = ttk.Button(actions, text="BUILD APK", command=self.start_build)
        self.build_button.grid(row=0, column=1, sticky="ew", ipady=6)

        ttk.Label(engine, text="Managed Build Engine", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(engine, text="No Android Studio, Python, Node.js or Cordova is required on the target PC.").pack(anchor="w")
        ttk.Label(engine, text="Repair only touches Titanium-managed files; system Java/Android Studio are never removed.").pack(anchor="w", pady=(2, 0))
        self.engine = tk.Text(engine, height=12, state="disabled", font=("Consolas", 10))
        self.engine.pack(fill="x", pady=10)
        engine_buttons = ttk.Frame(engine)
        engine_buttons.pack(fill="x")
        ttk.Button(engine_buttons, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Button(engine_buttons, text="Prepare Build Engine", command=self.prepare).pack(side="left", padx=8)
        ttk.Button(engine_buttons, text="Repair Build Engine", command=self.repair).pack(side="left")
        ttk.Label(engine, text=f"Android SDK license: {ANDROID_LICENSE_URL}").pack(anchor="w", pady=10)

        status_row = ttk.Frame(outer)
        status_row.pack(fill="x")
        ttk.Label(status_row, textvariable=self.status).pack(side="left", fill="x", expand=True)
        ttk.Button(status_row, text="Clear log", command=self.clear_log).pack(side="right")
        ttk.Button(status_row, text="Copy log", command=self.copy_log).pack(side="right", padx=(0, 6))
        self.console = tk.Text(outer, height=10, state="disabled", font=("Consolas", 9))
        self.console.pack(fill="x", pady=(5, 0))
        self._source_type_changed()

    def cfg(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        data.update({k: v.get() for k, v in self.flags.items()})
        data["ui_mode"] = self.mode.get()
        return data

    def load(self):
        c = self.store.load()
        for k, v in self.vars.items():
            if k in c and k not in {"store_password", "key_password"}:
                v.set(c[k])
        for k, v in self.flags.items():
            if k in c:
                v.set(bool(c[k]))
        if c.get("ui_mode") in {"Simple", "Advanced"}:
            self.mode.set(c["ui_mode"])

    def apply_mode(self):
        simple = self.mode.get() == "Simple"
        if simple:
            self.advanced_panel.grid_remove()
            self.vars["export_format"].set("APK")
            self.vars["build_mode"].set("Debug")
            self.vars["target_sdk"].set(str(ANDROID_API))
            self.build_button.config(text="BUILD APK")
            self.status.set("Simple mode — Titanium chooses safe defaults")
        else:
            self.advanced_panel.grid()
            self.build_button.config(text="BUILD APK / AAB")
            self.status.set("Advanced mode")
        self.store.save(self.cfg())

    def _source_type_changed(self):
        if self.vars["source_type"].get() == "URL":
            self.browse_button.state(["disabled"])
        else:
            self.browse_button.state(["!disabled"])
        self.preflight_status.set("Project not analyzed yet")

    def browse_source(self):
        kind = self.vars["source_type"].get()
        if kind == "Folder":
            selected = filedialog.askdirectory()
        elif kind == "ZIP":
            selected = filedialog.askopenfilename(filetypes=[("ZIP", "*.zip")])
        else:
            selected = ""
        if selected:
            self.vars["source"].set(selected)
            self.preflight_status.set("Project changed — analyze before build")

    def browse_output(self):
        selected = filedialog.askdirectory()
        if selected:
            self.vars["output_dir"].set(selected)

    def browse_keystore(self):
        selected = filedialog.askopenfilename(filetypes=[("Keystore", "*.jks *.keystore"), ("All", "*.*")])
        if selected:
            self.vars["keystore"].set(selected)

    def clear_log(self):
        self.logs.clear()
        self.console.config(state="normal")
        self.console.delete("1.0", "end")
        self.console.config(state="disabled")

    def copy_log(self):
        text = "\n".join(line for _level, line in self.logs)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status.set("Log copied to clipboard")

    def refresh(self):
        data = self.t.status()
        text = "\n".join(f"{k:24} {v}" for k, v in data.items())
        self.engine.config(state="normal")
        self.engine.delete("1.0", "end")
        self.engine.insert("1.0", text)
        self.engine.config(state="disabled")
        self.status.set("Build engine ready" if self.t.ready() else "Build engine needs preparation")

    def _license_consent(self, title):
        return messagebox.askyesno(
            title,
            "Titanium may download a private JDK, Gradle and Android SDK components for this Windows user. "
            "Nothing is installed system-wide.\n\nContinue only if you accept the Android SDK license terms.",
        )

    def prepare(self):
        if not self._license_consent("Prepare Build Engine"):
            return
        self.status.set("Preparing build engine...")
        threading.Thread(target=self._prepare, daemon=True).start()

    def _prepare(self):
        try:
            self.t.provision()
            self.emit("log", "SUCCESS: Build engine prepared")
            self.emit("status", "Build engine ready")
        except Exception as exc:
            self.emit("log", f"ERROR: {exc}")
            self.emit("status", "Build engine preparation failed")
        self.root.after(0, self.refresh)

    def repair(self):
        if not self._license_consent("Repair Build Engine"):
            return
        if not messagebox.askyesno(
            "Repair Build Engine",
            "Titanium will scan its managed toolchain, remove incomplete managed components and download only what is missing.\n\nContinue?",
        ):
            return
        self.status.set("Repairing build engine...")
        threading.Thread(target=self._repair, daemon=True).start()

    def _repair(self):
        try:
            self.t.repair()
            self.emit("log", "SUCCESS: Build engine repair completed")
            self.emit("status", "Build engine ready")
        except Exception as exc:
            self.emit("log", f"ERROR: Repair failed: {exc}")
            self.emit("status", "Build engine repair failed")
        self.root.after(0, self.refresh)

    def first_run_wizard(self):
        if self._first_run_shown or self.t.ready():
            return
        self._first_run_shown = True
        win = tk.Toplevel(self.root)
        win.title("Titanium First Run")
        win.transient(self.root)
        win.resizable(False, False)
        box = ttk.Frame(win, padding=20)
        box.pack(fill="both", expand=True)
        ttk.Label(box, text="Prepare Titanium for Android builds", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(
            box,
            text="Titanium did not find a complete build engine. It can prepare a private toolchain automatically — no Android Studio, Python, Node.js or Cordova installation is required.",
            wraplength=560,
            justify="left",
        ).pack(anchor="w", pady=(8, 14))
        ttk.Label(box, text="1. Accept the Android SDK terms\n2. Titanium verifies and prepares the required tools\n3. Build HTML/ZIP/URL projects to APK or AAB", justify="left").pack(anchor="w")
        row = ttk.Frame(box)
        row.pack(fill="x", pady=(18, 0))
        ttk.Button(row, text="Later", command=win.destroy).pack(side="right")
        ttk.Button(row, text="Prepare now", command=lambda: self._wizard_prepare(win)).pack(side="right", padx=(0, 8))
        win.grab_set()

    def _wizard_prepare(self, win):
        win.destroy()
        self.notebook.select(1)
        self.prepare()

    def start_analysis(self):
        c = self.cfg()
        self.preflight_status.set("Analyzing project...")
        self.status.set("Analyzing project...")
        threading.Thread(target=self._analyze_worker, args=(c,), daemon=True).start()

    def _analyze_worker(self, c):
        try:
            findings = analyze_source(c["source_type"], c["source"])
        except Exception as exc:
            findings = [Finding("ERROR", f"Analyzer failed: {exc}")]
        self.root.after(0, lambda: self.show_analysis(findings))

    def show_analysis(self, findings):
        errors = sum(f.severity == "ERROR" for f in findings)
        warnings = sum(f.severity == "WARNING" for f in findings)
        if errors:
            self.preflight_status.set(f"Preflight: {errors} error(s), {warnings} warning(s)")
            self.status.set("Project analysis found blocking errors")
        elif warnings:
            self.preflight_status.set(f"Preflight passed with {warnings} warning(s)")
            self.status.set("Project analysis completed with warnings")
        else:
            self.preflight_status.set("Preflight passed — ready to build")
            self.status.set("Project analysis passed")

        win = tk.Toplevel(self.root)
        win.title("Titanium Project Analyzer")
        win.geometry("760x420")
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Project Preflight Report", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tree = ttk.Treeview(frame, columns=("severity", "message"), show="headings", height=13)
        tree.heading("severity", text="Level")
        tree.heading("message", text="Finding")
        tree.column("severity", width=95, stretch=False)
        tree.column("message", width=620, stretch=True)
        tree.pack(fill="both", expand=True, pady=10)
        for finding in findings:
            tree.insert("", "end", values=(finding.severity, finding.message))
        ttk.Button(frame, text="Close", command=win.destroy).pack(anchor="e")

    def _preflight_for_build(self, c):
        findings = analyze_source(c["source_type"], c["source"])
        errors = [f.message for f in findings if f.severity == "ERROR"]
        if errors:
            raise ValueError("Project Analyzer blocked the build:\n\n" + "\n".join(f"• {x}" for x in errors[:8]))
        warnings = [f.message for f in findings if f.severity == "WARNING"]
        if warnings:
            self.emit("log", "WARNING: Preflight warnings: " + " | ".join(warnings))
        self.preflight_status.set("Preflight passed — ready to build")

    def start_build(self):
        c = self.cfg()
        try:
            self.b.validate(c)
            self._preflight_for_build(c)
        except Exception as exc:
            messagebox.showerror("Validation", str(exc))
            return
        self.store.save(c)
        self.status.set("Building...")
        threading.Thread(target=self._build, args=(c,), daemon=True).start()

    def _build(self, c):
        try:
            out = self.b.build(c)
            self.emit("log", f"SUCCESS: {out}")
            self.emit("status", f"Build complete: {out.name}")
            self.root.after(0, lambda: messagebox.showinfo("Titanium", f"Build complete:\n{out}"))
        except Exception as exc:
            self.emit("log", f"ERROR: {exc}")
            self.emit("status", "Build failed")
            self.root.after(0, lambda msg=str(exc): messagebox.showerror("Build failed", msg))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
