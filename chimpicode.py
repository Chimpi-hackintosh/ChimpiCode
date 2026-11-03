"""ChimpiCode desktop entry point and packaged-runtime checks."""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) == 3 and sys.argv[1] in {"--self-test", "--gui-smoke"}:
        import customtkinter
        import requests
        from appcore import VERSION
        from appcore.i18n import Translator
        from appcore.paths import resource_root
        for language in ("en", "pt-BR"):
            Translator(language)
        result = {"ok": True, "version": VERSION, "resources": str(resource_root()),
                  "python": sys.version, "gui": False}
        if sys.argv[1] == "--gui-smoke":
            from appcore.ui import ChimpiCode
            app = ChimpiCode()
            app.after(500, app.destroy)
            app.mainloop()
            result["gui"] = True
        Path(sys.argv[2]).write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        return
    from appcore.ui import ChimpiCode
    ChimpiCode().mainloop()


if __name__ == "__main__":
    main()
