# ZipShield Pro

Encrypt-only Android app that turns an existing ZIP into a standard WinZip AES-256 encrypted ZIP (`<name>-encrypted.zip` in Downloads/ZipShield/), which opens in File Manager / ZArchiver / 7-Zip with the password.

- Package: `com.zipshield.app`
- Engine: custom WinZip AES-256 writer using hardware JCE crypto (no third-party jars), 2-thread pipeline, single-pass streaming.
- UI: pick a ZIP, enter a password, tap ENCRYPT, done. No decrypt in the app, no GEN KEY, no `.zsp`.
- Footer: Created by Ashok.

## Build

Run `./build.sh` (needs JDK 17 + Android SDK 34 + a `debug.keystore` in this directory), or push to `main` — GitHub Actions builds the APK and uploads it as the `zipshield-apk` artifact.

## Honest limits

- In a standard ZIP the filenames are visible; only the file contents are locked (the password is asked on open/extract).
- Already-locked ZIPs are rejected.
- A forgotten password cannot be recovered by anyone.
