# ORION GZ Docker

Containerized environment for working on the ORION Gazebo Harmonic simulation
stack with ROS 2 Jazzy. The image is a thin layer on top of `orion_dev:latest`
(from the [orion_common](https://github.com/DanielFLopez1620/orion_common)
repository), which already bundles Gazebo Harmonic, RViz2, Nav2, SLAM Toolbox,
`gz_ros2_control`, and the rest of the ORION development tooling.

---

## Architecture

```plaintext
osrf/ros:jazzy-ros-base       (upstream)
        │
        ▼
  orion_base:latest           (built from orion_common/orion_docker/base)
        │
        ▼
  orion_dev:latest            (built from orion_common/orion_docker/dev)
        │
        ▼
  orion_gz_dev (this image)   (FROM orion_dev:latest — minimal layer)
```

The image does **not** duplicate any of the dependencies already installed in
`orion_dev:latest`. It exists so a developer working primarily on simulation
can open the `orion_gz` repository as the devcontainer workspace (instead of
opening `orion_common` and treating `orion_gz` as a clone).

---

## Prerequisites

- [Docker Engine](https://docs.docker.com/engine/install/ubuntu/)
- [VS Code](https://code.visualstudio.com/) with the
  [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  and [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
  extensions
- `orion_base:latest` and `orion_dev:latest` images already built from
  [orion_common](https://github.com/DanielFLopez1620/orion_common). Follow the
  instructions in
  [orion_common/orion_docker/README.md](https://github.com/DanielFLopez1620/orion_common/blob/main/orion_docker/README.md)
  for the first two layers.

Quick reminder of the parent build steps:

```bash
git clone https://github.com/DanielFLopez1620/orion_common.git
cd orion_common
docker build -t orion_base:latest orion_docker/base/
docker build -t orion_dev:latest  orion_docker/dev/
```

---

## Host setup (run once)

X11 display forwarding for RViz2 and Gazebo:

```bash
xhost +local:docker
# To apply automatically on login:
# echo "xhost +local:docker" >> ~/.profile
```

---

## Open in VS Code

The repository ships a `.devcontainer/` symlink at the root pointing to
`orion_gz_docker/dev/`. To start the container:

1. Clone this repository:

   ```bash
   git clone https://github.com/DanielFLopez1620/orion_gz.git
   cd orion_gz
   ```

2. Open the **repository root** (not a subdirectory) in VS Code:

   ```bash
   code .
   ```

3. Run the command palette action `Dev Containers: Reopen in Container`
   (`Ctrl + Shift + P`).

VS Code will build the local image (instant after the first build — it only
adds a marker layer on top of `orion_dev:latest`) and run
[`post_create.sh`](dev/post_create.sh), which:

- Clones `orion_common` into `~/ws/src/` (see [`repos.yaml`](dev/repos.yaml))
- Runs `rosdep install` for any remaining dependencies

---

## Build the workspace

Once the container is running and `post_create.sh` has finished:

```bash
cd ~/ws
colcon build --symlink-install --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
source install/setup.bash
```

The `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` flag generates `compile_commands.json`,
enabling full C++ IntelliSense in VS Code.

---

## Run the simulation

After building, the standard launch entry points work as usual:

```bash
# Robot State Publisher only
ros2 launch orion_gz rsp_gz.launch.py camera:=os30a

# Gazebo + bridges
ros2 launch orion_gz gz_ros.launch.py camera:=os30a servo:=true

# Gazebo + ros2_control
ros2 launch orion_gz gz_ros2_control.launch.py camera:=os30a servo:=true
```

See [orion_gz/README.md](../orion_gz/README.md) for the full launch surface.

---

## Directory layout

```plaintext
orion_gz_docker/
└── dev/
    ├── Dockerfile          ← thin layer on top of orion_dev:latest
    ├── devcontainer.json   ← VS Code devcontainer config
    ├── repos.yaml          ← external repos cloned by post_create.sh
    └── post_create.sh      ← workspace setup script
```

The `.devcontainer/` directory at the repository root is a symlink to
`orion_gz_docker/dev/`.

---

## ROS_DOMAIN_ID

The container sets `ROS_DOMAIN_ID=16` to keep simulation traffic isolated from
a real-robot stack (which uses `ROS_DOMAIN_ID=0` for the micro-ROS agent) if
both are running on the same host. Override it in
[`devcontainer.json`](dev/devcontainer.json) under `containerEnv` if you need a
different value.

---

## GPU support

`--gpus all` is left commented out in [`devcontainer.json`](dev/devcontainer.json).
To enable it, install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
on the host and uncomment the flag.

---

## Troubleshooting

### `Authorization required` when launching RViz2 or Gazebo

Run `xhost +local:docker` on the host.

### `fatal: detected dubious ownership` in git

The container changed file ownership on the bind-mounted directory. Fix with:

```bash
sudo chown -R $USER:$USER /path/to/orion_gz
```

### `orion_dev:latest: pull access denied` during build

The parent image is **not** on Docker Hub — it has to be built locally from
`orion_common`. See [Prerequisites](#prerequisites).

### Slow simulation

See the troubleshooting section in
[orion_gz/README.md](../orion_gz/README.md#-troubleshooting).
