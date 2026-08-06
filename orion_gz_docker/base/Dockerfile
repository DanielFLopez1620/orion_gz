# ============================================================================
# Gazebo Harmonic Simulation Layer
# Inherits from orion_dev (which includes ROS 2, development tools, etc.)
# Adds only simulation-specific packages (Gazebo + ROS 2 bridges)
# ============================================================================
FROM orion_dev:latest

ARG USERNAME=orion_user

USER root

# ---- Gazebo Harmonic simulation stack (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # ---- Gazebo and ROS 2 integration
    ros-${ROS_DISTRO}-ros-gz \
    ros-${ROS_DISTRO}-ros-gz-sim \
    ros-${ROS_DISTRO}-ros-gz-bridge \
    ros-${ROS_DISTRO}-ros-gz-image \
    # ---- ROS 2 control with Gazebo
    ros-${ROS_DISTRO}-gz-ros2-control \
    # ---- URDF and xacro (simulation description)
    ros-${ROS_DISTRO}-xacro \
    ros-${ROS_DISTRO}-urdfdom-py \
    && rm -rf /var/lib/apt/lists/*

USER $USERNAME

WORKDIR /home/${USERNAME}/ws

CMD ["/bin/bash"]
