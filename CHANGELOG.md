# Changelog

All notable Titanium APK Builder changes are documented here.

## [10.0.0-dev.4] - 2026-09-15

### Added
- Dedicated CI release gate that generates a fresh ephemeral signing keystore for every run.
- End-to-end signed Release APK and signed Release AAB builds against Android API 36.
- APK signature verification with Android Build Tools `apksigner`.
- AAB signature-integrity verification with `jarsigner`.
- AAB structural/installability validation by generating a universal APK set with Google `bundletool` 1.18.3.
- SHA-256 verification of the downloaded `bundletool` artifact before use.

### Security
- CI signing credentials are generated randomly at runtime and masked in GitHub Actions logs.
- No CI signing password is stored in the repository.
- The ephemeral signing certificate and keystore exist only on the temporary GitHub Actions runner.

### Quality
- The release gate proves that the same generated Titanium project can produce both a signed Release APK and a signed AAB.
- The gate independently validates APK signing, AAB signing integrity and bundle processing instead of relying only on a successful Gradle exit code.

## [10.0.0-dev.3] - 2026-09-15

### Added
- WebView runtime permission bridge for camera and microphone using `WebChromeClient.onPermissionRequest` plus Android runtime permissions.
- WebView geolocation bridge using Android fine/coarse location runtime permissions.
- Native Android file picker support for HTML `<input type="file">` controls.
- HTTP/HTTPS download handling through Android `DownloadManager`, including WebView cookies and user-agent headers when available.
- External/custom scheme routing for links such as `tel:`, `mailto:`, `sms:`, `geo:`, `market:` and `intent:`.
- HTML5 custom-view fullscreen support with safe exit and back-button handling.
- Generated-code tests covering the new WebView compatibility hooks and permission declarations.

### Reliability
- Generated WebViews are explicitly detached and destroyed when the Activity closes to reduce retained WebView memory.
- Back navigation now exits fullscreen first, then traverses WebView history, then closes the Activity.
- Unsupported download schemes fail visibly instead of being silently handed to `DownloadManager`.

### Security
- Camera and microphone WebView resources are only granted when the feature is enabled in Titanium and the Android runtime permission is actually granted.
- Geolocation remains denied when the project option is disabled or the Android user rejects location permission.
- `javascript:` navigation attempts are not forwarded to external Android intent handlers.
- Normal HTTP/HTTPS/file navigation remains inside WebView; only non-web schemes are routed externally.

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
