import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from titanium.analyzer import analyze_source
from titanium.builder import AndroidBuilder
from titanium.builder_base import AndroidBuilder as BaseAndroidBuilder
from titanium.core import ConfigStore
from titanium.validator import ArtifactValidator, ValidationReport


class DummyPaths:
    def __init__(self, root):
        self.root = Path(root)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()


class DummyToolchain:
    def ready(self):
        return True


class DummyValidationToolchain:
    def apksigner_exe(self):
        return Path("apksigner.bat")

    def bundletool_jar(self):
        return Path("bundletool.jar")

    def java_exe(self):
        return Path("java.exe")

    def jarsigner_exe(self):
        return Path("jarsigner.exe")

    def env(self):
        return {}


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

    def test_generated_webview_has_modern_compatibility_bridge(self):
        with tempfile.TemporaryDirectory() as td:
            web = Path(td) / "web"
            web.mkdir()
            (web / "index.html").write_text("<input type='file'>", encoding="utf-8")
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td)
            c.update(source=str(web), camera=True, microphone=True, location=True)
            project = b.generate(c)
            java = (project / "app/src/main/java/com/example/testapp/MainActivity.java").read_text(encoding="utf-8")
            manifest = (project / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")

            self.assertIn("onPermissionRequest", java)
            self.assertIn("requestPermissions", java)
            self.assertIn("onGeolocationPermissionsShowPrompt", java)
            self.assertIn("onShowFileChooser", java)
            self.assertIn("setDownloadListener", java)
            self.assertIn("shouldOverrideUrlLoading", java)
            self.assertIn("onShowCustomView", java)
            self.assertIn("onHideCustomView", java)
            self.assertIn("webView.destroy()", java)
            self.assertIn("CAMERA_ENABLED = true", java)
            self.assertIn("MICROPHONE_ENABLED = true", java)
            self.assertIn("LOCATION_ENABLED = true", java)

            self.assertIn("android.permission.CAMERA", manifest)
            self.assertIn("android.permission.RECORD_AUDIO", manifest)
            self.assertIn("android.permission.ACCESS_FINE_LOCATION", manifest)
            self.assertIn("android.permission.ACCESS_COARSE_LOCATION", manifest)

    def test_url_wrapper_keeps_cleartext_policy_explicit(self):
        with tempfile.TemporaryDirectory() as td:
            b = AndroidBuilder(DummyPaths(td), DummyToolchain(), lambda *_: None)
            c = self.config(td)
            c.update(source_type="URL", source="http://example.com/app")
            project = b.generate(c)
            manifest = (project / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
            java = (project / "app/src/main/java/com/example/testapp/MainActivity.java").read_text(encoding="utf-8")
            self.assertIn('android:usesCleartextTraffic="true"', manifest)
            self.assertIn('webView.loadUrl("http://example.com/app")', java)

    def test_zip_path_traversal_is_rejected(self):
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

    def test_apk_validator_requires_valid_signature_when_expected(self):
        with tempfile.TemporaryDirectory() as td:
            artifact = Path(td) / "app.apk"
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("AndroidManifest.xml", "manifest")
            validator = ArtifactValidator(DummyValidationToolchain(), lambda *_: None)
            with patch.object(ArtifactValidator, "_run", return_value=(0, "Verifies\nSigner #1")) as run:
                report = validator.validate(artifact, expect_signed=True)
            self.assertTrue(report.signed)
            self.assertIn("ZIP integrity", report.checks)
            self.assertIn("APK signature", report.checks)
            self.assertIn("apksigner.bat", str(run.call_args.args[0][0]))

    def test_aab_validator_checks_bundle_structure_and_signature(self):
        with tempfile.TemporaryDirectory() as td:
            artifact = Path(td) / "app.aab"
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("base/manifest/AndroidManifest.xml", "manifest")
            validator = ArtifactValidator(DummyValidationToolchain(), lambda *_: None)
            with patch.object(
                ArtifactValidator,
                "_run",
                side_effect=[(0, "Bundle validation successful"), (0, "jar verified.")],
            ) as run:
                report = validator.validate(artifact, expect_signed=True)
            self.assertTrue(report.signed)
            self.assertIn("bundletool structure", report.checks)
            self.assertIn("AAB signature integrity", report.checks)
            self.assertEqual(run.call_count, 2)
            self.assertIn("validate", run.call_args_list[0].args[0])

    def test_aab_validator_can_report_intentionally_unsigned_output(self):
        with tempfile.TemporaryDirectory() as td:
            artifact = Path(td) / "unsigned.aab"
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("base/manifest/AndroidManifest.xml", "manifest")
            validator = ArtifactValidator(DummyValidationToolchain(), lambda *_: None)
            with patch.object(
                ArtifactValidator,
                "_run",
                side_effect=[(0, "Bundle validation successful"), (1, "jar is unsigned")],
            ):
                report = validator.validate(artifact, expect_signed=False)
            self.assertFalse(report.signed)
            self.assertIn("AAB unsigned state accepted", report.checks)

    def test_validator_rejects_corrupt_android_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            artifact = Path(td) / "broken.apk"
            artifact.write_bytes(b"not-a-zip")
            validator = ArtifactValidator(DummyValidationToolchain(), lambda *_: None)
            with self.assertRaises(RuntimeError):
                validator.validate(artifact)

    def test_builder_wrapper_runs_post_build_validation(self):
        with tempfile.TemporaryDirectory() as td:
            artifact = Path(td) / "app.apk"
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("AndroidManifest.xml", "manifest")
            builder = AndroidBuilder(DummyPaths(td), DummyValidationToolchain(), lambda *_: None)
            expected = ValidationReport(artifact, "APK", True, ("ZIP integrity", "APK signature"))
            with patch.object(BaseAndroidBuilder, "build", return_value=artifact), patch.object(
                ArtifactValidator, "validate", return_value=expected
            ) as validate:
                result = builder.build({"build_mode": "Release", "sign_release": True})
            self.assertEqual(result, artifact)
            validate.assert_called_once_with(artifact, expect_signed=True)

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
