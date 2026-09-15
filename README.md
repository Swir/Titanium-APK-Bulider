<div align="center">

# Titanium APK Builder

### Native HTML / ZIP / URL → Android APK / AAB builder for Windows

**Native Android WebView • Gradle • Android SDK • Standalone Windows EXE • Zero manual toolchain setup**

</div>

## v10 development

Titanium v10 is built around one goal: **a user should not have to manually install Android Studio, Python, Node.js, Cordova, JDK or Gradle just to turn a web project into an Android application.**

The stable legacy release remains `v9.0.0`. The current v10 development line is **`10.0.0-dev.6`**; see [`ROADMAP.md`](ROADMAP.md) for the remaining stable-release gates.

## What v10 already does

- Builds local HTML/CSS/JavaScript folders, ZIP web projects and URLs into native Android WebView apps.
- Generates its own Gradle/Android project — no Android Studio template is required.
- Builds APK or AAB in Debug or Release mode and targets Android 16 / API 36 by default.
- Supports JKS signing without persisting signing passwords.
- Provides Simple and Advanced interface modes, first-run setup, Project Analyzer and safe Build Engine repair.
- Detects or provisions JDK, Gradle, Android SDK components and Google bundletool in user space without administrator rights.
- Retries/resumes managed toolchain downloads and verifies managed archives with SHA-256.
- Supports WebView camera, microphone, geolocation, file upload, downloads, external schemes and HTML5 fullscreen.
- Runs post-build APK/AAB validation before reporting a successful output.
- Builds and smoke-tests a standalone Windows EXE in CI with Python removed from runtime paths.
- Builds the exact Portable release package in pull-request CI before it can be merged.

## WebView compatibility engine

Generated apps include Android runtime permission bridges for camera, microphone and location. HTML `<input type="file">` opens the native picker; HTTP/HTTPS downloads use Android `DownloadManager`; non-web schemes such as `tel:`, `mailto:`, `sms:`, `geo:`, `market:` and `intent:` are routed through Android handlers.

HTML5 custom-view/fullscreen content is supported, back navigation exits fullscreen before traversing WebView history, and the generated Activity explicitly destroys its WebView during teardown.

## Project Analyzer

Before Gradle starts, Titanium can report or block problems such as:

- missing `index.html`;
- missing local HTML assets;
- unsafe ZIP paths;
- plain-HTTP references;
- problematic `file://` references;
- PWA manifest/service-worker usage;
- unusually large ZIP projects.

Blocking findings stop the build before Android compilation begins.

## Signed release and post-build validation

The CI release gate creates a fresh temporary signing keystore for every run, builds both a signed Release APK and AAB, verifies the APK with Android Build Tools `apksigner`, verifies AAB signing integrity and validates the bundle with SHA-256-pinned Google `bundletool 1.18.3`.

Titanium also performs validation itself after a normal build. APK output is ZIP-integrity checked and passed through `apksigner`. AAB output is ZIP-integrity checked, structurally validated with `bundletool`, and checked for signing integrity with JDK `jarsigner` plus real signature metadata under `META-INF`.

## Zero-manual-setup model

The standalone EXE does not require Python on the target PC. The Portable package is built with:

- Titanium APK Builder EXE;
- Eclipse Temurin JDK 21;
- Gradle 9.6.0;
- Google bundletool 1.18.3;
- required documentation, notices and the bundletool Apache 2.0 license.

The release workflow verifies the downloaded JDK, Gradle and bundletool artifacts, confirms `java.exe`, `jarsigner.exe`, `gradle.bat` and bundletool execution, then smoke-launches Titanium from inside the Portable directory with Python removed from `PATH`, `PYTHONHOME` and `PYTHONPATH` before the ZIP is accepted as a release-candidate artifact.

### Android SDK licensing

Android SDK components are **not** redistributed in the Portable ZIP. Titanium displays the Android SDK license notice and provisions the command-line tools, platform tools, API 36 platform and Build Tools 36.0.0 into a private per-user directory only after the user accepts the SDK terms.

No Android Studio or administrator rights are required.

## Release workflow safety

Release packaging and release publication are separate jobs. Pull requests run the exact package-building path with read-only repository permissions. The write-enabled publish job is skipped for pull requests and is available only for explicit release/tag events.

## Run from source

Python 3.11+ is recommended for development:

```bash
python "Titanium V10.py"
```

The v10 application currently uses only the Python standard library at runtime.

## Security

Titanium v10 does **not** globally terminate `java.exe`, does not save signing passwords in its JSON configuration, rejects ZIP path traversal and passes signing secrets to Gradle only through the process environment. Managed downloads are checksum-verified and Repair Build Engine only modifies Titanium-managed files.

See [`SECURITY.md`](SECURITY.md), [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

## Current status

**v10.0.0-dev.6 — release-candidate hardening**

The exact Portable package now passes an automated PR packaging gate. Stable `v10.0.0` will be published only after the remaining stable criteria in [`ROADMAP.md`](ROADMAP.md) pass, especially the isolated managed Build Engine Prepare/Repair test.

## Legacy v9

`Titanium V9.py` is retained so the published `v9.0.0` release remains reproducible while v10 completes its final quality gates.

## Author

Developed by **Swir**.
