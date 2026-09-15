<div align="center">

# Titanium APK Builder

### Native HTML / ZIP / URL → Android APK / AAB builder for Windows

**Native Android WebView • Gradle • Android SDK • Standalone Windows EXE • Zero manual toolchain setup**

</div>

## Titanium v10

Titanium APK Builder **10.0.0** is the stable v10 line. Its goal is simple: a user should not have to manually install Android Studio, Python, Node.js, Cordova, JDK or Gradle just to turn a web project into an Android application.

The exact `10.0.0` candidate is required to pass the normal Android/Windows CI, the full Portable release-package gate and the isolated managed Build Engine Prepare/Repair gate before publication.

## What v10 does

- Builds local HTML/CSS/JavaScript folders, ZIP web projects and URLs into native Android WebView apps.
- Generates its own Gradle/Android project — no Android Studio template is required.
- Builds APK or AAB in Debug or Release mode and targets Android 16 / API 36 by default.
- Supports JKS signing without persisting signing passwords.
- Provides Simple and Advanced modes, first-run setup, Project Analyzer and safe Build Engine repair.
- Detects or provisions JDK, Gradle, Android SDK components and Google bundletool in user space without administrator rights.
- Retries/resumes managed toolchain downloads and verifies managed archives with SHA-256.
- Supports WebView camera, microphone, geolocation, file upload, downloads, external schemes and HTML5 fullscreen.
- Runs post-build APK/AAB validation before reporting successful output.
- Builds and smoke-tests standalone and Portable Windows packages in CI without relying on Python runtime paths.

## Simple workflow

1. Choose an HTML folder, ZIP project or URL.
2. Set the app name and package name.
3. Run **Analyze Project**.
4. Build an APK, or switch to Advanced mode for AAB/Release/signing options.

## WebView compatibility engine

Generated apps include Android runtime permission bridges for camera, microphone and location. HTML `<input type="file">` opens the native picker; HTTP/HTTPS downloads use Android `DownloadManager`; non-web schemes such as `tel:`, `mailto:`, `sms:`, `geo:`, `market:` and `intent:` are routed through Android handlers.

HTML5 custom-view/fullscreen content is supported, back navigation exits fullscreen before traversing WebView history, and the generated Activity explicitly destroys its WebView during teardown.

## Project Analyzer

Before Gradle starts, Titanium can report or block problems such as missing `index.html`, missing local assets, unsafe ZIP paths, plain-HTTP references, problematic `file://` references, PWA/service-worker usage and unusually large ZIP projects.

Blocking findings stop the build before Android compilation begins.

## Release signing and post-build validation

The CI release gate creates a fresh temporary signing keystore, builds both a signed Release APK and AAB, verifies the APK with Android Build Tools `apksigner`, checks AAB signing integrity and validates the bundle with SHA-256-pinned Google `bundletool 1.18.3`.

Titanium performs validation itself after a normal build. APK output is ZIP-integrity checked and passed through `apksigner`. AAB output is ZIP-integrity checked, structurally validated with `bundletool`, and checked with JDK `jarsigner` plus real signature metadata under `META-INF`.

## Zero-manual-setup model

The standalone EXE does not require Python on the target PC. The Portable package contains:

- Titanium APK Builder EXE;
- Eclipse Temurin JDK 21;
- Gradle 9.6.0;
- Google bundletool 1.18.3;
- documentation, notices and the bundletool Apache 2.0 license.

The release workflow verifies JDK, Gradle and bundletool downloads, confirms `java.exe`, `jarsigner.exe`, `gradle.bat` and bundletool execution, then smoke-launches Titanium from inside the Portable directory with Python removed from `PATH`, `PYTHONHOME` and `PYTHONPATH`.

### Android SDK licensing

Android SDK components are **not** redistributed in the Portable ZIP. Titanium displays the Android SDK license notice and provisions the command-line tools, Platform Tools, API 36 platform and Build Tools 36.0.0 into a private per-user directory only after the user accepts the SDK terms.

The isolated managed-engine CI starts without detectable system Java, Android SDK or Gradle, provisions the complete Titanium-managed toolchain into a fresh user-data directory, deliberately damages managed components and proves **Repair Build Engine** restores them. No Android Studio or administrator rights are required for normal use.

## Release workflow safety

Release packaging and release publication are separate jobs. Pull requests build the exact release package with read-only repository permissions. The write-enabled publish job is skipped for pull requests and runs only for explicit release/tag events.

Stable downloadable assets use versioned names and include SHA-256 checksum files.

## Run from source

Python 3.11+ is recommended for development:

```bash
python "Titanium V10.py"
```

The v10 application currently uses only the Python standard library at runtime.

## Security

Titanium v10 does **not** globally terminate `java.exe`, does not save signing passwords in its JSON configuration, rejects ZIP path traversal and passes signing secrets to Gradle only through the process environment. Managed downloads are checksum-verified and Repair Build Engine only modifies Titanium-managed files.

See [`SECURITY.md`](SECURITY.md), [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) and [`MIGRATION_V9_TO_V10.md`](MIGRATION_V9_TO_V10.md).

## Current status

**10.0.0 — stable release candidate**

All defined v10.0 technical and documentation criteria passed on the preceding candidate. The exact `10.0.0` commit is undergoing the final repeated CI/package/managed-engine gates before stable publication.

## Legacy v9

`Titanium V9.py` is retained so the published `v9.0.0` release remains reproducible.

## Author

Developed by **Swir**.
