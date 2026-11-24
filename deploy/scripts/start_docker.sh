#!/usr/bin/env bash
set -euo pipefail
image=$(sed -n 's/^IMAGE=//p' /opt/spotify-hybrid/release.env)
region=$(sed -n 's/^AWS_REGION=//p' /opt/spotify-hybrid/release.env)
[[ $image =~ ^[0-9]{12}\.dkr\.ecr\.[a-z0-9-]+\.amazonaws\.com/[a-z0-9._/-]+@sha256:[a-f0-9]{64}$ ]]
[[ $region =~ ^[a-z0-9-]+$ ]]
registry=${image%%/*}
aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$registry"
docker pull "$image"
if docker container inspect spotify-hybrid >/dev/null 2>&1; then
  docker rm -f spotify-hybrid
fi
docker run -d --name spotify-hybrid --restart unless-stopped -p 80:8000 \
  --mount type=bind,src=/opt/spotify-data,dst=/app/data/local,readonly \
  --mount type=volume,src=spotify-feedback,dst=/app/.runtime "$image"
for attempt in {1..30}; do
  if curl -fsS http://127.0.0.1/_stcore/health; then exit 0; fi
  sleep 2
done
docker logs spotify-hybrid
exit 1
