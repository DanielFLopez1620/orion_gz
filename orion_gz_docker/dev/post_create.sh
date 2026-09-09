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
# The depth_* and ldlidar_component keys are source packages required by
# orion_bringup (real robot only). They are not cloned into this simulation
# workspace, so rosdep cannot resolve them — skip them and exclude
# orion_bringup from the build below.
rosdep install --from-paths src --ignore-src -y \
    --skip-keys="sounddevice webrtcvad python3-sounddevice pytest depth_maixsense_a010 depth_ydlidar_os30a ldlidar_component"

echo "Done. Build the workspace with:"
echo "  cd ${WS_ROOT} && colcon build --symlink-install --packages-ignore orion_bringup orion"
echo ""
echo "NOTE: orion_bringup (real robot) and orion (metapackage depending on it)"
echo "      must be ignored — they need the physical sensor drivers, which are"
echo "      not part of this simulation workspace."
