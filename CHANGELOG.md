# Changelog

All notable Titanium APK Builder changes are documented here.

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
