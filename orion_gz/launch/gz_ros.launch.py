import os
import yaml

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

from nav2_common.launch import ReplaceString   


def generate_launch_description():
    # ------------------------ Paths definitions ----------------------------
    pkg_gz = get_package_share_directory('orion_gz')
    spawn_file = os.path.join(pkg_gz, 'launch', 'spawn_robot.launch.py')
    bridge_config_file_path = os.path.join(pkg_gz, 'config', 
        'ros_gz_bridge.yaml')

    # --------------------------- Configurations -----------------------------
    camera = LaunchConfiguration('camera')
    servo = LaunchConfiguration('servo')
    g_mov = LaunchConfiguration('g_mov')
    rasp = LaunchConfiguration('rasp')
    world = LaunchConfiguration('world')
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    roll = LaunchConfiguration('R')
    pitch = LaunchConfiguration('P')
    yaw = LaunchConfiguration('Y')

    # -------------------------- Launch arguments -----------------------------
    camera_arg = DeclareLaunchArgument(
        'camera',
        default_value='a010',
        description="Choose a cam for the robot (os30a, astra_s, a010)"
    )

    use_servo_arg = DeclareLaunchArgument(
        'servo',
        default_value='true',
        description="Boolean to include or not the servos"
    )

    use_g_mov_arg = DeclareLaunchArgument(
        'g_mov',
        default_value='true',
        description="When using camera a010, whether to include or not G Mov"
    )
    
    rasp_arg = DeclareLaunchArgument(
        'rasp',
        default_value='rpi5',
        description="Select 4 for Raspberry Pi 4B, or 5 for Raspberry Pi 5"
    )

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='Specify the world file for Gazebo'
    )

    x_arg = DeclareLaunchArgument(
        'x', 
        default_value='0.0', 
        description='Initial X position'
    )

    y_arg = DeclareLaunchArgument(
        'y',
        default_value='0.0',
        description='Initial Y position'
    )

    z_arg = DeclareLaunchArgument(
        'z',
        default_value='0.5',
        description='Initial Z position'
    )

    roll_arg = DeclareLaunchArgument(
        'R',
        default_value='0.0',
        description='Initial Roll'
    )

    pitch_arg = DeclareLaunchArgument(
        'P',
        default_value='0.0',
        description='Initial Pitch'
    )

    yaw_arg = DeclareLaunchArgument(
        'Y',
        default_value='0.0',
        description='Initial Yaw'
    )

    # ------------------------ Additional setups -------------------------------
    bridge_config = ReplaceString(
       source_file=bridge_config_file_path,
       replacements={'<entity>': 'orion'},
   )


    # -------------------------- Includes --------------------------------------
    spawn_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(spawn_file),
        launch_arguments= {"camera": camera, "servo": servo,
                            "g_mov": g_mov, "rasp": rasp,
                            "x": x, "y": y, "z": z,
                            "roll": roll, "pitch": pitch, 
                            "yaw": yaw}.items(),
    )
    # ------------------------ Nodes --------------------------------------------
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': bridge_config
        }],
        output='screen',
    )


    # -------------------------- Nodes ----------------------------------------
    return LaunchDescription([
        camera_arg,
        use_servo_arg,
        use_g_mov_arg,
        rasp_arg,
        world_arg,
        x_arg,
        y_arg,
        z_arg,
        roll_arg,
        pitch_arg,
        yaw_arg,
        spawn_include,
        bridge_node,
    ])