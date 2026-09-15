# Third-party runtime notices

Titanium APK Builder can use or package the following build tools:

## Eclipse Temurin / OpenJDK
Eclipse Temurin binaries are distributed by Eclipse Adoptium under the GNU General Public License, version 2, with the Classpath Exception. The Portable Runtime release may include an unmodified Temurin JDK distribution together with its original license and notice files.

## Gradle Build Tool
Gradle Build Tool is open source under the Apache License 2.0. The Portable Runtime release may include the official binary distribution with its original LICENSE, NOTICE and README files.

## Google bundletool
Google bundletool is distributed under the Apache License 2.0. Titanium may include the official, unmodified `bundletool-all` release JAR in the Portable Runtime so AAB artifacts can be validated without an additional first-run download. Titanium verifies the bundled JAR against a pinned SHA-256 digest and includes a copy of the bundletool Apache 2.0 license in the Portable package under `licenses/bundletool-LICENSE.txt`.

## Android SDK / Android command-line tools
Android SDK components are governed by the Android SDK License Agreement. Titanium does not silently bundle those SDK components into the Portable Runtime package. The user is shown the license notice and must accept the Android SDK terms before Titanium provisions the SDK into a private per-user directory.

Titanium does not install these build tools system-wide and does not require administrator rights for its managed toolchain mode.
