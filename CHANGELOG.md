# Changelog

All notable Titanium APK Builder changes are documented here.

## [10.0.0] - 2026-09-15

### Stable release
- Promoted the verified v10 architecture to the stable `10.0.0` line.
- Native HTML folder, ZIP and URL → Android APK/AAB generation targeting Android API 36.
- Standalone Windows EXE plus Portable package with Eclipse Temurin JDK 21, Gradle 9.6.0 and SHA-256-verified Google bundletool 1.18.3.
- Android SDK components remain license-gated and are provisioned into Titanium's private user-data directory rather than redistributed in the Portable archive.
- Simple / Advanced UI, first-run Build Engine setup, Project Analyzer and safe Repair Build Engine.
- WebView runtime camera/microphone/location permissions, file upload, downloads, external/deep-link schemes and HTML5 fullscreen.
- Debug and Release APK/AAB builds with JKS signing secrets kept out of saved configuration and generated Gradle source.
- In-app post-build validation with APK `apksigner`, AAB bundletool validation and AAB signing-integrity checks.

### Stable quality gates
- Real API 36 debug APK CI build.
- Signed Release APK and AAB CI build with a fresh ephemeral keystore.
- APK signing, AAB signing and bundle processing validation.
- Standalone Windows EXE smoke launch with Python runtime paths removed.
- Exact Portable release-package assembly and smoke launch.
- Isolated managed Build Engine provisioning with no detected system Java/Android SDK/Gradle.
- Deliberate managed-tool corruption followed by successful Repair Build Engine recovery.
- Release packaging and publication separated so PR package tests use read-only repository permissions.
- Stable downloadable assets use versioned names and include SHA-256 checksum files.

## [10.0.0-dev.6] - 2026-09-15

### Release candidate hardening
- Refactored the v10 release workflow into separate package and publish jobs so pull requests can build the exact release package without receiving release-write permissions.
- Pull requests that touch release packaging run the full Windows release-package path without publishing a GitHub Release.
- Standalone release EXE is smoke-launched with Python removed from `PATH`, `PYTHONHOME` and `PYTHONPATH` before packaging.
- Portable Runtime includes SHA-256-verified Google bundletool 1.18.3 next to the EXE, Temurin JDK 21 and Gradle 9.6.0.
- Portable package includes the bundletool Apache 2.0 license.
- Portable packaging validates `java.exe`, `jarsigner.exe`, `gradle.bat`, bundletool execution and Gradle execution before creating the ZIP.
- The packaged Portable EXE is smoke-launched from inside the final Portable directory with Python runtime paths removed.
- Android SDK components remain intentionally excluded from the Portable archive and are provisioned after Android SDK license acceptance.

### Final stable quality gate
- Added an isolated Windows Prepare/Repair Build Engine integration test with system Java, Android SDK and Gradle discovery disabled.
- The isolated test provisions Temurin JDK, Gradle, Android command-line tools, API 36, Build Tools 36.0.0, Platform Tools and bundletool entirely under Titanium's private user-data directory.
- The gate executes managed Java, Gradle, apksigner and bundletool binaries after provisioning.
- The test deliberately corrupts managed bundletool and removes API 36 `android.jar`, then proves Repair Build Engine restores both and returns to a ready state.
- Migration and troubleshooting documentation was aligned with the verified Portable runtime and validator behavior.

## [10.0.0-dev.5] - 2026-09-15

### Added
- In-app post-build validation for generated APK and AAB artifacts before Titanium reports a successful build.
- APK verification through Android Build Tools `apksigner`.
- AAB structural validation through Google `bundletool 1.18.3`.
- AAB signature-integrity verification through JDK `jarsigner` plus direct signature-entry checks in `META-INF`.
- Managed `bundletool` provisioning with a pinned SHA-256 digest.
- Build Engine diagnostics for `apksigner`, `jarsigner` and `bundletool` readiness.
- Validator unit tests for signed APK, signed AAB, intentionally unsigned AAB, corrupt artifacts and builder/validator integration.

### Architecture
- Preserved the proven WebView/project generator as `builder_base.py`.
- `builder.py` became a thin integration layer that runs artifact validation after the base build completes.

### Reliability and Security
- AAB signature detection no longer depends on English `jarsigner` output; Titanium checks real signature metadata entries and tool exit status.
- Managed Build Engine repair removes a corrupted managed bundletool copy and reacquires a verified one.
- Post-build validation fails closed for expected signed Release artifacts.

## [10.0.0-dev.4] - 2026-09-15

### Added
- Dedicated CI release gate with a fresh ephemeral signing keystore for every run.
- End-to-end signed Release APK and signed Release AAB builds against Android API 36.
- APK signature verification with Android Build Tools `apksigner`.
- AAB signing-integrity verification with `jarsigner`.
- AAB processing with SHA-256-verified Google `bundletool` 1.18.3.

### Security
- CI signing credentials are generated randomly at runtime and masked in Actions logs.
- No reusable CI signing password is stored in the repository.

## [10.0.0-dev.3] - 2026-09-15

### Added
- WebView runtime permission bridge for camera and microphone.
- WebView geolocation bridge.
- Native file picker for HTML upload controls.
- HTTP/HTTPS downloads through Android DownloadManager.
- External/custom scheme routing.
- HTML5 custom-view fullscreen support.
- Generated-code tests for WebView compatibility hooks.

### Reliability and Security
- Explicit WebView teardown on Activity destruction.
- Back navigation exits fullscreen before WebView history.
- Camera/microphone/location capabilities require enabled project options and Android permission approval.
- `javascript:` navigation is not forwarded to external intents.

## [10.0.0-dev.2] - 2026-09-15

### Added
- Simple / Advanced interface modes.
- First-run setup wizard.
- Project Analyzer and preflight checks.
- Repair Build Engine.
- Structured timestamped logs.
- Retrying/resumable managed toolchain downloads.

### Safety
- Repair Engine never deletes system Java, Android Studio, system Android SDKs or the Portable runtime.
- Project Analyzer blocks missing or unsafe local assets before Android compilation.

## [10.0.0-dev.1] - 2026-09-15

### Added
- New native Android/Gradle v10 foundation.
- HTML folder, ZIP and URL source modes.
- Managed per-user JDK, Gradle and Android SDK provisioning.
- Android API 36 baseline.
- APK/AAB and Debug/Release build modes.
- Environment-variable based release signing secrets.

### Security
- No global `java.exe` termination.
- Keystore passwords are not persisted.
- ZIP import rejects path traversal.
- Build commands use argument lists rather than shell command strings.

## [9.0.0] - 2026-09-12
- First automated Windows EXE GitHub Release workflow for the legacy v9 codebase.
