# Titanium APK Builder v10 — Troubleshooting

## Build Engine says `missing`

Open **Build Engine** and click **Prepare Build Engine**. Titanium checks for a Portable runtime beside the EXE first, then its private per-user toolchain, then compatible system tools.

The v10 Portable release contains the standalone EXE, Eclipse Temurin JDK 21, Gradle 9.6.0 and Google bundletool 1.18.3. Android SDK components are downloaded only after the user accepts the Android SDK terms.

## Android SDK download fails

- Confirm that the PC has internet access.
- Confirm that HTTPS access to `dl.google.com` is not blocked by a proxy, firewall or DNS filter.
- Reopen Titanium and run **Prepare Build Engine** again.
- If a managed component is incomplete, use **Repair Build Engine**.
- Do not manually edit the managed toolchain folder while provisioning is active.

Titanium verifies the Android command-line tools archive with SHA-256 before extraction.

## JDK, Gradle or bundletool download fails

Titanium downloads managed tools only from their official distribution endpoints and verifies their SHA-256 hashes. A checksum mismatch is treated as a hard failure and the invalid managed artifact is discarded. **Repair Build Engine** can reacquire incomplete or corrupted Titanium-managed components without deleting a system Java, Android Studio installation or system Android SDK.

## `index.html` not found

Folder and ZIP modes require an `index.html`. Titanium also accepts a ZIP containing one single nested web-project directory and flattens that directory automatically. ZIP paths attempting to escape the extraction directory are rejected.

## Invalid package name

Use a lowercase Android package identifier such as:

```text
com.example.myapp
```

Spaces, uppercase letters and punctuation other than dots/underscores are rejected.

## Release signing fails

Check that:

- the selected `.jks` or `.keystore` file exists;
- the alias is correct;
- store password and key password are correct.

Titanium does not save those passwords. They must be entered again after restarting the application.

## Build finishes but post-build validation fails

Titanium does not treat a successful Gradle exit code as sufficient for a valid release artifact.

- APK output is checked for ZIP integrity and verified with Android Build Tools `apksigner`.
- AAB output is checked for ZIP integrity, validated with Google bundletool and checked for signing integrity with JDK `jarsigner` plus signature metadata inspection.

If validation fails, review the final validator section in the Titanium log and run **Repair Build Engine** if `apksigner`, `jarsigner` or bundletool is reported missing or damaged.

## Where does Titanium keep its files?

Managed toolchain, workspace and configuration data are stored under the current Windows user's local application-data directory in `TitaniumAPKBuilder`. A Portable release can additionally provide `runtime/jdk`, `runtime/gradle` and `runtime/bundletool` beside the EXE. Android SDK components stay in the private user-data toolchain unless a compatible external SDK is explicitly detected.

## Titanium does not require Android Studio

v10 generates its own native Android Gradle project. A pre-existing Android Studio project is not used as a template.

## Reporting a build problem

Use the log shown in Titanium and include:

- Titanium version;
- source mode (Folder / ZIP / URL);
- APK or AAB;
- Debug or Release;
- whether Build Engine status reports all components ready;
- the final build/validation error section.

Do not include keystore passwords, signing passwords, API secrets or private source files in public GitHub issues.
