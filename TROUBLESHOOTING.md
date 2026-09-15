# Titanium APK Builder v10 — Troubleshooting

## Build Engine says `missing`

Open **Build Engine** and click **Prepare Build Engine**. Titanium checks for a portable runtime beside the EXE first, then its private per-user toolchain, then compatible system tools.

The Portable release is intended to include JDK and Gradle. Android SDK components are downloaded only after the user accepts the Android SDK terms.

## Android SDK download fails

- Confirm that the PC has internet access.
- Confirm that HTTPS access to `dl.google.com` is not blocked by a proxy, firewall or DNS filter.
- Reopen Titanium and run **Prepare Build Engine** again.
- Do not manually edit the managed toolchain folder while provisioning is active.

Titanium verifies the Android command-line tools archive with SHA-256 before extraction.

## JDK or Gradle download fails

Titanium downloads managed tools only from their official distribution endpoints and verifies their SHA-256 hashes. A checksum mismatch is treated as a hard failure and the archive is discarded.

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

## Where does Titanium keep its files?

Managed toolchain, workspace and configuration data are stored under the current Windows user's local application-data directory in `TitaniumAPKBuilder`. A Portable release can additionally provide `runtime/jdk` and `runtime/gradle` beside the EXE.

## Titanium does not require Android Studio

v10 generates its own native Android Gradle project. A pre-existing Android Studio project is not used as a template.

## Reporting a build problem

Use the log shown in Titanium and include:

- Titanium version;
- source mode (Folder / ZIP / URL);
- APK or AAB;
- Debug or Release;
- the final build-error section.

Do not include keystore passwords, signing passwords, API secrets or private source files in public GitHub issues.
