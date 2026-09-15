# Titanium APK Builder — Roadmap to v10.0

Titanium v10 is a clean transition from the experimental v9/Ghost codebase to a reproducible, secure, zero-manual-setup Android builder for Windows.

## Product goal

**Input:** HTML folder, ZIP web project, or URL  
**Output:** installable APK or Play-ready AAB  
**User experience:** download Titanium, run the EXE, click **Prepare Build Engine** once, then build apps without installing Android Studio, Python, JDK, Gradle, Node.js, or Cordova manually.

> Android SDK components are provisioned into Titanium's private user-data directory after the user accepts Google's Android SDK license. They are not redistributed inside the Portable archive.

## Current v10 status

The current development line is **v10.0.0-dev.6**. The regular CI gate passes a real API 36 debug APK, signed Release APK/AAB validation and standalone Windows EXE launch. The release-package PR gate now also builds the exact Portable Windows package, validates its bundled runtime, smoke-launches the EXE from inside the Portable directory and uploads the resulting release-candidate artifacts without publishing a GitHub Release.

The Portable package contains the standalone EXE, Eclipse Temurin JDK 21, Gradle 9.6.0 and SHA-256-verified Google bundletool 1.18.3 with its Apache 2.0 license. Android SDK components remain license-gated and are provisioned into Titanium's private user-data directory after explicit user acceptance.

Stable `v10.0.0` remains gated by the criteria below rather than by a calendar date.

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
- [x] Resumable downloads and retry/backoff.
- [x] Toolchain repair button that only modifies Titanium-managed files.
- [x] Detect/provision SHA-256-pinned `bundletool` for post-build validation.
- [ ] End-to-end isolated managed-engine Prepare/Repair CI gate without relying on system Java/Gradle/Android SDK.
- [ ] Toolchain update channel (Stable / Preview).
- [ ] Offline cache import/export.

### M2 — Web app compatibility 🚧
- [x] Project preflight scanner for `index.html`, local HTML asset references and unsafe paths.
- [ ] Advanced CSS `url()` / `@import` and JavaScript module dependency scanning.
- [ ] Configurable network security policy.
- [x] Runtime permission bridge for camera and microphone through WebChromeClient + Android runtime permissions.
- [x] Runtime geolocation bridge through WebChromeClient + Android fine/coarse location permissions.
- [x] HTML file upload support through the native Android file picker.
- [x] HTTP/HTTPS download support through Android DownloadManager.
- [x] Deep links / custom schemes including `tel:`, `mailto:`, `sms:`, `geo:`, `market:` and `intent:` routing.
- [x] Basic WebView back navigation.
- [x] HTML5 custom-view fullscreen support with safe exit/back handling.
- [x] Explicit WebView teardown on Activity destruction to reduce retained WebView memory.
- [ ] App-wide optional immersive mode.
- [ ] Status/navigation bar customization.
- [ ] Splash screen generator.
- [ ] Adaptive launcher icon generator.
- [ ] PWA manifest import for app name, theme and icons.

### M3 — Release and Play Store pipeline 🚧
- [x] APK and AAB build modes.
- [x] Debug / Release variants.
- [x] JKS release signing without saving passwords.
- [x] CI proves the same generated project builds to signed Release APK and AAB.
- [x] In-app `apksigner` verification after APK build.
- [x] In-app `bundletool` validation for AAB.
- [x] In-app AAB signature-integrity verification with `jarsigner` and signature metadata checks.
- [ ] Keystore creation wizard.
- [ ] Automatic version-code management.
- [ ] Google Play readiness report.
- [ ] API-level compatibility warnings.
- [ ] ProGuard/R8 controls.

### M4 — Professional desktop application 🚧
- [x] Split v10 UI, build engine and Android generator into separate modules.
- [x] Add Simple / Advanced interface modes.
- [x] Add first-run setup wizard when the build engine is incomplete.
- [x] Add timestamped logs with copy and clear actions.
- [x] Add human-readable project preflight diagnostics before build.
- [ ] New responsive Windows UI polish pass.
- [ ] Build profiles and recent projects.
- [ ] Structured log filtering/export.
- [ ] Suggested one-click fixes for common project-analysis findings.
- [ ] Crash reports stored locally (opt-in sharing only).
- [ ] Multi-language UI with system-language detection and English fallback.
- [ ] Accessibility and high-DPI testing.

### M5 — Automated quality gate 🚧
- [x] Unit tests for configuration and project generation.
- [x] ZIP security tests.
- [x] Signing-secret persistence tests.
- [x] Project Analyzer tests for valid projects, missing assets and HTTP warnings.
- [x] Generated WebView compatibility tests for runtime permissions, upload, download, external routing and fullscreen hooks.
- [x] Generated Gradle project smoke test on GitHub Actions.
- [x] Debug APK build test against API 36.
- [x] Release-signing test with a fresh ephemeral CI keystore.
- [x] Signed Release APK verification with Android Build Tools `apksigner`.
- [x] Signed AAB integrity verification with `jarsigner`.
- [x] AAB processing test with SHA-256-pinned Google `bundletool` 1.18.3 producing a universal APK set.
- [x] Unit tests for the in-app post-build validator and builder integration.
- [x] Windows standalone EXE launch smoke test with Python removed from runtime environment paths.
- [x] Exact release-package PR gate builds and smoke-tests the Portable directory before ZIP creation.
- [ ] VirusTotal-friendly deterministic packaging where possible.
- [ ] SBOM and dependency/license manifest.

### M6 — v10 release packaging 🚧
- [x] Automated standalone Windows EXE packaging workflow.
- [x] Automated Portable package containing the EXE + JDK + Gradle + bundletool.
- [x] Portable runtime discovery beside the EXE; no installer or admin rights required.
- [x] SHA-256 files for release assets and verification of bundled JDK/Gradle/bundletool downloads.
- [x] Validate packaged `java.exe`, `jarsigner.exe`, `gradle.bat`, bundletool and the bundletool license before ZIP creation.
- [x] Smoke-launch the EXE from inside the generated Portable directory with Python runtime paths removed.
- [x] Pull requests can build the exact release package with read-only repository permissions; publication is isolated in a separate write-enabled job.
- [x] Publish development prerelease `v10.0.0-dev.1` with EXE + Portable ZIP + checksums.
- [x] Add release notes, v9→v10 migration notes and troubleshooting guide.
- [ ] Publish the next fully hardened development/RC package from the new release workflow.
- [ ] Publish `Titanium-APK-Builder-v10.0.0-Windows-x64.exe` after all stable gates pass.
- [ ] Publish `Titanium-APK-Builder-v10.0.0-Portable-Windows-x64.zip` after all stable gates pass.
- [ ] Sign the Windows executable when a code-signing certificate becomes available.

## v10.0 release criteria

v10.0 is considered stable only when all of the following are true:

1. A Windows release-package runner can launch both the standalone and Portable Titanium EXE with Python removed from runtime paths. ✅
2. The user can prepare or repair the build engine from inside Titanium without administrator rights; final isolated managed-engine CI verification remains.
3. A sample local HTML5 project passes preflight and builds to a working debug APK. ✅
4. The same generated project builds in CI to a signed Release APK and signed AAB, and both pass signing/bundle validation. ✅
5. Target SDK is API 36 or newer and generated APK/AAB outputs pass Titanium's post-build validator. ✅
6. No signing password is written to configuration, source files, logs or generated Gradle files. ✅
7. Titanium never terminates or deletes unrelated Java/Gradle/Android Studio components. ✅
8. CI validates Python syntax, analyzer tests, generated WebView compatibility, validator tests, a real API 36 debug APK, signed Release APK/AAB validation, standalone Windows EXE launch and exact Portable release-package assembly. ✅
9. README, CHANGELOG, migration, security, third-party notices and troubleshooting documentation match the actual application.

## After v10.0

Planned post-v10 work includes plug-in APIs, project templates, automatic PWA conversion, advanced WebView bridges, optional cloud build, macOS/Linux desktop builds and direct Play Console workflow support where APIs and account permissions allow it.
