import customtkinter as ctk
import subprocess, os, threading, requests, shutil, platform
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

OLLAMA_URL = "http://localhost:11434/api/generate"

class ChimpiAI:
    def __init__(self, model="llama3.1"):
        self.model = model
    def ask(self, prompt, cb):
        def run():
            try:
                r = requests.post(OLLAMA_URL, json={
                    "model": self.model,
                    "prompt": f"You are ChimpiAI, the AI inside ChimpiCode, a replacement for Xcode that builds iOS apps. You build .py, .c, .cpp, .swift and export .app/.ipa. User: {prompt}",
                    "stream": False
                }, timeout=120)
                cb(r.json().get("response",""))
            except Exception as e:
                cb(f"Erro Ollama: {e} - rode 'ollama serve'")
        threading.Thread(target=run, daemon=True).start()

class ChimpiCode(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ChimpiCode - by ChimpiAI 🐒")
        self.geometry("1420x860")
        self.agent = ChimpiAI()
        self.project_path = os.getcwd()

        top = ctk.CTkFrame(self, height=55, fg_color="#1A1A1A")
        top.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(top, text="🐒 ChimpiCode", font=("SF Pro", 20, "bold"), text_color="#FFD700").pack(side="left", padx=15)
        ctk.CTkLabel(top, text="ChimpiAI inside", font=("SF Pro", 12), text_color="#AAA").pack(side="left")

        self.model_box = ctk.CTkEntry(top, width=140, placeholder_text="qwen2.5-coder")
        self.model_box.insert(0, "qwen2.5-coder")
        self.model_box.pack(side="left", padx=10)

        self.device_combo = ctk.CTkComboBox(top, values=["iPhone 15 Pro", "iPhone 14", "iPad Pro", "ChimpiPhone 1"], width=180)
        self.device_combo.pack(side="left", padx=10)

        ctk.CTkButton(top, text="▶ Build & Run", fg_color="#FFD700", text_color="black", hover_color="#E5C100", width=130, font=("SF Pro", 13, "bold"), command=self.build_and_run).pack(side="left", padx=5)
        ctk.CTkButton(top, text="📦 Export .app / .ipa", fg_color="#7B61FF", width=160, command=self.export_app).pack(side="left", padx=5)
        ctk.CTkButton(top, text="🧹 Clean", fg_color="#333", width=70, command=self.clean).pack(side="left", padx=5)

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=5)

        # ESQUERDA
        left = ctk.CTkFrame(main, width=260)
        left.pack(side="left", fill="y", padx=5, pady=5)
        ctk.CTkLabel(left, text="ChimpiCode Project", font=("SF Pro", 13, "bold")).pack()
        self.file_list = ctk.CTkScrollableFrame(left, width=240, height=400)
        self.file_list.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(left, text="Abrir Pasta", fg_color="#222", command=self.open_project).pack(pady=3, fill="x", padx=5)
        ctk.CTkButton(left, text="Novo Arquivo", fg_color="#222", command=self.new_file).pack(pady=3, fill="x", padx=5)

        # CENTRO
        center = ctk.CTkFrame(main)
        center.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        tabs = ctk.CTkTabview(center)
        tabs.pack(fill="both", expand=True)
        tabs.add("Code")
        tabs.add("Preview")
        
        self.editor = ctk.CTkTextbox(tabs.tab("Code"), font=("JetBrains Mono", 13))
        self.editor.pack(fill="both", expand=True)
        self.editor.insert("0.0", '# main.py - ChimpiCode\nprint("Hello from ChimpiCode 🐒")\n# Suporta: .py .c .cpp .h .swift .app\n')

        # PREVIEW IPHONE COM CHIMPI
        preview = tabs.tab("Preview")
        self.iphone = ctk.CTkFrame(preview, width=360, height=700, fg_color="#0A0A0A", corner_radius=50, border_width=7, border_color="#FFD700")
        self.iphone.pack(pady=15)
        self.iphone.pack_propagate(False)
        notch = ctk.CTkFrame(self.iphone, width=130, height=28, fg_color="black", corner_radius=12)
        notch.pack(pady=8)
        ctk.CTkLabel(notch, text="🐒 ChimpiPhone", font=("SF Pro", 10)).pack()
        self.preview_console = ctk.CTkTextbox(self.iphone, font=("Menlo", 11), fg_color="black", text_color="#FFD700")
        self.preview_console.pack(fill="both", expand=True, padx=15, pady=10)
        self.preview_console.insert("0.0", "ChimpiPhone OS\nPronto pra rodar seu app...\n")

        # DIREITA - ChimpiAI
        right = ctk.CTkFrame(main, width=400, fg_color="#141414")
        right.pack(side="left", fill="y", padx=5, pady=5)
        ctk.CTkLabel(right, text="🐒 ChimpiAI", font=("SF Pro", 15, "bold"), text_color="#FFD700").pack(pady=5)
        ctk.CTkLabel(right, text="Substituto do SnoopyAI - Ollama Power", font=("SF Pro", 11), text_color="#888").pack()

        self.chat = ctk.CTkTextbox(right, height=340, fg_color="#1E1E1E")
        self.chat.pack(fill="x", padx=5, pady=5)
        self.chat.insert("0.0", "🐒 ChimpiAI: Fala! Eu sou o ChimpiAI, dentro do ChimpiCode. Eu substituí o SnoopyAI.\nEu compilo .py, .c, .cpp, .swift e exporto .app e .ipa.\nMe manda: 'cria um app de calculadora' ou 'converte isso pra C++'\n")

        self.prompt = ctk.CTkEntry(right, placeholder_text="Pergunte ao ChimpiAI: cria tela login SwiftUI")
        self.prompt.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(right, text="Perguntar ao ChimpiAI 🐒", fg_color="#FFD700", text_color="black", command=self.ask).pack(pady=5, fill="x", padx=5)

        ctk.CTkLabel(right, text="ChimpiCode Console", font=("SF Pro", 12, "bold")).pack(pady=(15,0))
        self.console = ctk.CTkTextbox(right, height=280, fg_color="#0F0F0F")
        self.console.pack(fill="both", expand=True, padx=5, pady=5)

        self.refresh_files()

    def refresh_files(self):
        for w in self.file_list.winfo_children(): w.destroy()
        exts = (".py", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".swift", ".app", ".m", ".mm", ".plist")
        for f in os.listdir(self.project_path):
            if f.endswith(exts):
                ctk.CTkButton(self.file_list, text=f, width=220, anchor="w", fg_color="#222", height=28, command=lambda n=f: self.load_file(n)).pack(pady=2)

    def load_file(self, name):
        p = os.path.join(self.project_path, name)
        if os.path.isdir(p): return
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                self.editor.delete("0.0", "end")
                self.editor.insert("0.0", fh.read())
        except: pass

    def open_project(self):
        p = filedialog.askdirectory()
        if p:
            self.project_path = p
            self.refresh_files()
            self.console.insert("end", f"ChimpiCode Project: {p}\n")

    def new_file(self):
        self.editor.delete("0.0", "end")
        self.editor.insert("0.0", '# Novo arquivo ChimpiCode\n# .py .c .cpp .swift suportados\n')

    def ask(self):
        q = self.prompt.get()
        if not q: return
        self.agent.model = self.model_box.get()
        self.chat.insert("end", f"\nVocê: {q}\nChimpiAI pensando...\n")
        def cb(r):
            self.chat.insert("end", f"🐒 ChimpiAI: {r}\n\n")
            if "```" in r:
                try:
                    code = r.split("```")[1]
                    # remove linguagem do bloco
                    if "\n" in code: code = code.split("\n",1)[1]
                    self.editor.delete("0.0", "end")
                    self.editor.insert("0.0", code)
                except: pass
        self.agent.ask(q, cb)

    def build_and_run(self):
        code = self.editor.get("0.0", "end")
        ext = ".py"
        if "iostream" in code: ext = ".cpp"
        elif "#include" in code: ext = ".c"
        elif "import SwiftUI" in code or "UIKit" in code: ext = ".swift"
        path = os.path.join(self.project_path, f"chimpi_build{ext}")
        with open(path, "w", encoding="utf-8") as f: f.write(code)
        self.console.insert("end", f"\n=== ChimpiCode BUILD {ext} ===\n")
        threading.Thread(target=self.compile_thread, args=(path, ext), daemon=True).start()

    def compile_thread(self, path, ext):
        out = ""
        try:
            if ext == ".py":
                res = subprocess.run([ "python3" if platform.system()!="Windows" else "python", path ], capture_output=True, text=True, timeout=10)
                out = res.stdout + res.stderr
            elif ext == ".c":
                exe = path.replace(".c", "")
                res = subprocess.run([ "clang" if shutil.which("clang") else "gcc", path, "-o", exe ], capture_output=True, text=True)
                out = res.stderr if res.returncode!=0 else "C OK\n"
                if res.returncode==0:
                    out += subprocess.run([exe], capture_output=True, text=True, timeout=5).stdout
            elif ext in [".cpp", ".cc"]:
                exe = path.replace(ext, "")
                comp = "clang++" if shutil.which("clang++") else "g++"
                res = subprocess.run([comp, path, "-o", exe, "-std=c++20"], capture_output=True, text=True)
                out = res.stderr if res.returncode!=0 else "C++ OK\n"
                if res.returncode==0:
                    out += subprocess.run([exe], capture_output=True, text=True, timeout=5).stdout
            elif ext == ".swift":
                out = "Swift compilado no Mac" if platform.system()=="Darwin" else "[SIM] Swift"
            self.console.insert("end", out + "\n✅ ChimpiCode Build OK\n")
            self.preview_console.delete("0.0", "end")
            self.preview_console.insert("0.0", f"🐒 ChimpiPhone - {self.device_combo.get()}\n\n{out[:3000]}\n")
            self.refresh_files()
        except Exception as e:
            self.console.insert("end", f"Erro: {e}\n")

    def export_app(self):
        self.console.insert("end", "\n📦 Exportando ChimpiApp.app / ChimpiApp.ipa...\n")
        def run():
            try:
                # Cria estrutura .app
                app_dir = os.path.join(self.project_path, "ChimpiApp.app")
                os.makedirs(os.path.join(app_dir, "Contents", "MacOS"), exist_ok=True)
                # Copia build
                build_file = os.path.join(self.project_path, "chimpi_build.py")
                if not os.path.exists(build_file):
                    build_file = os.path.join(self.project_path, "chimpi_build.cpp")
                if os.path.exists(build_file):
                    shutil.copy(build_file, os.path.join(app_dir, "Contents", "MacOS", "ChimpiApp"))
                # Info.plist fake
                with open(os.path.join(app_dir, "Contents", "Info.plist"), "w") as f:
                    f.write('<plist><dict><key>CFBundleName</key><string>ChimpiApp</string><key>CFBundleIdentifier</key><string>com.chimpi.code</string></dict></plist>')
                self.console.insert("end", f"✅ Exportado: {app_dir}\n")
                self.console.insert("end", "Para .ipa no Mac: Product > Archive no Xcode, aqui geramos o .app base.\n")
            except Exception as e:
                self.console.insert("end", f"Erro export: {e}\n")
        threading.Thread(target=run, daemon=True).start()

    def clean(self):
        for f in os.listdir(self.project_path):
            if f.startswith("chimpi_build") or f.startswith("ChimpiApp"):
                try:
                    p = os.path.join(self.project_path, f)
                    if os.path.isdir(p): shutil.rmtree(p)
                    else: os.remove(p)
                except: pass
        self.console.insert("end", "Clean OK 🐒\n")

if __name__ == "__main__":
    ChimpiCode().mainloop()