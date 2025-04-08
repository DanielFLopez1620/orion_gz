# ORION Gazebo Sim

## Overview

Package oriented to the basic usage of the ORION project, a ROS 2 differential robot oriented for Human-Robot Interaction applications.

**Keywords:** ROS 2, Differential, HRI, ROS 2 Jazzy, low-cost.

## License

The source code is released under a [BSD 3-Clause license](/LICENSE).

**Authors**: Daniel Felipe López Escobar, Miguel Ángel Gonzalez Rodriguez and Alejandro Bermudez.

The ORION Common packages have been tested under [ROS](https://www.ros.org/) Jazzy.

## Package summary

- **[orion_gz](/orion_gz/README.md):** Package for simulation of the robot in GZ Sim.

## Installation

1. Follow the installation steps of **[ORION Commons](https://github.com/Tesis-ORION/orion_common/blob/dev/README.md)** as they are required for the simulation.

2. Clone this repository:

    ~~~bash
    cd ~/ros2_ws/src
    # For now, the project is in the development branch
    git clone -b https://github.com/Tesis-ORION/orion_gz.git
    ~~~

3. Install the dependencies:

    ~~~bash
    cd ~/ros2_ws
    git clone rosdep install --from-paths src --ignore-src -r -y
    ~~~

4. Build the simulation package.

    ~~~bash
    cd ~/ros2_ws
    colcon build --symlink-install --packages-select orion_gz
    source install/setup.bash
    ~~~

5. You are redy to explore the packages

**NOTE:** Do not build the plugins along the ROS Packages as they may lead to build errors.
