# Changelog

All notable Titanium APK Builder changes are documented here.

## [10.0.0-dev.2] - 2026-09-15

### Added
- Simple / Advanced interface modes.
- First-run setup wizard when the build engine is incomplete.
- Project Analyzer with preflight checks before build.
- Missing local asset detection for HTML projects.
- Plain-HTTP and `file://` compatibility warnings.
- PWA manifest and service-worker detection.
- Repair Build Engine action that only touches Titanium-managed files.
- Structured timestamped log output with copy and clear actions.

### Reliability
- Managed toolchain downloads now retry automatically with exponential backoff.
- Interrupted JDK / Gradle / Android command-line tool downloads can resume from `.part` files when the server supports HTTP Range requests.
- Build-engine readiness checks now verify concrete SDK files such as `android.jar`, `aapt2.exe` and `adb.exe` instead of only checking directories.
- CI now runs automatically for all `v10-*` feature branches and validates the analyzer module.

### Safety
- Repair Engine never deletes system Java, Android Studio, system Android SDKs or the Portable runtime.
- Project Analyzer blocks builds with missing or unsafe local asset paths before Gradle starts.

## [10.0.0-dev.1] - 2026-09-15

### Added
- New native Android/Gradle v10 foundation.
- HTML folder, ZIP and URL source modes.
- Managed per-user JDK, Gradle and Android SDK provisioning flow.
- Android 16 / API 36 baseline.
- APK and AAB output.
- Debug and Release build variants.
- Environment-variable based release signing secrets.
- Build-engine diagnostics.
- Dedicated v10 roadmap.

### Security
- v10 no longer kills all `java.exe` processes before a build.
- Keystore passwords are not persisted in the v10 configuration file.
- ZIP import rejects path traversal entries.
- Build commands use argument lists instead of shell command strings.

### Changed
- v10 no longer requires a pre-existing Android Studio project as its template.
- v10 no longer depends on Cordova, Node.js or CustomTkinter.

## [9.0.0] - 2026-09-12
- First automated Windows EXE GitHub Release workflow for the legacy v9 codebase.
