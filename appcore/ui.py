import queue
import re
import shutil
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

import customtkinter as ctk
import requests

from . import VERSION
from .builds import BuildError, build_and_run, export_python, native_target
from .i18n import Translator
from .settings import Settings


class ChimpiCode(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.settings = Settings()
        self.t = Translator(self.settings.values.get("language", "auto"))
        self.title(f"ChimpiCode {VERSION} — ChimpiAI")
        self.geometry("1380x840")
        self.minsize(1060, 660)
        self.events = queue.Queue()
        self.busy = False
        self.current_file = None
        self.original_text = ""
        self.suggested_code = ""
        default_project = self.settings.directory / "Projects"
        saved_project = Path(self.settings.values.get("project_path") or default_project)
        self.project_path = saved_project if saved_project.is_dir() else default_project
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.protocol("WM_DELETE_WINDOW", self.close)

        toolbar = ctk.CTkFrame(self, fg_color="#191919")
        toolbar.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(toolbar, text="🐒 ChimpiCode", text_color="#FFD04A", font=("Arial", 20, "bold")).pack(side="left", padx=12)
        self.model = ctk.CTkEntry(toolbar, width=155)
        self.model.insert(0, self.settings.values["model"])
        self.model.pack(side="left", padx=5)
        self.build_button = ctk.CTkButton(toolbar, text=self.t("build"), command=self.run_build, fg_color="#D59E16", text_color="#101010", width=160)
        self.build_button.pack(side="left", padx=5)
        self.target = ctk.CTkOptionMenu(toolbar, values=[".app", ".exe", ".msi"], width=75)
        import sys
        self.target.set(".app" if sys.platform == "darwin" else ".exe")
        self.target.pack(side="left", padx=5)
        self.export_button = ctk.CTkButton(toolbar, text=self.t("export"), command=self.export, width=90, fg_color="#7154C8")
        self.export_button.pack(side="left", padx=5)
        self.clean_button = ctk.CTkButton(toolbar, text=self.t("clean"), command=self.clean, width=120, fg_color="#333333")
        self.clean_button.pack(side="left", padx=5)
        language = ctk.CTkOptionMenu(toolbar, values=["auto", "pt-BR", "en"], width=85, command=self.language_changed)
        language.set(self.settings.values["language"])
        language.pack(side="right", padx=8)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=8)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)
        left = ctk.CTkFrame(main, width=195)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(left, text=self.t("project"), font=("Arial", 14, "bold")).pack(pady=8)
        self.project_label = ctk.CTkLabel(left, text=str(self.project_path), wraplength=185, text_color="#AAAAAA")
        self.project_label.pack(padx=6)
        self.files = ctk.CTkScrollableFrame(left, width=180)
        self.files.pack(fill="both", expand=True, padx=6, pady=6)
        self.navigation_buttons = []
        for key, callback in [("open", self.open_project), ("new", self.new_file), ("save", self.save_file),
                              ("save_as", lambda: self.save_file(True)), ("python", self.choose_python)]:
            button = ctk.CTkButton(left, text=self.t(key), command=callback, fg_color="#333333")
            button.pack(fill="x", padx=6, pady=3)
            self.navigation_buttons.append(button)
        center = ctk.CTkFrame(main)
        center.grid(row=0, column=1, sticky="nsew")
        self.file_label = ctk.CTkLabel(center, text="main.py", anchor="w")
        self.file_label.pack(fill="x", padx=10)
        tabs = ctk.CTkTabview(center)
        tabs.pack(fill="both", expand=True)
        tabs.add(self.t("code"))
        tabs.add(self.t("preview"))
        self.editor = ctk.CTkTextbox(tabs.tab(self.t("code")), font=("Courier", 13), wrap="none", undo=True)
        self.editor.pack(fill="both", expand=True)
        self.preview = ctk.CTkTextbox(tabs.tab(self.t("preview")), font=("Courier", 12), fg_color="#111111", text_color="#FFD04A")
        self.preview.pack(fill="both", expand=True, padx=18, pady=18)
        self.preview.insert("end", self.t("preview_note") + "\n")
        right = ctk.CTkFrame(main, width=320, fg_color="#171717")
        right.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(right, text="🐒 ChimpiAI", font=("Arial", 18, "bold"), text_color="#FFD04A").pack(pady=6)
        ctk.CTkLabel(right, text=self.t("ai_subtitle")).pack()
        self.chat = ctk.CTkTextbox(right, width=300, height=245)
        self.chat.pack(fill="x", padx=8, pady=8)
        self.chat.insert("end", self.t("welcome") + "\n")
        self.prompt = ctk.CTkEntry(right, placeholder_text=self.t("prompt"))
        self.prompt.pack(fill="x", padx=8, pady=4)
        self.ask_button = ctk.CTkButton(right, text=self.t("ask"), command=self.ask)
        self.ask_button.pack(fill="x", padx=8, pady=4)
        self.insert_button = ctk.CTkButton(right, text=self.t("insert"), command=self.insert_code, fg_color="#333333")
        self.insert_button.pack(fill="x", padx=8, pady=4)
        ctk.CTkLabel(right, text=self.t("console")).pack(pady=(12, 0))
        self.console = ctk.CTkTextbox(right, width=300, font=("Courier", 11))
        self.console.pack(fill="both", expand=True, padx=8, pady=8)
        self.status = ctk.CTkLabel(self, text=self.t("about", version=VERSION), anchor="w")
        self.status.pack(fill="x", padx=12, pady=4)
        self.bind("<Control-s>", lambda event: self.save_file())
        self.bind("<Command-s>", lambda event: self.save_file())
        self.set_text('print("Hello from ChimpiCode")\n')
        self.refresh_files()
        self.after(60, self.poll)

    def set_text(self, value):
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", value)
        self.original_text = value

    def text(self):
        return self.editor.get("1.0", "end-1c")

    def log(self, text):
        self.console.insert("end", text + "\n")
        self.console.see("end")

    def confirm_changes(self):
        if self.text() == self.original_text:
            return True
        answer = messagebox.askyesnocancel("ChimpiCode", self.t("unsaved"), parent=self)
        return self.save_file() if answer else answer is False

    def refresh_files(self):
        for widget in self.files.winfo_children():
            widget.destroy()
        self.project_label.configure(text=str(self.project_path))
        extensions = {".py", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".swift", ".json", ".plist", ".md"}
        for file in sorted(self.project_path.iterdir()):
            if file.is_file() and file.suffix.lower() in extensions:
                ctk.CTkButton(self.files, text=file.name, anchor="w", width=160, fg_color="#282828",
                              command=lambda path=file: self.load_file(path)).pack(fill="x", pady=2)

    def load_file(self, path):
        if self.busy or not self.confirm_changes():
            return
        try:
            value = path.read_text(encoding="utf-8")
            self.current_file = path
            self.set_text(value)
            self.file_label.configure(text=path.name)
        except (OSError, UnicodeError) as exc:
            messagebox.showerror(self.t("error"), self.t("file_error", details=exc), parent=self)

    def open_project(self):
        if not self.confirm_changes():
            return
        chosen = filedialog.askdirectory(parent=self, initialdir=self.project_path)
        if chosen:
            self.project_path = Path(chosen)
            self.current_file = None
            self.set_text("")
            self.file_label.configure(text="main.py")
            self.refresh_files()

    def new_file(self):
        if self.confirm_changes():
            self.current_file = None
            self.set_text("")
            self.file_label.configure(text="main.py")

    def save_file(self, save_as=False):
        if self.current_file is None or save_as:
            chosen = filedialog.asksaveasfilename(parent=self, title=self.t("save_as"), initialdir=self.project_path,
                                                 initialfile=self.current_file.name if self.current_file else "main.py",
                                                 defaultextension=".py")
            if not chosen:
                return False
            path = Path(chosen)
        else:
            path = self.current_file
        try:
            path.write_text(self.text(), encoding="utf-8")
            self.current_file = path
            self.project_path = path.parent
            self.original_text = self.text()
            self.file_label.configure(text=path.name)
            self.refresh_files()
            return True
        except OSError as exc:
            messagebox.showerror(self.t("error"), self.t("file_error", details=exc), parent=self)
            return False

    def choose_python(self):
        chosen = filedialog.askopenfilename(parent=self, title=self.t("choose_python"))
        if chosen:
            self.settings.values["python_path"] = chosen
            self.settings.save()

    def language_changed(self, language):
        self.settings.values["language"] = language
        self.settings.save()
        messagebox.showinfo("ChimpiCode", self.t("restart_language"), parent=self)

    def start_job(self, function, kind):
        if self.busy:
            return
        self.busy = True
        self.status.configure(text=self.t("busy"))
        for button in [self.build_button, self.export_button, self.clean_button, self.ask_button, self.insert_button, *self.navigation_buttons]:
            button.configure(state="disabled")
        self.editor.configure(state="disabled")
        def worker():
            try:
                self.events.put((kind, function()))
            except Exception as exc:
                self.events.put(("error", exc))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                self.busy = False
                for button in [self.build_button, self.export_button, self.clean_button, self.ask_button, self.insert_button, *self.navigation_buttons]:
                    button.configure(state="normal")
                self.editor.configure(state="normal")
                self.status.configure(text=self.t("ready"))
                if kind == "error":
                    self.log(self.t(value.key, **value.values) if isinstance(value, BuildError) else str(value))
                    self.status.configure(text=self.t("failed"))
                elif kind == "ai":
                    self.chat.insert("end", "\nChimpiAI: " + value + "\n")
                    self.chat.see("end")
                    matches = re.findall(r"```[^\n]*\n(.*?)```", value, re.S)
                    self.suggested_code = matches[0] if matches else ""
                else:
                    result, output_path = value if kind == "export" else (value, None)
                    self.log(result.output)
                    self.log(self.t("ok" if result.ok else "failed"))
                    self.status.configure(text=self.t("ok" if result.ok else "failed"))
                    self.preview.delete("1.0", "end")
                    self.preview.insert("end", self.t("preview_note") + "\n\n" + result.output[:12000])
                    if output_path:
                        self.log(self.t("exported", path=output_path))
                    self.refresh_files()
        except queue.Empty:
            pass
        self.after(60, self.poll)

    def run_build(self):
        if self.busy or not self.save_file():
            return
        source, python = self.current_file, self.settings.values["python_path"]
        self.start_job(lambda: build_and_run(source, python), "build")

    def export(self):
        if self.busy:
            return
        target = self.target.get()
        try:
            native_target(target)
        except BuildError as exc:
            messagebox.showinfo("ChimpiCode", self.t(exc.key, **exc.values), parent=self)
            return
        if not self.save_file():
            return
        if self.current_file.suffix.lower() != ".py":
            messagebox.showinfo("ChimpiCode", self.t("python_export_only"), parent=self)
            return
        name = simpledialog.askstring("ChimpiCode", self.t("export_name"), initialvalue="ChimpiApp", parent=self)
        if not name:
            return
        folder = filedialog.askdirectory(parent=self, title=self.t("export_folder"), initialdir=self.project_path)
        if not folder:
            return
        source, python = self.current_file, self.settings.values["python_path"]
        self.start_job(lambda: export_python(source, target, folder, name, python), "export")

    def ask(self):
        question, model = self.prompt.get().strip(), self.model.get().strip()
        if self.busy or not question or not model:
            return
        self.chat.insert("end", f"\n{self.t('you')}: {question}\n{self.t('thinking')}\n")
        language = self.t.language
        def request():
            try:
                response = requests.post("http://localhost:11434/api/generate", json={
                    "model": model,
                    "prompt": f"You are ChimpiAI, a coding assistant in ChimpiCode. Reply in {language}. Do not claim to compile code or run an iOS simulator. User: {question}",
                    "stream": False}, timeout=(10, 180))
                response.raise_for_status()
                payload = response.json()
                if payload.get("error"):
                    raise ValueError(payload["error"])
                return payload["response"]
            except (requests.RequestException, ValueError, KeyError) as exc:
                raise BuildError("ai_error", details=str(exc)) from exc
        self.start_job(request, "ai")

    def insert_code(self):
        if not self.suggested_code:
            self.log(self.t("no_code"))
        elif messagebox.askyesno("ChimpiCode", self.t("replace_code"), parent=self):
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", self.suggested_code)

    def clean(self):
        if self.busy:
            return
        if messagebox.askyesno("ChimpiCode", self.t("clean_confirm"), parent=self):
            work = self.project_path / ".chimpicode" / "work"
            if work.is_symlink() or work.parent.is_symlink():
                self.log(self.t("failed"))
                return
            if work.exists():
                shutil.rmtree(work)
            self.log(self.t("clean_done"))

    def close(self):
        if self.busy or not self.confirm_changes():
            return
        self.settings.values.update(project_path=str(self.project_path), model=self.model.get())
        self.settings.save()
        self.destroy()
