<div align="center">

# Titanium APK Builder

### Native HTML / ZIP / URL → Android APK / AAB builder for Windows

**Python GUI • Native Android WebView • Gradle • Android SDK • Zero manual toolchain setup**

</div>

## v10 development

Titanium v10 is being rebuilt around a simple goal: **a user should not have to install Android Studio, Python, Node.js, Cordova, JDK or Gradle manually just to turn a web project into an Android application.**

The stable legacy release remains `v9.0.0`. The current v10 development line is `10.0.0-dev.4`; see the full [`ROADMAP.md`](ROADMAP.md) for the remaining stable-release gates.

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
- Supports WebView runtime permission bridging for camera, microphone and geolocation.
- Supports HTML file upload controls through the Android file picker.
- Supports HTTP/HTTPS downloads through Android DownloadManager.
- Routes `tel:`, `mailto:`, `sms:`, `geo:`, `market:`, `intent:` and other external/custom schemes to Android handlers.
- Supports HTML5 fullscreen/custom-view content and restores normal WebView navigation after exit.
- Explicitly destroys the WebView when the generated Activity closes to reduce retained WebView memory.
- CI builds and verifies a signed Release APK and signed AAB using a fresh ephemeral keystore.
- CI validates APK signing with `apksigner`, AAB signing integrity with `jarsigner`, and AAB processing with SHA-256-verified Google `bundletool`.

## Simple Mode

Simple Mode intentionally keeps the workflow short:

1. Choose HTML folder, ZIP or URL.
2. Set the app name and package name.
3. Click **Analyze Project**.
4. Click **Build APK**.

Titanium applies safe defaults for the remaining settings. Switching to Advanced Mode exposes SDK, output format, orientation, permissions and release signing.

## WebView compatibility engine

`10.0.0-dev.3` moved generated apps beyond a basic website wrapper.

Camera and microphone access are bridged through `WebChromeClient.onPermissionRequest` and Android runtime permissions. Location uses the WebView geolocation callback plus Android fine/coarse location permissions. These capabilities are only granted when the corresponding option is enabled in Titanium and the Android user grants the runtime permission.

HTML `<input type="file">` elements open the native Android file picker. HTTP/HTTPS downloads are handed to Android's DownloadManager, including the current WebView cookies and user-agent where available. Non-web schemes are routed to Android through explicit intents, while normal HTTP/HTTPS/file navigation stays inside the WebView.

HTML5 video and other custom-view content can enter fullscreen using `WebChromeClient` and safely return to the generated application. Back navigation first exits fullscreen, then walks WebView history, then closes the Activity.

## Signed release quality gate

`10.0.0-dev.4` adds an independent release pipeline test instead of assuming that a successful debug build means release output is safe.

Every release-gate CI run creates a new temporary RSA signing keystore with a random masked password. Titanium then generates an API 36 project with release signing enabled and Gradle builds **both** the Release APK and Release AAB. The APK must pass Android Build Tools `apksigner`, the AAB must pass signing-integrity verification, and a SHA-256-pinned `bundletool 1.18.3` must successfully turn the bundle into a universal APK set.

The test keystore and password exist only on the temporary CI runner and are never committed to the repository. This CI gate is separate from the planned in-app post-build validator that will later give the same checks directly to Titanium users.

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

Toolchain archives are SHA-256 verified. ZIP imports reject path traversal entries. The preflight analyzer blocks missing or unsafe local web assets before a build starts. Generated WebView permission requests only grant camera/microphone resources explicitly enabled by the project and approved by Android runtime permission prompts. The CI release gate also creates signing credentials dynamically and masks them instead of storing a reusable test password in the repository.

## Current status

**v10.0.0-dev.4 — active development**

The public `v10.0.0-dev.1` prerelease proved the standalone EXE + Portable JDK/Gradle packaging path. dev.2 added UX, diagnostics and build-engine repair. dev.3 added the production-oriented WebView compatibility layer. dev.4 adds signed APK/AAB release validation. Stable `v10.0.0` will only be published after every release criterion in [`ROADMAP.md`](ROADMAP.md) passes.

## Author

Developed by **Swir**.
