# Titanium APK Builder — Roadmap to v10.0

Titanium v10 is a clean transition from the experimental v9/Ghost codebase to a reproducible, secure, zero-manual-setup Android builder for Windows.

## Product goal

**Input:** HTML folder, ZIP web project, or URL  
**Output:** installable APK or Play-ready AAB  
**User experience:** download Titanium, run the EXE, click **Prepare Build Engine** once, then build apps without installing Android Studio, Python, JDK, Gradle, Node.js, or Cordova manually.

> Android SDK components are provisioned into Titanium's private user-data directory after the user accepts Google's Android SDK license. They are not redistributed inside the Portable archive.

## Current v10 status

The v10 foundation is merged into `main`. End-to-end GitHub Actions tests generate a native Android project targeting API 36 and successfully compile a real debug APK. The Windows job also builds a standalone PyInstaller executable.

A public development prerelease, **v10.0.0-dev.1**, is now available with:

- standalone Windows EXE;
- Portable Windows ZIP containing the EXE, Temurin JDK 21 and Gradle 9.6.0;
- SHA-256 files for both deliverables.

The Portable ZIP is intended to require no JDK, Gradle, Python, Node.js, Cordova or Android Studio installation. Android SDK components are prepared inside Titanium after explicit SDK-license consent. Stable `v10.0.0` remains gated by the criteria below.

## v10.0 milestones

### M0 — v10 foundation ✅
- [x] Introduce `Titanium V10.py` without Cordova dependency.
- [x] Native Gradle/Android project generation.
- [x] HTML folder → APK/AAB.
- [x] ZIP → APK/AAB with path-traversal protection.
- [x] URL → APK/AAB.
- [x] Target Android 16 / API 36 by default.
- [x] Remove the dangerous global `taskkill java.exe` behavior from the v10 engine.
- [x] Stop persisting keystore passwords.
- [x] Pass signing secrets to Gradle through process environment variables.
- [x] Move build workspace/toolchain under the application user-data directory.
- [x] Thread-safe UI logging through an event queue.
- [x] Eliminate the requirement for a pre-existing Android Studio project.

### M1 — Managed build engine 🚧
- [x] Detect local, portable or Titanium-managed JDK.
- [x] Detect local, portable or Titanium-managed Android SDK.
- [x] Detect local, portable or Titanium-managed Gradle.
- [x] One-click managed JDK/Gradle/Android SDK provisioning.
- [x] User-visible Android SDK license consent before provisioning.
- [x] SHA-256 verification for managed JDK, Gradle and Android command-line tools downloads.
- [ ] Resumable downloads and retry/backoff.
- [ ] Toolchain repair button.
- [ ] Toolchain update channel (Stable / Preview).
- [ ] Offline cache import/export.

### M2 — Web app compatibility
- [ ] Project scanner with HTML/CSS/JS validation before build.
- [ ] Configurable network security policy.
- [ ] Runtime permission bridge for camera, microphone and geolocation.
- [ ] File upload/download support inside WebView.
- [ ] Deep links / custom schemes.
- [x] Basic WebView back navigation.
- [ ] Full-screen / immersive mode.
- [ ] Status/navigation bar customization.
- [ ] Splash screen generator.
- [ ] Adaptive launcher icon generator.
- [ ] PWA manifest import for app name, theme and icons.

### M3 — Release and Play Store pipeline
- [x] APK and AAB build modes.
- [x] Debug / Release variants.
- [x] JKS release signing without saving passwords.
- [ ] Keystore creation wizard.
- [ ] `apksigner` verification after APK build.
- [ ] `bundletool` validation for AAB.
- [ ] Automatic version-code management.
- [ ] Google Play readiness report.
- [ ] API-level compatibility warnings.
- [ ] ProGuard/R8 controls.

### M4 — Professional desktop application
- [x] Split v10 UI, build engine and Android generator into separate modules.
- [ ] New responsive Windows UI polish pass.
- [ ] First-run setup wizard.
- [ ] Build profiles and recent projects.
- [ ] Structured log viewer with copy/export/filter.
- [ ] Human-readable diagnostics with suggested fixes.
- [ ] Crash reports stored locally (opt-in sharing only).
- [ ] Multi-language UI with system-language detection and English fallback.
- [ ] Accessibility and high-DPI testing.

### M5 — Automated quality gate
- [x] Unit tests for configuration and project generation.
- [x] ZIP security tests.
- [x] Signing-secret persistence tests.
- [x] Generated Gradle project smoke test on GitHub Actions.
- [x] APK build test against API 36.
- [ ] Release-signing test with ephemeral CI keystore.
- [ ] Windows EXE launch smoke test.
- [ ] VirusTotal-friendly deterministic packaging where possible.
- [ ] SBOM and dependency/license manifest.

### M6 — v10 release packaging
- [x] Automated standalone Windows EXE packaging workflow.
- [x] Automated Portable package containing the EXE + JDK + Gradle.
- [x] Portable runtime discovery beside the EXE; no installer or admin rights required.
- [x] SHA-256 files for release assets and verification of bundled JDK/Gradle downloads.
- [x] Validate that packaged Portable runtime actually contains `java.exe` and `gradle.bat` on future releases.
- [x] Publish development prerelease `v10.0.0-dev.1` with EXE + Portable ZIP + checksums.
- [x] Add release notes, v9→v10 migration notes and troubleshooting guide.
- [ ] Publish `Titanium-APK-Builder-v10.0.0-Windows-x64.exe` after all stable gates pass.
- [ ] Publish `Titanium-APK-Builder-v10.0.0-Portable-Windows-x64.zip` after all stable gates pass.
- [ ] Sign the Windows executable when a code-signing certificate becomes available.

## v10.0 release criteria

v10.0 is considered stable only when all of the following are true:

1. A clean Windows machine can launch Titanium without Python or Android Studio.
2. The user can prepare the build engine from inside Titanium without administrator rights.
3. A sample local HTML5 project builds to a working debug APK.
4. The same project builds to a signed release APK and AAB.
5. Target SDK is API 36 or newer and the build passes post-build validation.
6. No signing password is written to configuration, source files, logs or generated Gradle files.
7. Titanium never terminates unrelated Java/Gradle processes.
8. CI validates Python syntax, generated project structure, a real API 36 APK build and the Windows executable build.
9. README, CHANGELOG, migration and troubleshooting documentation match the actual application.

## After v10.0

Planned post-v10 work includes plug-in APIs, project templates, automatic PWA conversion, advanced WebView bridges, optional cloud build, macOS/Linux desktop builds and direct Play Console workflow support where APIs and account permissions allow it.
