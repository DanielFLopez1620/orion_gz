FROM orion_gz:latest

# Inherit username from the parent image (orion_user, UID 1001).
# Override at build time with --build-arg if you used a custom value in orion_base.
ARG USERNAME=orion_user

# orion_gz (base layer) already provides:
#   - Everything from orion_dev (ROS 2 dev environment)
#   - Gazebo Harmonic + ROS 2 bridges (ros-gz-sim, ros-gz-bridge)
#   - ROS 2 control + gz-ros2-control
#   - URDF/xacro tools
#
# This dev layer exists so a separate devcontainer can be opened from orion_gz/
# without conflicting with the orion_common bind-mount. Add simulation-only
# development tools here if needed (none required as of 1.8.x).

USER $USERNAME

WORKDIR /home/${USERNAME}/ws

CMD ["/bin/bash"]
