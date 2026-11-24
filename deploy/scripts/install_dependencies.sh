#!/usr/bin/env bash
set -euo pipefail
command -v aws >/dev/null
docker version >/dev/null
test -s /opt/spotify-data/catalog.csv
test -s /opt/spotify-data/audio.npy
test -s /opt/spotify-data/interactions.npz
