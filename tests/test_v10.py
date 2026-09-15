import json
import tempfile
import unittest
from pathlib import Path

from titanium.analyzer import analyze_source
from titanium.builder import AndroidBuilder
from titanium.core import ConfigStore


class DummyPaths:
    def __init__(self, root):
        self.root = Path(root)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()


class DummyToolchain:
    def ready(self):
        return True


class V10ProjectTests(unittest.TestCase):
    def test_rejects_bad_package(self):
        with tempfile.TemporaryDirectory() as td:
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td)
            c["package"] = "Bad Package"
            with self.assertRaises(ValueError):
                b.validate(c)

    def test_generates_native_webview_project(self):
        with tempfile.TemporaryDirectory() as td:
            web = Path(td) / "web"
            web.mkdir()
            (web / "index.html").write_text("<h1>Titanium</h1>", encoding="utf-8")
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td)
            c["source"] = str(web)
            project = b.generate(c)
            self.assertTrue((project / "app/src/main/assets/www/index.html").exists())
            self.assertTrue((project / "app/build.gradle").exists())
            self.assertTrue((project / "app/src/main/AndroidManifest.xml").exists())
            gradle = (project / "app/build.gradle").read_text(encoding="utf-8")
            self.assertIn("targetSdk 36", gradle)
            self.assertIn("buildTypes {", gradle)
            self.assertIn("debug {", gradle)
            self.assertIn("release {", gradle)

    def test_zip_path_traversal_is_rejected(self):
        import zipfile

        with tempfile.TemporaryDirectory() as td:
            zpath = Path(td) / "bad.zip"
            with zipfile.ZipFile(zpath, "w") as z:
                z.writestr("../escape.txt", "no")
                z.writestr("index.html", "ok")
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td)
            c["source_type"] = "ZIP"
            c["source"] = str(zpath)
            with self.assertRaises(ValueError):
                b.generate(c)

    def test_config_never_persists_signing_passwords(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "config.json"
            ConfigStore(path).save({
                "app_name": "Safe",
                "store_password": "store-secret",
                "key_password": "key-secret",
                "key_alias": "release",
            })
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("store_password", data)
            self.assertNotIn("key_password", data)
            self.assertEqual(data["key_alias"], "release")

    def test_generated_signing_config_uses_environment_only(self):
        with tempfile.TemporaryDirectory() as td:
            web = Path(td) / "web"
            web.mkdir()
            (web / "index.html").write_text("ok", encoding="utf-8")
            key = Path(td) / "release.jks"
            key.write_bytes(b"placeholder")
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td)
            c.update(
                source=str(web),
                build_mode="Release",
                sign_release=True,
                keystore=str(key),
                store_password="TOPSECRET",
                key_alias="release",
                key_password="KEYSECRET",
            )
            project = b.generate(c)
            gradle = (project / "app/build.gradle").read_text(encoding="utf-8")
            self.assertIn("TITANIUM_STORE_PASSWORD", gradle)
            self.assertIn("TITANIUM_KEY_PASSWORD", gradle)
            self.assertNotIn("TOPSECRET", gradle)
            self.assertNotIn("KEYSECRET", gradle)

    def test_analyzer_accepts_valid_local_project(self):
        with tempfile.TemporaryDirectory() as td:
            web = Path(td) / "web"
            web.mkdir()
            (web / "assets").mkdir()
            (web / "assets/app.js").write_text("console.log('ok')", encoding="utf-8")
            (web / "index.html").write_text('<script src="assets/app.js"></script>', encoding="utf-8")
            findings = analyze_source("Folder", str(web))
            self.assertFalse(any(x.severity == "ERROR" for x in findings))
            self.assertTrue(any(x.severity == "READY" for x in findings))

    def test_analyzer_blocks_missing_local_asset(self):
        with tempfile.TemporaryDirectory() as td:
            web = Path(td) / "web"
            web.mkdir()
            (web / "index.html").write_text('<script src="assets/missing.js"></script>', encoding="utf-8")
            findings = analyze_source("Folder", str(web))
            self.assertTrue(any(x.severity == "ERROR" and "Missing" in x.message for x in findings))

    def test_analyzer_warns_on_plain_http_url(self):
        findings = analyze_source("URL", "http://example.com/app")
        self.assertTrue(any(x.severity == "WARNING" for x in findings))
        self.assertFalse(any(x.severity == "ERROR" for x in findings))

    @staticmethod
    def config(td):
        return {
            "app_name": "TestApp",
            "package": "com.example.testapp",
            "version_name": "1.0.0",
            "version_code": "1",
            "min_sdk": "24",
            "target_sdk": "36",
            "source_type": "Folder",
            "source": "",
            "output_dir": td,
            "export_format": "APK",
            "build_mode": "Debug",
            "orientation": "unspecified",
            "camera": False,
            "microphone": False,
            "location": False,
            "sign_release": False,
            "keystore": "",
            "store_password": "",
            "key_alias": "",
            "key_password": "",
        }


if __name__ == "__main__":
    unittest.main()
