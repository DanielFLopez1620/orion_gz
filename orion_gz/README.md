# orion_gz

## Overview

Package oriented to the usage of the simulator GZ Sim (Harmonic) with the ORION robot.

## License

The source code is released under a [BSD 3-Clause license](/LICENSE).

**Author**: [Daniel Felipe López Escobar](https://github.com/DanielFLopez1620).

The orion_gz package has been tested under [ROS](https://www.ros.org/) Jazzy.

## Usage

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

## Additional comments

- By default, the **rgdb** and **depth** cameras' **point clouds** were disabled due to high overload and slow the processing of the simulation. If you want to activate them, go to the [config](/orion_gz/config/) dir, search for the .yaml file of the camera you want to use and uncomment the point cloud arg.
