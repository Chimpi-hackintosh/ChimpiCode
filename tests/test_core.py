import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from appcore.builds import BuildError, Result, build_and_run, command, native_target, python_command
from appcore.i18n import Translator, resolve_language
from appcore.msi import WIX, write_wxs
from appcore.settings import Settings

ROOT = Path(__file__).resolve().parents[1]


class CoreTests(unittest.TestCase):
    def test_ui_language_resolution(self):
        self.assertEqual(resolve_language(["pt_BR"]), "pt-BR")
        self.assertEqual(resolve_language(["pt-PT"]), "pt-BR")
        self.assertEqual(resolve_language(["fr-FR", "pt-BR"]), "pt-BR")
        self.assertEqual(resolve_language(["en-GB", "pt-BR"]), "en")
        self.assertEqual(resolve_language(["ja-JP"]), "en")

    def test_all_translations_have_same_keys_and_placeholders(self):
        import string
        en, pt = Translator("en").strings, Translator("pt-BR").strings
        self.assertEqual(set(en), set(pt))
        for key in en:
            fields = lambda value: {name for _, name, _, _ in string.Formatter().parse(value) if name}
            self.assertEqual(fields(en[key]), fields(pt[key]), key)

    def test_settings_upgrade_preserves_user_values(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "settings.json"
            path.write_text('{"model":"existing-model","custom":"keep-me","language":"en"}', encoding="utf-8")
            settings = Settings(temp)
            settings.save()
            loaded = Settings(temp)
            self.assertEqual(loaded.values["model"], "existing-model")
            self.assertEqual(loaded.values["custom"], "keep-me")
            self.assertEqual(loaded.values["schema_version"], 1)

    def test_native_target_rejects_cross_platform(self):
        for target, system in [(".app", "Windows"), (".exe", "Darwin"), (".msi", "Darwin")]:
            with self.assertRaises(BuildError):
                native_target(target, system)
        native_target(".app", "Darwin")
        native_target(".exe", "Windows")
        native_target(".msi", "Windows")

    def test_python_child_exit_status(self):
        self.assertTrue(command([sys.executable, "-c", "print('hello')"]).ok)
        failed = command([sys.executable, "-c", "raise RuntimeError('expected')"])
        self.assertFalse(failed.ok)
        self.assertIn("expected", failed.output)

    def test_compiler_failure_does_not_execute_old_binary(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "main.c"
            source.write_text("not valid C", encoding="utf-8")
            with patch("appcore.builds.shutil.which", return_value="compiler"), patch("appcore.builds.command", return_value=Result(False, "compile error")) as run:
                result = build_and_run(source)
            self.assertFalse(result.ok)
            self.assertEqual(run.call_count, 1)

    def test_timeout_is_failure(self):
        result = command([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.1)
        self.assertFalse(result.ok)

    def test_real_c_program_when_compiler_available(self):
        if not (shutil.which("gcc") or shutil.which("clang")):
            self.skipTest("No C compiler")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "with spaces.c"
            path.write_text('#include <stdio.h>\nint main(void){puts("CHIMPI_C_OK");return 0;}\n', encoding="utf-8")
            result = build_and_run(path)
            self.assertTrue(result.ok, result.output)
            self.assertIn("CHIMPI_C_OK", result.output)

    def test_msi_covers_nested_staging_and_rejects_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            stage = Path(temp) / "stage & spaces"
            (stage / "lib" / "a").mkdir(parents=True)
            (stage / "ChimpiCode.exe").write_bytes(b"MZ-fixture")
            (stage / "lib" / "a" / "runtime.dll").write_bytes(b"runtime-fixture")
            (stage / "locales").mkdir()
            (stage / "locales" / "pt-BR.json").write_text("{}", encoding="utf-8")
            output = Path(temp) / "package.wxs"
            self.assertEqual(write_wxs(stage, output, version="1.1.0"), 3)
            xml = ET.parse(output)
            files = xml.findall(".//{" + WIX + "}File")
            self.assertEqual(len(files), 3)
            self.assertTrue(all(Path(file.attrib["Source"]).is_file() for file in files))
            first = output.read_bytes()
            write_wxs(stage, output, version="1.1.0")
            self.assertEqual(first, output.read_bytes())
            (stage / "LICENSE").write_text("MIT License\nCopyright © 2026 {ChimpiCode}", encoding="utf-8")
            write_wxs(stage, output, version="1.1.0")
            xml = ET.parse(output)
            self.assertIsNotNone(xml.find(".//{" + WIX + "}WixVariable"))
            rtf = output.with_suffix(".rtf").read_text(encoding="ascii")
            self.assertIn("MIT License", rtf)
            self.assertIn("\\u169?", rtf)
            self.assertIn("\\{ChimpiCode\\}", rtf)
            (stage / "from.cmd").write_text("@echo off\n", encoding="utf-8")
            write_wxs(stage, output, version="1.1.0")
            environment = ET.parse(output).find(".//{" + WIX + "}Environment")
            self.assertEqual(environment.attrib["Name"], "PATH")
            self.assertEqual(environment.attrib["Part"], "last")
            self.assertEqual(environment.attrib["Permanent"], "no")
            (stage / "lib" / "exposed.py").write_text("pass", encoding="utf-8")
            with self.assertRaises(ValueError):
                write_wxs(stage, output)


if __name__ == "__main__":
    unittest.main()
