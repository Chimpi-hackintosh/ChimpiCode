# 🐒 ChimpiCode

**The Xcode replacement powered by ChimpiAI**

ChimpiCode é um clone do Xcode feito em Python + CustomTkinter que compila `.py`, `.c`, `.cpp`, `.swift` e exporta `.app` / `.ipa`. 
Roda em Windows, Linux e Mac, com preview de iPhone real.

> **ChimpiAI é usado a base Ollama**

---

### ✨ Características

- **Editor estilo Xcode** - Project Navigator, Code Editor, Preview iPhone, Console
- **Multi-linguagem:**
    - `.py` -> Python + PyInstaller -> `.app`
    - `.c / .h` -> gcc / clang
    - `.cpp / .cc / .cxx / .hpp` -> g++ / clang++ (C++20)
    - `.swift / .m / .mm` -> swiftc (Mac)
    - `.app` -> abre direto
- **Preview iPhone** - Moldura ChimpiPhone 1 com notch, console verde estilo terminal
- **ChimpiAI** - Agente IA local via Ollama. Qualquer modelo: `llama3.1`, `qwen2.5-coder`, `codellama`, `deepseek-coder`
- **Export .app / .ipa** - Gera bundle `ChimpiApp.app/Contents/MacOS/` com `Info.plist`

### 📦 Instalação

```bash
# 1. Instale o Ollama
https://ollama.com

# 2. Baixe um modelo
ollama pull qwen2.5-coder
ollama serve

# 3. Instale deps
pip install customtkinter requests

# 4. Rode o ChimpiCode
python chimpicode.py
