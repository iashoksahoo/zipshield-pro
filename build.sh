#!/bin/bash
# ZipShield Pro v3.9 — encrypt-only, SIMPLE UI + hardware-AES engine.
# No third-party jars: WinZip AES-256 is written by FastZipEncryptor
# (JCE hardware AES + HmacSHA1). Same package and keystore as before,
# so this installs as an update over all earlier versions. Manual build.
set -e
SDK="$HOME/android-sdk"
BT="$SDK/build-tools/34.0.0"
PLATFORM="$SDK/platforms/android-34/android.jar"
cd "$(dirname "$0")"
for t in "$BT/aapt2" "$BT/d8" "$BT/zipalign" "$BT/apksigner" "$PLATFORM"; do
  [ -e "$t" ] || { echo "MISSING: $t"; exit 1; }
done
export PATH="$HOME/jdk17/bin:$PATH"
command -v javac >/dev/null || { echo "MISSING: javac"; exit 1; }
[ -f debug.keystore ] || { echo "MISSING: debug.keystore"; exit 1; }
[ -f assets/zipshield.html ] || { echo "MISSING: assets/zipshield.html"; exit 1; }
rm -rf out/gen out/obj out/dex out/res.zip out/app-*.apk out/sources.txt out/ZipShield-Pro.apk
mkdir -p out/gen out/obj out/dex
"$BT/aapt2" compile --dir res -o out/res.zip
"$BT/aapt2" link -o out/app-unsigned.apk -I "$PLATFORM" --manifest AndroidManifest.xml --java out/gen out/res.zip
find java out/gen -name "*.java" > out/sources.txt
javac -encoding UTF-8 -nowarn -classpath "$PLATFORM" -d out/obj @out/sources.txt
"$BT/d8" --lib "$PLATFORM" --min-api 29 --output out/dex $(find out/obj -name "*.class")
cp out/app-unsigned.apk out/app-dex.apk
(cd out/dex && zip -q ../app-dex.apk classes.dex)
zip -q out/app-dex.apk assets/zipshield.html
"$BT/zipalign" -f -p 4 out/app-dex.apk out/app-aligned.apk
"$BT/apksigner" sign --ks debug.keystore --ks-pass pass:android --key-pass pass:android --out out/ZipShield-Pro.apk out/app-aligned.apk
"$BT/apksigner" verify out/ZipShield-Pro.apk && echo "signature: OK"
"$BT/aapt2" dump badging out/ZipShield-Pro.apk | head -6
ls -la out/ZipShield-Pro.apk
