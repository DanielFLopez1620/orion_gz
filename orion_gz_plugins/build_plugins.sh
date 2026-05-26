#!/usr/bin/env bash
# Build script for orion_gz_plugins.
# Run from anywhere; it always resolves the workspace root automatically.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"   # dev_ws

# ── Source ROS 2 Jazzy ────────────────────────────────────────────────────────
if [[ -z "${ROS_DISTRO}" ]]; then
    source /opt/ros/jazzy/setup.bash
fi

echo "==> Workspace : ${WS_ROOT}"
echo "==> ROS distro: ${ROS_DISTRO}"

# ── Build ─────────────────────────────────────────────────────────────────────
cd "${WS_ROOT}"
colcon build \
    --packages-select orion_gz_plugins \
    --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo

# ── Source install ────────────────────────────────────────────────────────────
source "${WS_ROOT}/install/setup.bash"

echo ""
echo "==> Build complete."
echo "    Libraries : ${WS_ROOT}/install/orion_gz_plugins/lib/"
echo "    Textures  : ${WS_ROOT}/install/orion_gz_plugins/share/orion_gz_plugins/textures/"
echo "    SDF model : ${WS_ROOT}/install/orion_gz_plugins/share/orion_gz_plugins/models/"
echo ""
echo "    Before running GZ, export:"
echo "      export GZ_GUI_PLUGIN_PATH=\${WS_ROOT}/install/orion_gz_plugins/lib:\$GZ_GUI_PLUGIN_PATH"
echo "      export GZ_SIM_RESOURCE_PATH=\${WS_ROOT}/install/orion_gz_plugins/share/orion_gz_plugins/models:\$GZ_SIM_RESOURCE_PATH"
echo ""
echo "    Launch demo:"
echo "      gz sim \${WS_ROOT}/install/orion_gz_plugins/share/orion_gz_plugins/models/orion_demo.sdf"
