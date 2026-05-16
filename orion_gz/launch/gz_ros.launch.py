# ///////////////////////////// REQUIRED LIBRARIES //////////////////////////////
# .............................. Python libraries ...............................
import os

# ............................ Launch dependencies .............................
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

# ........................... Additional packages dependencies ..................
from nav2_common.launch import ReplaceString   

# //////////////////////////// GLOBAL DEFINITIONS //////////////////////////////
ARGS = [
    DeclareLaunchArgument('camera', default_value='os30a',
        description="Choose a cam for the robot (os30a, astra_s, a010)",
        choices=['os30a', 'astra_s', 'a010']),
    DeclareLaunchArgument('servo',default_value='true',
        description="Boolean to include or not the servos",
        choices=['true', 'false']),
    DeclareLaunchArgument('g_mov',default_value='false',
        description="When using camera a010, whether to include or not G Mov",
        choices=['true', 'false']),
    DeclareLaunchArgument('rasp', default_value='rpi5',
        description="Select 4 for Raspberry Pi 4B, or 5 for Raspberry Pi 5",
        choices=['rpi4', 'rpi5']),
    DeclareLaunchArgument('gazebo',default_value='true',
        description="True for using gazebo tags, false otherwise",
        choices=['true', 'false']),
    DeclareLaunchArgument('world', default_value='custom_empty.sdf',
        description='Specify the world file for Gazebo',
        choices=['custom_empty.sdf', 'simple_obstacles.sdf', 'more_obstacles.sdf', 'turtle_world.sdf']),
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
    DeclareLaunchArgument('Y', default_value='0.0',
        description='Initial Yaw'),
    DeclareLaunchArgument('entity', default_value='orion',
        description='Entity name or your preferred name for the robot'),
    DeclareLaunchArgument('ros_bridge', default_value='true',
        description='Boolean flag to indicate the usage of the ROS-GZ bridge',
        choices=['true', 'false']),
    DeclareLaunchArgument('simplified', default_value='false',
        description="To ignore no-functional components in the URDF description",
        choices=['true', 'false']),
    DeclareLaunchArgument('motor', default_value='100',
        description="Select your  motor nominal speed (rpm) at 12V",
        choices=['1000', '100']),
]

# /////////////////////////// FUNCTION DEFINITIONS ////////////////////////////
def replace_entities(path):
    """
    Function oriented to replace the elements of the bridge config so it adapts
    to the world and the entity.

    Params
    ---
    path : String
        Path to the .yaml file that contains the ros-gz bridge config

    Returns
    ---
    bridge : String
        Replaced .yaml config for launching the bridge
    """
    config_file = ReplaceString(
        source_file=path,
        replacements={
           '<entity>': LaunchConfiguration('entity'),
           '<world>': LaunchConfiguration('world')}
        )
    return ReplaceString(
        source_file=config_file,
        replacements={
           '.sdf': ''}
        )


# /////////////////////////// LAUNCH DEFINITION ///////////////////////////////
def generate_launch_description():
    """
    Launch configuration oriented to load a robot state, load it to spawn a
    robot in Gazebo and configure the ros-gz bridge for making possible
    the interaction between the simulation and the ROS 2 ecosystem.
    """

    # Generate launch descripiton
    ld = LaunchDescription(ARGS)

    # Path definitions
    pkg_gz = get_package_share_directory('orion_gz')
    spawn_file = os.path.join(pkg_gz, 'launch', 'spawn_robot.launch.py')
    base_bridge_path = os.path.join(pkg_gz, 'config', 'base_bridge.yaml')
    servo_bridge_path = os.path.join(pkg_gz, 'config', 'servo_bridge.yaml')
    astra_bridge_path = os.path.join(pkg_gz, 'config', 'astra_bridge.yaml')
    a010_bridge_path = os.path.join(pkg_gz, 'config', 'a010_bridge.yaml')
    g_mov_bridge_path = os.path.join(pkg_gz, 'config', 'g_mov_bridge.yaml')
    os30a_bridge_path = os.path.join(pkg_gz, 'config', 'os30a_bridge.yaml')

    # Additional config set up
    base_bridge_config = replace_entities(base_bridge_path)
    servo_bridge_config = replace_entities(servo_bridge_path)
    astra_bridge_config = replace_entities(astra_bridge_path)
    a010_bridge_config = replace_entities(a010_bridge_path)
    g_mov_bridge_config = replace_entities(g_mov_bridge_path)
    os30a_bridge_config = replace_entities(os30a_bridge_path)

    # Include spawn orion robot
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(spawn_file),
            launch_arguments= {
                "camera": LaunchConfiguration('camera'),
                "servo": LaunchConfiguration('servo'),
                "g_mov": LaunchConfiguration('g_mov'),
                "rasp": LaunchConfiguration('rasp'),
                "ros2_control": "false",
                "x": LaunchConfiguration('x'),
                "y": LaunchConfiguration('y'),
                "z": LaunchConfiguration('z'),
                "R": LaunchConfiguration('R'),
                "P": LaunchConfiguration('P'),
                "Y": LaunchConfiguration('Y'),
                "world": LaunchConfiguration('world'),
                "entity": LaunchConfiguration('entity'),
                "ros_bridge": LaunchConfiguration('ros_bridge'),
                "simplified": LaunchConfiguration('simplified'),
                "motor": LaunchConfiguration('motor')
            }.items(),
        )
    )

    # Launch joint_state, tfs, cmd_vel and odom bridge between ROS and GZ
    ld.add_action(
       Node(
               package='ros_gz_bridge',
               name="ros_gz_bridge_base",
               executable='parameter_bridge',
               parameters=[{
                'config_file': base_bridge_config
                }],
                output='screen',
                condition=IfCondition(LaunchConfiguration('ros_bridge')),
           ),
    )
    
    # Launch servo controller bridge between ROS and GZ
    ld.add_action(
       Node(
               package='ros_gz_bridge',
               name="ros_gz_bridge_servo",
               executable='parameter_bridge',
               parameters=[{
                'config_file': servo_bridge_config
                }],
                output='screen',
                condition=IfCondition(LaunchConfiguration('servo')),
           ),
    )
    
    # Launch astra_s bridge between ROS and GZ
    ld.add_action(
       Node(
               package='ros_gz_bridge',
               name="ros_gz_bridge_astra_s",
               executable='parameter_bridge',
               parameters=[{
                'config_file': astra_bridge_config
                }],
                output='screen',
                condition=IfCondition(PythonExpression(
                    ["'", LaunchConfiguration('camera'), "' == 'astra_s'"])),
           ),
    )

    # Launch a010 bridge between ROS and GZ
    ld.add_action(
       Node(
               package='ros_gz_bridge',
               name="ros_gz_bridge_a010",
               executable='parameter_bridge',
               parameters=[{
                'config_file': a010_bridge_config
                }],
                output='screen',
                condition=IfCondition(PythonExpression(
                    ["'", LaunchConfiguration('camera'), "' == 'a010'"])),
           ),
    )

    # Launch g_mov bridge between ROS and GZ
    ld.add_action(
       Node(
               package='ros_gz_bridge',
               name="ros_gz_bridge_g_mov",
               executable='parameter_bridge',
               parameters=[{
                'config_file': g_mov_bridge_config
                }],
                output='screen',
                condition=IfCondition(LaunchConfiguration('g_mov')),
           ),
    )

    # Launch os30a bridge between ROS and GZ
    ld.add_action(
       Node(
               package='ros_gz_bridge',
               name="ros_gz_bridge_os30a",
               executable='parameter_bridge',
               parameters=[{
                'config_file': os30a_bridge_config
                }],
                output='screen',
                condition=IfCondition(PythonExpression(
                    ["'", LaunchConfiguration('camera'), "' == 'os30a'"])),
           ),
    )

    # Activate laser filter
    ld.add_action(Node(
        package='orion_utils_py',
        executable='laser_filter',
        name='laser_filter',
        output='screen'
    ))

    # Return launch description
    return ld