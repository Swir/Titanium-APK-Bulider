<div align="center">

# Titanium APK Builder

### Native HTML / ZIP / URL → Android APK / AAB builder for Windows

**Python GUI • Native Android WebView • Gradle • Android SDK • Zero manual toolchain setup**

</div>

## v10 development

Titanium v10 is being rebuilt around a simple goal: **a user should not have to install Android Studio, Python, Node.js, Cordova, JDK or Gradle manually just to turn a web project into an Android application.**

The stable legacy release remains `v9.0.0`. The current v10 development line is `10.0.0-dev.2`; see the full [`ROADMAP.md`](ROADMAP.md) for the remaining stable-release gates.

## What v10 already does

- Builds a local HTML/CSS/JavaScript folder into a native Android WebView app.
- Imports ZIP web projects safely.
- Creates URL-based Android wrappers.
- Generates native Gradle/Android project files itself — no template Android Studio project is required.
- Builds APK or AAB in Debug or Release mode.
- Defaults to Android 16 / API 36.
- Supports JKS signing without writing signing passwords to config files.
- Detects JDK, Android SDK and Gradle.
- Can provision a private per-user build engine from inside Titanium.
- Provides **Simple Mode** for fast builds and **Advanced Mode** for full controls.
- Runs a **Project Analyzer** before build to catch missing assets, unsafe paths and common WebView compatibility problems.
- Includes a first-run setup wizard and a safe **Repair Build Engine** action.
- Retries and resumes interrupted managed-toolchain downloads when the server supports HTTP Range requests.

## Simple Mode

Simple Mode intentionally keeps the workflow short:

1. Choose HTML folder, ZIP or URL.
2. Set the app name and package name.
3. Click **Analyze Project**.
4. Click **Build APK**.

Titanium applies safe defaults for the remaining settings. Switching to Advanced Mode exposes SDK, output format, orientation, permissions and release signing.

## Project Analyzer

The preflight analyzer runs before Gradle and can detect or report:

- missing `index.html`;
- missing local `src`, `href` or `poster` assets;
- unsafe ZIP paths;
- plain-HTTP URLs and asset references;
- `file://` references that may fail in Android WebView;
- PWA manifest presence;
- service-worker usage;
- unusually large ZIP projects.

Blocking errors stop the build before Android compilation begins.

## Zero-manual-setup model

The Windows EXE itself is standalone. Python is not required on the user's PC.

For Android compilation, Titanium keeps its build engine under the current user's application-data directory rather than installing tools system-wide. The **Prepare Build Engine** action provisions:

- Eclipse Temurin JDK
- Gradle
- Android command-line tools
- Android Platform Tools
- Android API 36 platform
- Android Build Tools 36.0.0

No administrator rights or Android Studio installation are required.

Android SDK downloads are license-gated. Titanium asks the user to confirm the Android SDK terms before it provisions Google's SDK components.

The **Repair Build Engine** command only checks and repairs Titanium-managed components. It never removes system Java, Android Studio, a system Android SDK or the Portable runtime.

## Run v10 from source

Python 3.11+ is recommended for development:

```bash
python "Titanium V10.py"
```

The v10 application currently uses only the Python standard library.

## Legacy v9

The legacy file `Titanium V9.py` is retained so the published `v9.0.0` release remains reproducible. v9 and v10 are intentionally separated while the v10 quality gates are completed.

## Security improvements in v10

Titanium v10 does **not** globally terminate `java.exe`. It also does **not** save keystore passwords in its JSON configuration. Release signing secrets exist only in memory and are passed to Gradle through temporary process environment variables.

Toolchain archives are SHA-256 verified. ZIP imports reject path traversal entries. The new preflight analyzer also blocks missing or unsafe local web assets before a build starts.

## Current status

**v10.0.0-dev.2 — active development**

The public `v10.0.0-dev.1` prerelease proved the standalone EXE + Portable JDK/Gradle packaging path. dev.2 adds the next UX and reliability layer; stable `v10.0.0` will only be published after every release criterion in [`ROADMAP.md`](ROADMAP.md) passes.

## Author

Developed by **Swir**.
