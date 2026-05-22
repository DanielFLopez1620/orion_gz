FROM orion_dev:latest

# Inherit username from the parent image (orion_user, UID 1001).
# Override at build time with --build-arg if you used a custom value in orion_base.
ARG USERNAME=orion_user

# orion_dev already provides everything the simulation stack needs:
#   - ros-${ROS_DISTRO}-ros-gz  (Gazebo Harmonic + bridge)
#   - ros-${ROS_DISTRO}-rviz2
#   - ros-${ROS_DISTRO}-gz-ros2-control
#   - ros-${ROS_DISTRO}-joint-state-publisher-gui
#   - Nav2, SLAM Toolbox, Cartographer
#   - ros2_control, ros2_controllers, xacro
#
# This layer exists so a separate devcontainer can be opened from orion_gz/
# without conflicting with the orion_common bind-mount. Add simulation-only
# tooling here if it appears (none required as of 1.8.x).

USER $USERNAME

WORKDIR /home/${USERNAME}/ws

CMD ["/bin/bash"]
