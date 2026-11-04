#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${ANDROID_NDK_HOME:?Set ANDROID_NDK_HOME to Android NDK directory}"
cmake -S "$ROOT" -B "$ROOT/build-android" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-28 -DANDROID_STL=c++_shared \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$ROOT/build-android" --parallel 2
mkdir -p "$ROOT/dist/modelbridge/config"
cp "$ROOT/manifest.json" "$ROOT/dist/modelbridge/"
cp "$ROOT/config/config.json" "$ROOT/dist/modelbridge/config/"
cp "$ROOT/build-android/libmodelbridge.so" "$ROOT/dist/modelbridge/"
(cd "$ROOT/dist/modelbridge" && zip -q -r "$ROOT/dist/modelbridge.levipack" manifest.json libmodelbridge.so config/)
echo "Created $ROOT/dist/modelbridge.levipack"

python3 - "$ROOT/dist/modelbridge.levipack" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
    names=set(z.namelist())
    assert {"manifest.json","libmodelbridge.so"} <= names
    assert z.testzip() is None
    print("ZIP package validated")
PY
