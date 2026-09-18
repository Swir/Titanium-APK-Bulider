# Titanium APK Builder — v10 Roadmap

Titanium v10 is the transition from the experimental v9/Ghost codebase to a reproducible, secure, zero-manual-setup Android builder for Windows.

## Stable v10.0.0 — released ✅

Titanium APK Builder **10.0.0** is now published as the stable v10 release.

The exact stable application line passed the normal Windows/Android CI, exact Portable release-package gate and isolated managed Build Engine Prepare/Repair gate before publication. The final release workflow rebuilt and smoke-tested the standalone EXE and Portable package again before the write-enabled publication job created the public GitHub Release.

Stable release: [`v10.0.0`](https://github.com/Swir/Titanium-APK-Bulider/releases/tag/v10.0.0)

<!-- SWIR-PROGRESS-SVG-PRO:v1 -->
<p align="center">
  <img width="100%" src="assets/readme/progress-mini.svg" alt="Titanium APK Builder v10.0 stable release criteria — 10 of 10 complete" />
</p>

| Measured scope | Completed | Total | Progress | Status |
|---|---:|---:|---:|---|
| v10.0 stable release criteria | **10** | **10** | **100.0%** | **COMPLETE** |

> This 100.0% applies only to the published v10.0 stable release criteria. Post-v10 ideas below remain future work and are not folded into this completed release scope.

The Portable package contains the standalone EXE, Eclipse Temurin JDK 21, Gradle 9.6.0 and SHA-256-verified Google bundletool 1.18.3 with its Apache 2.0 license. Android SDK components remain license-gated and are provisioned into Titanium's private user-data directory after explicit acceptance; they are intentionally not redistributed in the Portable archive.

## v10.0 milestones

### M0 — v10 foundation ✅
- [x] Native v10 architecture without Cordova or Node.js.
- [x] Native Gradle/Android project generation.
- [x] HTML folder, ZIP and URL source modes.
- [x] APK and AAB output.
- [x] Android 16 / API 36 default target.
- [x] No global Java process termination.
- [x] Signing passwords are not persisted.
- [x] Signing secrets reach Gradle only through process environment variables.
- [x] Workspace/toolchain stays under application user data.
- [x] No Android Studio template project is required.

### M1 — Managed Build Engine ✅
- [x] Detect portable, Titanium-managed or compatible system JDK/SDK/Gradle.
- [x] One-click managed JDK/Gradle/Android SDK provisioning.
- [x] Android SDK license consent before provisioning.
- [x] SHA-256 verification of managed JDK, Gradle, Android command-line tools and bundletool.
- [x] Resumable downloads with retry/backoff.
- [x] Repair Build Engine only modifies Titanium-managed files.
- [x] Isolated Windows CI provisions without discovering system Java/Android SDK/Gradle.
- [x] Isolated CI deliberately corrupts managed bundletool/API 36 and proves Repair restores a ready toolchain.

Future/non-blocking: Stable/Preview toolchain channels and offline cache import/export.

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

Future/non-blocking: deeper CSS/JS scanning, custom network-security policies, immersive mode, system-bar theming, splash/icon generators and PWA metadata import.

### M3 — Release and Play pipeline ✅ for v10.0 scope
- [x] APK and AAB build modes.
- [x] Debug and Release variants.
- [x] JKS signing without saving passwords.
- [x] CI builds signed Release APK and AAB from the same generated project.
- [x] In-app APK verification with `apksigner`.
- [x] In-app AAB structural validation with SHA-256-pinned bundletool.
- [x] In-app AAB signature-integrity validation with `jarsigner` plus signature metadata checks.

Future/non-blocking: keystore wizard, automatic version-code management, Play readiness report, richer API compatibility warnings and R8/ProGuard controls.

### M4 — Desktop application ✅ for v10.0 scope
- [x] Separate UI, build engine, Android generator, analyzer and validator modules.
- [x] Simple / Advanced modes.
- [x] First-run Build Engine setup flow.
- [x] Timestamped logs with copy/clear actions.
- [x] Human-readable preflight diagnostics.

Future/non-blocking: additional visual polish, project profiles/recent projects, log filtering/export, suggested fixes, optional crash reports, multilingual UI and expanded accessibility/high-DPI work.

### M5 — Automated quality gate ✅
- [x] Unit/security/analyzer/validator tests.
- [x] Real API 36 debug APK CI build.
- [x] Ephemeral-keystore signed Release APK/AAB CI build.
- [x] APK signature verification with `apksigner`.
- [x] AAB signing verification and bundletool processing.
- [x] Standalone Windows EXE smoke launch without Python runtime paths.
- [x] Exact Portable release-package build and smoke launch.
- [x] Fully isolated managed Build Engine Prepare/Repair integration test.

Future/non-blocking: further deterministic packaging work, SBOM generation and external malware-scanner reporting.

### M6 — Stable release packaging ✅
- [x] Automated versioned Windows EXE packaging.
- [x] Automated versioned Portable ZIP with EXE + JDK + Gradle + bundletool.
- [x] SHA-256 checksum assets.
- [x] Validate packaged Java, jarsigner, Gradle, bundletool and licenses.
- [x] Smoke-launch the EXE from inside Portable without Python runtime paths.
- [x] Pull requests build the exact release package with read-only permissions.
- [x] Publication is isolated in a separate write-enabled job.
- [x] Exact `10.0.0` stable PR repeated all green gates.
- [x] Exact `10.0.0` candidate merged to `main`.
- [x] Tag `v10.0.0` created and stable GitHub Release published.
- [x] Versioned EXE, Portable ZIP and matching SHA-256 assets published.

Optional/non-blocking: Windows Authenticode signing when a suitable code-signing certificate becomes available.

## Stable release criteria

All v10.0.0 release criteria are satisfied:

1. Standalone and Portable EXEs launch without Python runtime paths. ✅
2. Isolated Prepare/Repair works without system Java/Gradle/Android SDK locations. ✅
3. Local HTML5 project builds a real API 36 debug APK. ✅
4. Signed Release APK and AAB build and pass signing/bundle validation. ✅
5. Generated APK/AAB output passes Titanium's post-build validator. ✅
6. Signing passwords are not persisted to config/generated Gradle/repository files. ✅
7. Titanium does not terminate/delete unrelated development tools. ✅
8. CI covers source/tests, WebView generation, Android builds, signing, Windows EXE launch, Portable packaging and isolated Prepare/Repair. ✅
9. README, CHANGELOG, migration, troubleshooting, security and third-party notices match v10 behavior. ✅
10. Stable v10.0.0 release assets were rebuilt, verified and published by the controlled release workflow. ✅

## After v10.0

Planned post-v10 work includes the non-blocking enhancements above, plug-in APIs, project templates, deeper PWA conversion, advanced WebView bridges, optional cloud build, macOS/Linux desktop builds and direct Play Console workflows where APIs/account permissions allow them.
