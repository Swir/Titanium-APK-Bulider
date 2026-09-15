# Migrating from Titanium APK Builder v9 to v10

Titanium v10 is a new architecture rather than an in-place upgrade of the v9/Ghost builder.

## What changes

### No Android Studio template project
v9 cloned and modified an existing Android Studio project. v10 generates its own Android Gradle project for every build. Existing v9 template projects are not required and are not modified.

### No Cordova / Node.js requirement
v10 builds a native Android WebView wrapper directly with the Android Gradle Plugin. Cordova and Node.js are not part of the v10 build path.

### New source modes
v10 accepts:
- a folder containing `index.html`;
- a ZIP web project;
- an HTTP/HTTPS URL.

### Managed build engine
Use the **Build Engine** tab and **Prepare Build Engine**. Titanium can use a compatible system toolchain, its private per-user toolchain, or a Portable runtime placed beside the EXE.

The v10 Portable release contains the standalone Titanium EXE, Eclipse Temurin JDK 21, Gradle 9.6.0 and SHA-256-verified Google bundletool 1.18.3. Android SDK components are not redistributed in the Portable archive; Titanium downloads them directly into its private per-user directory only after the user accepts Google's Android SDK terms.

The Prepare/Repair path is tested in CI from an isolated user-data directory with system Java, Android SDK and Gradle discovery disabled. The test also deliberately corrupts managed components and verifies that **Repair Build Engine** restores them without using system-wide install locations.

### Signing passwords are not migrated
v9 could save keystore passwords in its JSON configuration. v10 deliberately does not migrate or persist those passwords. Re-enter store/key passwords when building a signed release.

### Configuration
v10 stores its configuration under the current user's local application-data directory in `TitaniumAPKBuilder`. Legacy `ghost_apex_config.json` is ignored.

## Recommended migration flow

1. Keep v9 installed or archived until an important project has been rebuilt successfully with v10.
2. Download the v10 Portable release for the easiest setup.
3. Open Titanium and prepare the Build Engine if Android SDK components are not present yet.
4. Select the original HTML project folder or ZIP instead of a v9-generated Android Studio project.
5. Re-enter app identity, version and permissions.
6. Re-select your JKS/keystore for Release builds and enter passwords again.
7. Build a Debug APK and test it on a device.
8. Build a signed Release APK/AAB only after the Debug build behaves correctly.

Titanium validates generated APK/AAB artifacts after the build. Signed APK output is checked with Android Build Tools `apksigner`; AAB output is structurally checked with bundletool and its signing integrity is checked with JDK `jarsigner` plus signature metadata inspection.

## What v10 intentionally does not import

- v9 temporary Ghost workspace;
- v9-generated Android Studio template state;
- saved signing passwords;
- v9 regex-injected Gradle/Manifest changes.

This keeps the v10 build reproducible and prevents insecure legacy state from silently carrying forward.
