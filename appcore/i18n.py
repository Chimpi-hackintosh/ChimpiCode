import json
from .paths import preferred_ui_languages, resource_root


def resolve_language(candidates):
    for candidate in candidates:
        code = candidate.replace("_", "-").split(".")[0].lower()
        if code == "pt-br" or code.split("-")[0] == "pt":
            return "pt-BR"
        if code.split("-")[0] == "en":
            return "en"
    return "en"


class Translator:
    def __init__(self, override="auto"):
        self.language = resolve_language(preferred_ui_languages() if override == "auto" else [override])
        self.strings = json.loads((resource_root() / "locales" / f"{self.language}.json").read_text(encoding="utf-8"))

    def __call__(self, key, **values):
        return self.strings[key].format(**values)
