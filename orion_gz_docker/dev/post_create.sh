#!/bin/bash
# post_create.sh
# Runs once when the devcontainer is created. Imports external repos and
# resolves rosdep dependencies. Mirrors the flow of orion_common/orion_docker
# but with orion_gz as the bind-mounted package.

set -e

WS_ROOT="/home/orion_user/ws"
REPOS_YAML="${WS_ROOT}/src/orion_gz/orion_gz_docker/dev/repos.yaml"

# Fix ownership only on non-bind-mounted workspace dirs (build, install, log).
sudo mkdir -p "${WS_ROOT}/build" "${WS_ROOT}/install" "${WS_ROOT}/log"
sudo chown -R orion_user:orion_user \
    "${WS_ROOT}/build" \
    "${WS_ROOT}/install" \
    "${WS_ROOT}/log"

echo "Importing repositories into ${WS_ROOT}/src ..."
cd "${WS_ROOT}"
vcs import src < "${REPOS_YAML}"

echo "Running rosdep..."
rosdep update
sudo apt-get update
rosdep install --from-paths src --ignore-src -y \
    --skip-keys="sounddevice webrtcvad python3-sounddevice pytest"

echo "Done. Build the workspace with:"
echo "  cd ${WS_ROOT} && colcon build --symlink-install"
