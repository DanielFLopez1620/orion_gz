# ORION GZ Docker Setup

This directory contains Docker and DevContainer configurations for the Gazebo Harmonic simulation environment.

## Image Hierarchy

```
orion_base (from orion_common)
    ↓
orion_dev (from orion_common)
    ↓
orion_gz (GZ-specific layer - this repo)
    ↓
orion_gz:dev (devcontainer)
```

### Image Descriptions

| Image | Purpose | Base |
|-------|---------|------|
| **orion_base** | ROS 2 + micro-ROS + Orbbec SDK | `ros:jazzy-ros-base` |
| **orion_dev** | Development tools (RViz, cameras, audio) | `orion_base:latest` |
| **orion_gz** | Gazebo Harmonic + simulation tools | `orion_dev:latest` |
| **orion_gz:dev** | DevContainer for simulation development | `orion_gz:latest` |

## Building Images

### Option 1: Build Everything from Scratch

```bash
# From orion_common repo
cd ~/dev_ws/src/orion_common
docker build -f orion_docker/base/Dockerfile -t orion_base:latest .
docker build -f orion_docker/dev/Dockerfile -t orion_dev:latest .

# From orion_gz repo
cd ~/dev_ws/src/orion_gz
docker build -f orion_gz_docker/base/Dockerfile -t orion_gz:latest .
docker build -f orion_gz_docker/dev/Dockerfile -t orion_gz:dev .
```

### Option 2: Using Docker Compose (Recommended)

If a `docker-compose.yml` is available at the workspace root, simply run:

```bash
docker compose build --no-cache
```

## DevContainer Setup

### Opening in VS Code

1. Open the orion_gz folder in VS Code
2. Click **Remote Container** icon → **Reopen in Container**
3. VS Code will automatically build the `orion_gz:dev` image

### Key Environment Variables

- `ROS_DOMAIN_ID=16` — Keeps simulation isolated from robot hardware (which uses domain 0)
- `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` — Inherited from orion_dev

### Post-Create Setup

When the container starts:
1. Creates workspace directories (`build/`, `install/`, `log/`)
2. Imports external repositories (defined in `repos.yaml`)
3. Installs ROS dependencies via `rosdep`

To build the workspace after container creation:

```bash
cd ~/ws
colcon build --symlink-install
```

## What's Included

### In `orion_gz` layer

- **Gazebo Harmonic**
  - `ros-jazzy-ros-gz` — Gazebo + ROS 2 integration
  - `ros-jazzy-ros-gz-sim` — Gazebo simulator
  - `ros-jazzy-ros-gz-bridge` — Topic/service bridge
  - `ros-jazzy-ros-gz-image` — Image transport support

- **Simulation Control**
  - `ros-jazzy-gz-ros2-control` — Gazebo + ros2_control integration
  - `ros-jazzy-xacro` — URDF macro processor
  - `ros-jazzy-urdfdom-py` — Python URDF utilities

## Notes

- **orion_gz does NOT include**: Nav2, SLAM, trajectory planning (see orion_tools for those)
- **orion_gz does NOT rebuild** dev tools from orion_dev (RViz, camera drivers, etc.) — inherited as-is
- Each layer is independently cacheable during builds

## Repository Configuration

The `repos.yaml` in the devcontainer defines which packages are imported:

```yaml
repositories:
  orion_gz:  # Not listed — bind-mounted by devcontainer
  orion_common:  # Imported from GitHub
    url: https://github.com/DanielFLopez1620/orion_common.git
    version: main
```

This ensures the simulation environment has access to common utilities while keeping orion_gz isolated for development.
