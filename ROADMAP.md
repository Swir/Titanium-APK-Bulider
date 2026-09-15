# Titanium APK Builder — Roadmap to v10.0

Titanium v10 is a clean transition from the experimental v9/Ghost codebase to a reproducible, secure, zero-manual-setup Android builder for Windows.

## Product goal

**Input:** HTML folder, ZIP web project, or URL  
**Output:** installable APK or Play-ready AAB  
**User experience:** download Titanium, run the EXE, prepare the Android Build Engine when required, then build apps without manually installing Android Studio, Python, JDK, Gradle, Node.js or Cordova.

> Android SDK components are provisioned into Titanium's private user-data directory after the user accepts Google's Android SDK license. They are intentionally not redistributed inside the Portable archive.

## Current v10 status

The current development line is **v10.0.0-dev.6** and all defined **v10.0.0 stable release criteria have now passed automated verification**.

The regular CI gate builds a real API 36 debug APK, builds and verifies signed Release APK/AAB output, runs validator tests and smoke-launches the standalone Windows EXE. The release-package gate builds the exact Portable Windows package, validates its bundled JDK/Gradle/bundletool runtime and smoke-launches the packaged EXE. The isolated managed-engine gate starts without detectable system Java, Android SDK or Gradle, provisions Titanium's private toolchain from scratch, deliberately damages managed components and proves **Repair Build Engine** restores them to a ready state.

The next step is the final `v10.0.0` version/release-candidate PR followed by publication of the stable Windows EXE and Portable ZIP if that exact stable commit repeats the green gates.

## v10.0 milestones

### M0 — v10 foundation ✅
- [x] Native `Titanium V10.py` architecture without Cordova or Node.js.
- [x] Native Gradle/Android project generation.
- [x] HTML folder, ZIP and URL source modes.
- [x] APK and AAB output.
- [x] Android 16 / API 36 default target.
- [x] No global Java process termination.
- [x] Signing passwords are not persisted.
- [x] Signing secrets are passed to Gradle through process environment variables.
- [x] Workspace/toolchain stays under application user data.
- [x] No pre-existing Android Studio template project is required.

### M1 — Managed build engine ✅
- [x] Detect portable, Titanium-managed or compatible system JDK.
- [x] Detect portable, Titanium-managed or compatible Android SDK.
- [x] Detect portable, Titanium-managed or compatible Gradle.
- [x] One-click JDK/Gradle/Android SDK provisioning.
- [x] Android SDK license consent before provisioning.
- [x] SHA-256 verification of managed JDK, Gradle, Android command-line tools and bundletool.
- [x] Resumable downloads with retry/backoff.
- [x] Repair Build Engine only modifies Titanium-managed files.
- [x] Isolated Windows CI proves Prepare/Repair works without discovering system Java, Android SDK or Gradle.
- [x] Isolated CI deliberately corrupts managed bundletool/API 36 and proves Repair restores a ready toolchain.

Future/non-blocking: Stable/Preview toolchain update channels and offline cache import/export.

### M2 — Web app compatibility ✅ for v10.0 scope
- [x] Project preflight scanner.
- [x] Runtime camera/microphone permission bridge.
- [x] Runtime geolocation bridge.
- [x] HTML file upload picker.
- [x] HTTP/HTTPS downloads through Android DownloadManager.
- [x] External/deep-link scheme routing.
- [x] WebView back navigation.
- [x] HTML5 custom-view fullscreen support.
- [x] Explicit WebView teardown.

Future/non-blocking: deeper CSS/JS dependency scanning, custom network-security policies, app-wide immersive mode, system-bar theming, splash/icon generators and PWA metadata import.

### M3 — Release and Play Store pipeline ✅ for v10.0 scope
- [x] APK and AAB build modes.
- [x] Debug and Release variants.
- [x] JKS signing without saving passwords.
- [x] CI builds signed Release APK and AAB from the same generated project.
- [x] In-app APK verification with `apksigner`.
- [x] In-app AAB structural validation with SHA-256-pinned bundletool.
- [x] In-app AAB signature-integrity validation with `jarsigner` plus signature metadata checks.

Future/non-blocking: keystore wizard, automatic version-code management, Play readiness report, richer API compatibility warnings and configurable R8/ProGuard controls.

### M4 — Professional desktop application ✅ for v10.0 scope
- [x] Separate UI, build engine, Android generator, analyzer and validator modules.
- [x] Simple / Advanced modes.
- [x] First-run Build Engine setup flow.
- [x] Timestamped logs with copy/clear actions.
- [x] Human-readable project preflight diagnostics.

Future/non-blocking: further visual polish, build profiles/recent projects, log filtering/export, suggested automatic fixes, optional local crash reports, multilingual UI and broader accessibility/high-DPI testing.

### M5 — Automated quality gate ✅
- [x] Unit tests for configuration, generation, analyzer and validator behavior.
- [x] ZIP path-traversal/security tests.
- [x] Signing-secret persistence tests.
- [x] Generated WebView compatibility tests.
- [x] Real API 36 debug APK CI build.
- [x] Ephemeral-keystore signed Release APK/AAB CI build.
- [x] APK signature verification with `apksigner`.
- [x] AAB signature-integrity verification with `jarsigner`.
- [x] AAB processing with SHA-256-pinned bundletool.
- [x] Windows standalone EXE launch test without Python runtime paths.
- [x] Exact Portable release-package build and smoke launch.
- [x] Fully isolated managed Build Engine Prepare/Repair integration test.

Future/non-blocking: additional reproducibility/determinism work, SBOM generation and external malware-scanner reporting.

### M6 — v10 release packaging 🚧
- [x] Automated standalone Windows EXE packaging.
- [x] Automated Portable package containing EXE + JDK + Gradle + bundletool.
- [x] Portable runtime discovery beside the EXE.
- [x] SHA-256 files for release assets.
- [x] Validate packaged `java.exe`, `jarsigner.exe`, `gradle.bat`, bundletool and its license.
- [x] Smoke-launch the EXE from inside the generated Portable directory without Python runtime paths.
- [x] Pull requests build the exact package with read-only repository permissions.
- [x] Release publication is isolated in a separate write-enabled job.
- [x] Development prerelease proved the GitHub Release path.
- [ ] Publish `Titanium-APK-Builder-v10.0.0-Windows-x64.exe` / stable EXE asset.
- [ ] Publish `Titanium-APK-Builder-v10.0.0-Portable-Windows-x64.zip` after the stable-version PR repeats all gates.

Optional/non-blocking: Windows Authenticode signing when a suitable code-signing certificate is available.

## v10.0 stable release criteria

All defined technical/documentation criteria are now satisfied on the development candidate:

1. Standalone and Portable Titanium EXEs launch without Python runtime paths. ✅
2. An isolated user can prepare and repair the complete managed Build Engine without relying on system Java/Gradle/Android SDK locations. ✅
3. A sample local HTML5 project passes preflight and builds a real API 36 debug APK. ✅
4. The same generated project builds signed Release APK and AAB output and passes signing/bundle validation. ✅
5. Generated APK/AAB output passes Titanium's post-build validator. ✅
6. Signing passwords are not written to configuration, generated Gradle source or repository files. ✅
7. Titanium does not terminate/delete unrelated Java, Gradle, Android Studio or system Android SDK components. ✅
8. CI validates source/tests, WebView generation, real Android builds, release signing, standalone EXE launch, exact Portable packaging and isolated Prepare/Repair. ✅
9. README, CHANGELOG, migration, troubleshooting, security and third-party notices match the verified v10 behavior. ✅

**Stable publication rule:** bump the exact candidate to `10.0.0`, run the full PR gates again on that version, merge only if green, then publish the release from that exact commit.

## After v10.0

Planned post-v10 work includes the non-blocking enhancements listed above, plug-in APIs, project templates, deeper PWA conversion, advanced WebView bridges, optional cloud build, macOS/Linux desktop builds and direct Play Console workflow support where APIs/account permissions allow it.
