# 🤖 ORION Gazebo Sim

![orion_gz_demo](/orion_gz/resources/orion_gz_demo.gif)

## 🌟 Overview

Package oriented to the simulation of the ORION project, a ROS 2 differential robot oriented for Human-Robot Interaction applications, in Gazebo Sim Harmonic.

**Keywords:** ROS 2, Differential, HRI, ROS 2 Jazzy, low-cost.

## 📝 License

The source code is released under a [BSD 3-Clause license](/LICENSE).

**Authors**: Daniel Felipe López Escobar, Miguel Ángel Gonzalez Rodriguez and Alejandro Bermudez.

The ORION Common packages have been tested under [ROS](https://www.ros.org/) Jazzy.

---

## 📚 Table of Contents

- [📦 Package summary](#-package-summary)
- [📥 Installation](#-installation)
- [⚠️ Troubleshooting](#️-troubleshooting)

---

## 📦 Package summary

- **[orion_gz](/orion_gz/README.md):** Package for simulation of the robot in GZ Sim so you can use GZ plugins, gz_ros2_control, ros_gz_bridges and custom worlds to use a simulated version of ORION.

    ![orion_gz_packages](/orion_gz/resources/orion_gz_packages.gif)

## 📥 Installation

1. Follow the installation steps of **[ORION Commons](https://github.com/DanielFLopez1620/orion_common)** as they are required for the simulation.

2. Clone this repository:

    ~~~bash
    cd ~/ros2_ws/src
    git clone https://github.com/DanielFLopez1620/orion_gz.git
    ~~~

3. Install the dependencies:

    ~~~bash
    cd ~/ros2_ws
    rosdep install --from-paths src --ignore-src -r -y
    ~~~

4. Build the simulation package.

    ~~~bash
    cd ~/ros2_ws
    colcon build --symlink-install --packages-select orion_gz
    source install/setup.bash
    ~~~

5. You are ready to explore the packages of this repository.

## ⚠️ Troubleshooting

Explore the packages content as each README may contain some easy tips on how to solve some common problems.
