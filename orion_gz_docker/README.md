# ORION GZ Docker Setup

This directory contains Docker and DevContainer configurations for the Gazebo Harmonic simulation environment.

## Image Hierarchy

```plaintext
orion_base (from orion_common)
    ↓
orion_dev (from orion_common)
    ↓
orion_gz (GZ-specific layer — this repo)
    ↓
orion_gz:dev (devcontainer)
```

### Image Descriptions

| Image | Purpose | Base |
| --- | --- | --- |
| **orion_base** | ROS 2 + micro-ROS + Orbbec SDK | `ros:jazzy-ros-base` |
| **orion_dev** | Development tools (RViz, cameras, audio) | `orion_base:latest` |
| **orion_gz** | Gazebo Harmonic + simulation tools | `orion_dev:latest` |
| **orion_gz:dev** | DevContainer for simulation development | `orion_gz:latest` |

## Building Images

`orion_base` and `orion_dev` come from the [orion_common repo](https://github.com/DanielFLopez1620/orion_common) and must exist before building this layer. See [orion_common/orion_docker/README.md](https://github.com/DanielFLopez1620/orion_common/blob/main/orion_docker/README.md) for those steps.

```bash
# From orion_common repo (only if the base images are not built yet)
cd ~/dev_ws/src/orion_common
docker build -t orion_base:latest orion_docker/base/
docker build -t orion_dev:latest orion_docker/dev/

# From orion_gz repo
cd ~/dev_ws/src/orion_gz
docker build -f orion_gz_docker/base/Dockerfile -t orion_gz:latest .
docker build -f orion_gz_docker/dev/Dockerfile -t orion_gz:dev .
```

Verify the chain is complete before opening the devcontainer:

```bash
docker images | grep orion
# expected: orion_base, orion_dev, orion_gz
```

> Building `orion_gz:dev` by hand is optional — VS Code builds it automatically when reopening the folder in the devcontainer.

## Host Setup

GUI applications (Gazebo, RViz2) need X11 forwarding. Run once on the host before launching them:

```bash
xhost +local:docker
```

To apply automatically on login:

```bash
echo "xhost +local:docker" >> ~/.profile
```

## DevContainer Setup

### Opening in VS Code

1. Open the `orion_gz` folder in VS Code (the repo root, not a subdirectory)
2. `Ctrl + Shift + P` → **Dev Containers: Reopen in Container**
3. VS Code builds `orion_gz:dev` and runs `post_create.sh` automatically

> After changing `devcontainer.json`, `Dockerfile` or `post_create.sh`, use **Dev Containers: Rebuild Container** instead — a plain "Reopen" may reuse a cached image.

### Key Environment Variables

- `ROS_DOMAIN_ID=16` — Keeps simulation isolated from robot hardware (which uses domain 0 for the micro-ROS agent)
- `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` — Inherited from orion_dev

### Post-Create Setup

When the container is created, `post_create.sh`:

1. Creates workspace directories (`build/`, `install/`, `log/`) and fixes their ownership
2. Imports external repositories (defined in `repos.yaml`)
3. Resolves ROS dependencies via `rosdep`, skipping the physical sensor driver keys (see below)

The script is re-runnable — if it fails partway, fix the cause and run it again instead of rebuilding the container:

```bash
bash ~/ws/src/orion_gz/orion_gz_docker/dev/post_create.sh
```

### Building the workspace

> **Important:** `orion_bringup` and `orion` must be excluded from the build.

```bash
cd ~/ws
colcon build --symlink-install --packages-ignore orion_bringup orion
```

`orion_common` brings `orion_bringup` into the workspace, and it depends on three
physical sensor driver packages — `depth_maixsense_a010`, `depth_ydlidar_os30a`
and `ldlidar_component` — which are **not** cloned into this simulation
workspace. The metapackage `orion` depends on `orion_bringup`, so it fails for
the same reason and must be ignored too.

This is intentional: `orion_bringup` starts the **real robot**, while the
simulation is launched from `orion_gz`. Keeping the drivers out avoids compiling
hardware code (notably `depth_ydlidar_os30a`, which ships a prebuilt `libeSPDI`)
that the simulation never uses.

For full IntelliSense support in VS Code, add the compile commands flag:

```bash
colcon build --symlink-install --packages-ignore orion_bringup orion \
    --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

Then source the workspace:

```bash
source ~/ws/install/setup.bash
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

- **orion_gz does NOT include**: Nav2, SLAM, trajectory planning (see [orion_tools](https://github.com/Tesis-ORION/orion_tools) for those)
- **orion_gz does NOT rebuild** dev tools from orion_dev (RViz, camera drivers, etc.) — inherited as-is
- **orion_gz does NOT include** the physical sensor drivers — the cameras and lidar are simulated inside Gazebo, and the `a010`/`os30a` names in `config/*_bridge.yaml` are simulated topics, not the real drivers
- Each layer is independently cacheable during builds

## Repository Configuration

The `repos.yaml` in the devcontainer defines which packages are imported:

```yaml
repositories:
  # orion_gz is NOT listed — bind-mounted live by the devcontainer
  orion_common:
    url: https://github.com/DanielFLopez1620/orion_common.git
    version: main
```

Unlike the orion_common devcontainer, the physical sensor drivers are
deliberately absent here. This keeps the simulation workspace light, at the cost
of excluding `orion_bringup` and `orion` from the build.

## Differences from the orion_common devcontainer

| Aspect | orion_common | orion_gz |
| --- | --- | --- |
| `ROS_DOMAIN_ID` | 0 (micro-ROS agent) | 16 (isolated from hardware) |
| `/dev` mount | full `/dev` (ESP32, LIDAR, I2C) | `/dev/dri` only (GPU rendering) |
| Sensor drivers | cloned via `repos.yaml` | not cloned |
| `orion_bringup` | builds | excluded |

The `/dev` difference matters: this container **cannot see** ESP32s, LIDAR or
physical cameras. Use the orion_common devcontainer for hardware work.

## Troubleshooting

### `Cannot locate rosdep definition for [depth_maixsense_a010 / depth_ydlidar_os30a / ldlidar_component]`

`post_create.sh` skips these keys. If you see this, the script ran with an older
version of itself — re-run it:

```bash
bash ~/ws/src/orion_gz/orion_gz_docker/dev/post_create.sh
```

### `Could not find a package configuration file provided by "depth_maixsense_a010"` during colcon build

The `--packages-ignore orion_bringup orion` flags are missing. `--skip-keys`
only silences rosdep; colcon still tries to build `orion_bringup`. Clean the
partial artifacts and rebuild:

```bash
rm -rf ~/ws/build/orion_bringup ~/ws/install/orion_bringup \
       ~/ws/build/orion ~/ws/install/orion
cd ~/ws && colcon build --symlink-install --packages-ignore orion_bringup orion
```

### `Authorization required` when launching Gazebo or RViz2

Run `xhost +local:docker` on the host. See [Host Setup](#host-setup).

### `failed to discover GPU vendor from CDI`

The `--gpus all` flag needs the NVIDIA Container Toolkit with CDI configured. It
is commented out by default in `dev/devcontainer.json`.

### `fatal: detected dubious ownership` in git

The container changed ownership on the bind-mounted directory. On the host:

```bash
sudo chown -R $USER:$USER ~/dev_ws/src/orion_gz
```

## Directory structure

```plaintext
orion_gz_docker/
├── base/
│   ├── Dockerfile          ← simulation layer (inherits orion_dev)
│   └── .dockerignore
├── dev/
│   ├── Dockerfile          ← devcontainer image (inherits orion_gz)
│   ├── devcontainer.json   ← VS Code devcontainer config
│   ├── repos.yaml          ← external repos cloned at container start
│   ├── post_create.sh      ← workspace setup script
│   └── .dockerignore
└── README.md
```

> `.devcontainer/` at the repo root is a symlink to `orion_gz_docker/dev/`.
