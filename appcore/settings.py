import json
from pathlib import Path
from .paths import resource_root, user_data_dir


class Settings:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory else user_data_dir()
        self.path = self.directory / "settings.json"
        self.values = json.loads((resource_root() / "settings.default.json").read_text(encoding="utf-8"))
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                self.values.update(saved)
        except (OSError, ValueError):
            pass

    def save(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.values, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self.path)
