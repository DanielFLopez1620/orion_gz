# 🤖 ORION Gazebo Sim

## 🌟 Overview

Package oriented to the usage of the simulator GZ Sim (Harmonic) with the ORION robot that allows the integration of plugins for sensor and actuators, it also provides the option to use **ros2_control** with **gz_ros2_control**

## License

The source code is released under a [BSD 3-Clause license](/LICENSE).

**Author**: [Daniel Felipe López Escobar](https://github.com/DanielFLopez1620).

The orion_gz package has been tested under [ROS](https://www.ros.org/) Jazzy.

## 📚 Table of Contents

- [🚀 Launch file](#-launch-files)
- [⚙️ RViz2 Configs](#️-rviz2-configs)
- [⚙️ Params and configs](#️-params-and-configs)
- [⚠️ Troubleshooting](#️-troubleshooting)

## 🚀 Launch files

Make sure you have followed the [installation_process](/README.md) and have sourced your workspace before you continue:

### Robot State Publisher for Gazebo

Launch the robot description with the *gazebo* flag ready to mount the robot description for simulations on gz by considering the file [rsp_gz.launch.py](/orion_gz/launch/rsp_gz.launch.py). It also considers the proper replacing for using the meshes during the conversion from URDF to SDF.

~~~bash
# Basic usage:
# ros2 launch orion_gz rsp_gz.launch.py
# Additional arguments:
#   camera : Can be 'astra_s', 'a010' or 'os30a'.
#   gazebo : Boolean (true/false) to indicate the usage of gazebo tags.
#   g_mov : Boolean (true/false) to use g_mov module when using 'a010' depth cam.
#   rasp : Whether to use 'rpi4' or 'rpi5', this will imply a change in the sound hardware.
#   ros_bridge : Boolean (true/false) to indicate the usage of the bridge for the clock
#   servo : Boolean (true/false) to indicate if use servo arms
#   simplified : Whether to use or not a simplified version of the URDF with less elements.   
ros2 launch orion_gz rsp_gz.launch.py camera:=a010
~~~

The reason why there are two **robot_state_publishers** is due to the specific management of meshes in GZ, as it is required to provide the file path, making it dependable on a fixed path, so this may lead to the meshes not working if you are using another machine. Therefore, the two options of robot state publisher were separated, one is present in **orion_description** and the other one is present here.

### Spawn robot

Spawn the robot in a given world of the simulator GZ Sim by considering the [spawn_robot.launch.py](/orion_gz/launch/spawn_robot.launch.py) file, which also loads the configurations from the **orion_description** package.

~~~bash
# Basic usage:
# ros2 launch orion_gz spawn_robot.launch.py
# Additional arguments:
#   camera : Can be 'astra_s', 'a010' or 'os30a'.
#   gazebo : Boolean (true/false) to indicate the usage of gazebo tags.
#   g_mov : Boolean (true/false) to use g_mov module when using 'a010' depth cam.
#   rasp : Whether to use 'rpi4' or 'rpi5', this will imply a change in the sound hardware.
#   ros_bridge : Boolean (true/false) to indicate the usage of the bridge for the clock
#   servo : Boolean (true/false) to indicate if use servo arms
#   world : Name of the world (Gz or custom present in GZ package) to launch with the simulator.
#   x : Float value of the position X of the robot
#   y : Float value of the position Y of the robot
#   z : Float value of the position Z of the robot
#   R : Float value of the Roll orientation of the robot.
#   P : Float value of the Pitch orientation of the robot.
#   Y : Float value of the Yaw orientation of the robot.
#   simplified : Whether to use or not a simplified version of the URDF with less elements.   
ros2 launch orion_gz spawn_robot.launch.py camera:=astra_s 
~~~

![spawn_robot](https://github.com/Tesis-ORION/orion_common/blob/main/docs/readmes/spawn_robot.gif)

### Gazebo launch with ROS Brige

Spawn the robot and includes the proper bridges to make possible the communication between GZ Harmonic and ROS 2 Jazzy, by using the configs provided in [model_vis.launch.py](/orion_description/launch/model_vis.launch.py) file, which also loads the configurations from the **orion_description** package.

~~~bash
# Basic usage:
# ros2 launch orion_gz gz_ros.launch.py
# Additional arguments:
#   camera : Can be 'astra_s', 'a010' or 'os30a'.
#   g_mov : Boolean (true/false) to use g_mov module when using 'a010' depth cam.
#   rasp : Whether to use 'rpi4' or 'rpi5', this will imply a change in the sound hardware.
#   servo : Boolean (true/false) to indicate if use servo arms
#   world : Name of the world (Gz or custom present in GZ package) to launch with the simulator.
#   x : Float value of the position X of the robot
#   y : Float value of the position Y of the robot
#   z : Float value of the position Z of the robot
#   R : Float value of the Roll orientation of the robot.
#   P : Float value of the Pitch orientation of the robot.
#   Y : Float value of the Yaw orientation of the robot.
#   simplified : Whether to use or not a simplified version of the URDF with less elements.    
ros2 launch orion_gz gz_ros.launch.py rasp:=rpi5 camera:=os30a
~~~

![gz_ros_launch](https://github.com/Tesis-ORION/orion_common/blob/main/docs/readmes/gz_ros.gif)

### Gazebo launch with ros2_control

Spawn the robto and includes the configuration of bridges for sensors while also connecting the actuatores (servos and motors) with the proper ros2_control interface in order to interact with them. It considers a differential driver controller for the DC motors and forward controllers for the servo motors. For more information, check the file [gz_ros2_control.launch.py](/orion_gz/launch/gz_ros2_control.launch.py)

~~~bash
# Basic usage:
# ros2 launch orion_gz gz_ros2_control.launch.py
# Additional arguments:
#   camera : Can be 'astra_s', 'a010' or 'os30a'.
#   g_mov : Boolean (true/false) to use g_mov module when using 'a010' depth cam.
#   rasp : Whether to use 'rpi4' or 'rpi5', this will imply a change in the sound hardware.
#   servo : Boolean (true/false) to indicate if use servo arms
#   world : Name of the world (Gz or custom present in GZ package) to launch with the simulator.
#   x : Float value of the position X of the robot
#   y : Float value of the position Y of the robot
#   z : Float value of the position Z of the robot
#   R : Float value of the Roll orientation of the robot.
#   P : Float value of the Pitch orientation of the robot.
#   Y : Float value of the Yaw orientation of the robot.
#   simplified : Whether to use or not a simplified version of the URDF with less elements.    
ros2 launch orion_gz gz_ros2_control.launch.py rasp:=rpi4 camera:=os30a
~~~

![gz_ros2_control_launch](https://github.com/Tesis-ORION/orion_common/blob/main/docs/readmes/gz_ros2_control.gif)

## ⚙️ RViz2 Configs

### vis_a010.rviz

This config will allow the set up for visualizing the Depth Camera A010 (depth image) and also a Pi Cam (color image), while also displaying the robot model, LIDAR information and tfs focused on the odom view.

### vis_astra.rviz

This config will allow the set up for visualizing the RGBD ORBBEC ASTRA S considering color, depth and cloud image; while also displaying the robot model, LIDAR information and tfs focused on the odom view.

### vis_os30a.rviz

This config will allow the set up for visualizing the Depth Camera OS30A considering color, depth and cloud image; while also displaying the robot model, LIDAR information and tfs focused on the odom view.

### visualization.rviz

Simple visualization of the robot state and sensors with a focus on the base_link of the robot.

## ⚙️ Params and configs

### a010_bridge.yaml

Contains the params to do the bridge to publish, from GZ to ROS 2, the depth image, camera info and point cloud of the A010 in simulation.

### astra_bridge.yaml

Contains the elements to make the bridge to publish, from GZ to ROS 2, the camera image, depth image, camera info and point cloud of the Astra S in simulation.

### base_bridge.yaml

Containts the element to exchange the information of the base simulation of the robot. On one hand, from ROS to GZ, the cmd_vel topic. On the other hand, from GZ to ROS, the TF tree, the odom, the joint_states and the scan of the LIDAR.

### g_mov_bridge.yaml

Presents the information to publish from ROS to GZ in the case of the G_Mov servo, and also to publish from GZ to ROS the info of the PI Cam (image and camera info) and the IMU.

### g_mov_short_bridge.yaml

Contains information to just use the Pi cam of the simualted version of the G-Mov module.

### os30a_bridge.yaml

Contains the elements to make the bridge to publish, from GZ to ROS 2, the camera image, depth image, camera info and point cloud of the OS30A in simulation.

### ros2_ctl_extra_bridge.yaml

Param bridge intended to be used when having **ros2_control** so you can access the TF tree additions coming from the controllers while also getting access to the joint states and the LIDAR scan.

### servo_bridge.yaml

Focused on the commands from ROS to GZ of the arms' servos when using native GZ plugins on the simulation.

## 🗒️ Additional comments

- By default, the **rgdb** and **depth** cameras' **point clouds** were disabled due to high overload and slow the processing of the simulation. If you want to activate them, go to the [config](/orion_gz/config/) dir, search for the .yaml file of the camera you want to use and uncomment the point cloud arg.

## ⚠️ Troubleshooting

### Slow simulation

This may depend on your machine resources, as ORION contains multiple plugins for sensors and actuators with a full definition model, it may run slow sometimes. In those cases, you can implement the next solutions:

- Use the simplified version of the robot, as it will ignore the meshes, links and joinst of inner parts. Keep in mind that this may affect the physic simulation.

    ~~~bash
    ros2 launch gz_ros2_control.launch.py simplified:=true
    ~~~

- Delete the logs of the simulator, as this may be slowing down your system.

    ~~~bash
    sudo rm ./.gz/sim/log/*
    ~~~

- Check that GZ Sim is using your GPU card (if you have one).

- If you do not require depth image, you can comment the brigde, similar to what was suggested on the **Additional notes section**.
