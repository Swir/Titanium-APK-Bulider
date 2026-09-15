<div align="center">

# Titanium APK Builder

### Native HTML / ZIP / URL → Android APK / AAB builder for Windows

**Python GUI • Native Android WebView • Gradle • Android SDK • Zero manual toolchain setup**

</div>

## v10 development

Titanium v10 is being rebuilt around a simple goal: **a user should not have to install Android Studio, Python, Node.js, Cordova, JDK or Gradle manually just to turn a web project into an Android application.**

The stable legacy release remains `v9.0.0`. The repository now also contains the new `Titanium V10.py` development foundation and the full [`ROADMAP.md`](ROADMAP.md).

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

## Current status

**v10.0.0-dev.1 — foundation / alpha**

It is suitable for development and testing, not yet the final stable v10 release. See [`ROADMAP.md`](ROADMAP.md) for release criteria and remaining work.

## Author

Developed by **Swir**.
