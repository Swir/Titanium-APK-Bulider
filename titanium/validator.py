from __future__ import annotations

import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidationReport:
    artifact: Path
    kind: str
    signed: bool
    checks: tuple[str, ...]

    def summary(self) -> str:
        state = "signed" if self.signed else "unsigned"
        return f"{self.kind} validation passed ({state}; {len(self.checks)} checks)"


class ArtifactValidator:
    """Post-build validation for APK and Android App Bundle artifacts."""

    def __init__(self, toolchain, emit):
        self.t = toolchain
        self.emit = emit

    @staticmethod
    def _run(args, env=None):
        result = subprocess.run(
            [str(x) for x in args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        return result.returncode, result.stdout or ""

    @staticmethod
    def _check_zip(path: Path):
        try:
            with zipfile.ZipFile(path) as archive:
                broken = archive.testzip()
        except (OSError, zipfile.BadZipFile) as exc:
            raise RuntimeError(f"Artifact is not a valid ZIP-based Android package: {exc}") from exc
        if broken:
            raise RuntimeError(f"Artifact ZIP integrity failed at entry: {broken}")

    def validate(self, artifact, expect_signed=True):
        path = Path(artifact)
        if not path.is_file():
            raise RuntimeError(f"Build artifact does not exist: {path}")

        suffix = path.suffix.lower()
        if suffix not in {".apk", ".aab"}:
            raise ValueError("Post-build validation supports only APK and AAB artifacts")

        checks: list[str] = []
        self.emit("log", f"Validating {path.name}...")
        self._check_zip(path)
        checks.append("ZIP integrity")

        if suffix == ".apk":
            signed = self._validate_apk(path, expect_signed, checks)
            kind = "APK"
        else:
            signed = self._validate_aab(path, expect_signed, checks)
            kind = "AAB"

        report = ValidationReport(path, kind, signed, tuple(checks))
        self.emit("log", report.summary())
        return report

    def _validate_apk(self, path: Path, expect_signed: bool, checks: list[str]):
        apksigner = self.t.apksigner_exe()
        if not apksigner:
            raise RuntimeError("Android apksigner is missing. Repair the Build Engine and try again.")

        code, output = self._run(
            [apksigner, "verify", "--verbose", "--print-certs", path],
            env=self.t.env(),
        )
        self.emit("detail", output[-6000:])
        if code == 0:
            checks.append("APK signature")
            return True
        if expect_signed:
            raise RuntimeError("APK signature verification failed. See the build log for apksigner details.")

        self.emit("log", "WARNING: APK is unsigned; signature verification was not required for this build.")
        checks.append("APK unsigned state accepted")
        return False

    def _validate_aab(self, path: Path, expect_signed: bool, checks: list[str]):
        java = self.t.java_exe()
        bundletool = self.t.bundletool_jar()
        if not java:
            raise RuntimeError("Java runtime is missing. Repair the Build Engine and try again.")
        if not bundletool:
            raise RuntimeError("bundletool is missing. Repair the Build Engine and try again.")

        code, output = self._run(
            [java, "-jar", bundletool, "validate", f"--bundle={path}"],
            env=self.t.env(),
        )
        self.emit("detail", output[-6000:])
        if code:
            raise RuntimeError("AAB validation failed. See the build log for bundletool details.")
        checks.append("bundletool structure")

        jarsigner = self.t.jarsigner_exe()
        if not jarsigner:
            raise RuntimeError("JDK jarsigner is missing. Repair the Build Engine and try again.")
        code, output = self._run([jarsigner, "-verify", "-verbose", "-certs", path], env=self.t.env())
        self.emit("detail", output[-6000:])
        verified = code == 0 and "jar verified" in output.lower() and "jar is unsigned" not in output.lower()
        if verified:
            checks.append("AAB signature integrity")
            return True
        if expect_signed:
            raise RuntimeError("AAB signature verification failed. See the build log for jarsigner details.")

        self.emit("log", "WARNING: AAB is unsigned; signature verification was not required for this build.")
        checks.append("AAB unsigned state accepted")
        return False
