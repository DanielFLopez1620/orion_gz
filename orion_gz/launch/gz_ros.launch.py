# ///////////////////////////// REQUIRED LIBRARIES //////////////////////////////
# .............................. Python libraries ...............................
import os

# ............................ Launch dependencies .............................
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

# ........................... Additional packages dependencies ..................
from nav2_common.launch import ReplaceString   

# //////////////////////////// GLOBAL DEFINITIONS //////////////////////////////
ARGS = [
    DeclareLaunchArgument('camera', default_value='a010',
        description="Choose a cam for the robot (os30a, astra_s, a010)"),
    DeclareLaunchArgument('servo',default_value='true',
        description="Boolean to include or not the servos"),
    DeclareLaunchArgument('g_mov',default_value='true',
        description="When using camera a010, whether to include or not G Mov"),
    DeclareLaunchArgument('rasp', default_value='rpi5',
        description="Select 4 for Raspberry Pi 4B, or 5 for Raspberry Pi 5"),
    DeclareLaunchArgument('gazebo',default_value='true',
        description="True for using gazebo tags, false otherwise"),
    DeclareLaunchArgument('world', default_value='empty.sdf',
        description='Specify the world file for Gazebo'),
    DeclareLaunchArgument('x', default_value='0.0', 
        description='Initial X position'),
    DeclareLaunchArgument('y', default_value='0.0',
        description='Initial Y position'),
    DeclareLaunchArgument('z', default_value='0.5',
        description='Initial Z position'),
    DeclareLaunchArgument('R', default_value='0.0',
        description='Initial Roll'),
    DeclareLaunchArgument('P', default_value='0.0',
        description='Initial Pitch'),
    DeclareLaunchArgument('Y', default_value='3.1416',
        description='Initial Yaw'),
    DeclareLaunchArgument('entity', default_value='orion',
        description='Entity name or your preferred name for the robot'),
    DeclareLaunchArgument('ros_bridge', default_value='true',
        description='Boolean flag to indicate the usage of the ROS-GZ bridge')
]

# /////////////////////////// LAUNCH DEFINITION /////////////////////////////////
def generate_launch_description():
    # Generate launch descripiton
    ld = LaunchDescription(ARGS)

    # Path definitions
    pkg_gz = get_package_share_directory('orion_gz')
    spawn_file = os.path.join(pkg_gz, 'launch', 'spawn_robot.launch.py')
    bridge_config_file_path = os.path.join(pkg_gz, 'config', 
        'ros_gz_bridge.yaml')   

    # Additional config set up
    bridge_config = ReplaceString(
       source_file=bridge_config_file_path,
       replacements={'<entity>': LaunchConfiguration('entity')},
   )


    # -Include spawn
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(spawn_file),
            launch_arguments= {
                "camera": LaunchConfiguration('camera'),
                "servo": LaunchConfiguration('servo'),
                "g_mov": LaunchConfiguration('g_mov'), 
                "rasp": LaunchConfiguration('rasp'),
                "x": LaunchConfiguration('x'), 
                "y": LaunchConfiguration('y'), 
                "z": LaunchConfiguration('z'),
                "roll": LaunchConfiguration('R'), 
                "pitch": LaunchConfiguration('P'), 
                "yaw": LaunchConfiguration('Y'),
                "world": LaunchConfiguration('world'),
                "entity": LaunchConfiguration('entity'), 
                "ros_bridge": LaunchConfiguration('ros_bridge'),
            }.items(),
        )
    )

    # Add additional bridge node
    ld.add_action( 
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            parameters=[{
                'config_file': bridge_config
            }],
            output='screen',
            condition=IfCondition(LaunchConfiguration('ros_bridge')),
        )
    )

    return ld