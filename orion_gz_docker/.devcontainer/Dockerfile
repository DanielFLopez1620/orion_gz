FROM docker.io/osrf/ros:jazzy-desktop-full

ARG USER_NAME=orion
ARG USER_UID=1010
ARG USER_GID=1010

RUN groupadd --gid $USER_GID $USER_NAME && \
    useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USER_NAME && \
    apt-get update && \
    apt-get install -y sudo && \
    usermod -aG sudo $USER_NAME && \
    echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME && \
    chmod 0440 /etc/sudoers.d/$USER_NAME

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-pip python3-setuptools python3-vcstool \ 
    apt-utils bash-completion \
    curl wget software-properties-common

    RUN apt-get update && apt-get install -y \
    python3-opencv \
    python3-venv \
    ffmpeg \
    protobuf-compiler \
    libprotobuf-dev \
    cmake \
    libopencv-dev \
    git \
    && apt-get clean

# Install MediaPipe
RUN pip3 install mediapipe --break-system-packages

ENV SHELL=/bin/bash

RUN colcon mixin remove default
RUN colcon mixin add default https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml
RUN colcon mixin update default

RUN apt-get update && apt-get install -y python3-colcon-common-extensions python3-colcon-mixin

RUN apt-get update && apt-get install -y ros-$ROS_DISTRO-rmw-cyclonedds-cpp

RUN apt-get update && apt-get install -y ros-$ROS_DISTRO-ros-gz


COPY repos.yaml /home/$USER_NAME/ws/repos.yaml

USER $USER_NAME

RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/$USER_NAME/.bashrc
RUN echo "source /home/orion/ws/install/setup.bash || echo 'Workspace not Ready. Run colcon build at /home/orion/ws'" >> /home/$USER_NAME/.bashrc
RUN echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> /home/$USER_NAME/.bashrc

RUN sudo apt update && sudo apt upgrade -y

WORKDIR /home/$USER_NAME/ws

CMD ["/bin/bash"]