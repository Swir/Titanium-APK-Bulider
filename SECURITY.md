# Security Policy

## Titanium v10 security rules

Titanium APK Builder v10 is designed around the following rules:

- Never terminate unrelated Java, Gradle or Android Studio processes.
- Never persist keystore passwords or key passwords in configuration files.
- Never write signing secrets into generated Gradle source files.
- Pass signing secrets only to the child build process through temporary environment variables.
- Reject ZIP entries that can escape the extraction directory.
- Keep managed build tools and workspaces inside the current user's application-data directory.
- Do not require administrator rights for normal use.
- Do not silently bundle or install Android SDK components without user-visible license consent.
- Keep downloaded toolchain components isolated from the system-wide PATH unless they are used by a Titanium child process.

## Reporting a vulnerability

Please open a GitHub issue for non-sensitive security problems. For a vulnerability that would expose credentials or private user data, do not post secrets, keystore files or passwords in a public issue. Provide only the minimum reproduction information required to identify the problem.

## Signing material

Keystore files remain under the user's control. Titanium v10 does not copy the keystore into the generated project. Passwords are held in process memory for the duration of the build and are not included in the saved Titanium configuration.
