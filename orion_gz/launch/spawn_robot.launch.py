# ///////////////////////////// REQUIRED LIBRARIES //////////////////////////////
# .............................. Python libraries ...............................
import os

# ............................ Launch dependencies .............................
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

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
    DeclareLaunchArgument('ros2_control', default_value='false',
        description="Whether to use ros2_control tags for motor controllers"),
    DeclareLaunchArgument('world', default_value='custom_empty.sdf',
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
    DeclareLaunchArgument('ros_bridge', default_value='false',
        description='Boolean flag to indicate the usage of the ROS-GZ bridge')
]

# ///////////////////////////// LAUNCH DEFINITION /////////////////////////////
def generate_launch_description():
    # Generate launch descripiton
    ld = LaunchDescription(ARGS)

    # Paths definitions
    pkg_orion_description = get_package_share_directory('orion_description')
    pkg_orion_gz = get_package_share_directory('orion_gz')
    pkg_gz = get_package_share_directory('ros_gz_sim')
    rsp_file = os.path.join(pkg_orion_description, 'launch', 'rsp.launch.py')
    gz_file = os.path.join(pkg_gz, 'launch', 'gz_sim.launch.py')
    world_path = PathJoinSubstitution([pkg_orion_gz,'world', LaunchConfiguration('world')])
    print(str(pkg_orion_gz))

    # Include ORION Robot State Publisher
    ld.add_action(
            IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rsp_file),
            launch_arguments= {
                "camera": LaunchConfiguration('camera'), 
                "servo": LaunchConfiguration('servo'),
                "g_mov": LaunchConfiguration('g_mov'), 
                "rasp": LaunchConfiguration('rasp'),
                "gazebo": 'true',
                "ros2_control": LaunchConfiguration("ros2_control")
            }.items(),
        )
    )

    # Include Gazebo Launch
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_file),
            launch_arguments={
                'gz_args': ['-r -v 4 ', world_path],
                'on_exit_shutdown': 'true'
            }.items()
        )
    )

    # Launch clock bridge between ROS and GZ
    ld.add_action(
       Node(
               package='ros_gz_bridge',
               name="ros_gz_bridge_for_clock",
               executable='parameter_bridge',
               arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'],
               output='screen',
               condition=IfCondition(LaunchConfiguration('ros_bridge')),
           ),
   )

    # Launch ORION spawner
    ld.add_action(
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', LaunchConfiguration('entity'),
                '-x', LaunchConfiguration('x'),
                '-y', LaunchConfiguration('y'),
                '-z', LaunchConfiguration('z'),
                '-R', LaunchConfiguration('R'),
                '-P', LaunchConfiguration('P'),
                '-Y', LaunchConfiguration('Y'),
                '-topic', 'robot_description',
                '-allow_renaming', 'false',
            ],
            output='screen',
        )
    )

    return ld