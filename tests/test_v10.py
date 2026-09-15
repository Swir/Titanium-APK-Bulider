import tempfile
import unittest
from pathlib import Path
from titanium.builder import AndroidBuilder

class DummyPaths:
    def __init__(self, root):
        self.root = Path(root)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()

class DummyToolchain:
    def ready(self): return True

class V10ProjectTests(unittest.TestCase):
    def test_rejects_bad_package(self):
        with tempfile.TemporaryDirectory() as td:
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td); c["package"] = "Bad Package"
            with self.assertRaises(ValueError): b.validate(c)

    def test_generates_native_webview_project(self):
        with tempfile.TemporaryDirectory() as td:
            web = Path(td) / "web"; web.mkdir(); (web / "index.html").write_text("<h1>Titanium</h1>", encoding="utf-8")
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td); c["source"] = str(web); project = b.generate(c)
            self.assertTrue((project / "app/src/main/assets/www/index.html").exists())
            self.assertTrue((project / "app/build.gradle").exists())
            self.assertTrue((project / "app/src/main/AndroidManifest.xml").exists())
            self.assertIn("targetSdk 36", (project / "app/build.gradle").read_text(encoding="utf-8"))

    def test_zip_path_traversal_is_rejected(self):
        import zipfile
        with tempfile.TemporaryDirectory() as td:
            zpath = Path(td) / "bad.zip"
            with zipfile.ZipFile(zpath, "w") as z:
                z.writestr("../escape.txt", "no"); z.writestr("index.html", "ok")
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td); c["source_type"] = "ZIP"; c["source"] = str(zpath)
            with self.assertRaises(ValueError): b.generate(c)

    @staticmethod
    def config(td):
        return {"app_name":"TestApp","package":"com.example.testapp","version_name":"1.0.0","version_code":"1","min_sdk":"24","target_sdk":"36","source_type":"Folder","source":"","output_dir":td,"export_format":"APK","build_mode":"Debug","orientation":"unspecified","camera":False,"microphone":False,"location":False,"sign_release":False,"keystore":"","store_password":"","key_alias":"","key_password":""}

if __name__ == "__main__": unittest.main()
