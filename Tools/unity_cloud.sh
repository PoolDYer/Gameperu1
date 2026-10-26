#!/usr/bin/env bash
set -euo pipefail
export XDG_CONFIG_HOME=/workspace/unity-runtime/config
export XDG_CACHE_HOME=/workspace/unity-runtime/cache
export XDG_DATA_HOME=/workspace/unity-runtime/data
mkdir -p "$XDG_CONFIG_HOME/unity3d" "$XDG_CACHE_HOME/unity3d" "$XDG_DATA_HOME"
exec /workspace/toolchains/unity-6000.6.7f1/Editor/Unity "$@"
