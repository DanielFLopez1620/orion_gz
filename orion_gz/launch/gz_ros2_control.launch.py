# ///////////////////////////// REQUIRED LIBRARIES //////////////////////////////
# .............................. Python libraries ...............................
import os

# ............................ Launch dependencies .............................
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

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
    DeclareLaunchArgument('Y', default_value='0.0',
        description='Initial Yaw'),
    DeclareLaunchArgument('entity', default_value='orion',
        description='Entity name or your preferred name for the robot'),
]

# /////////////////////////// FUNCTION DEFINITIONS ////////////////////////////
def replace_entities(path):
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


# /////////////////////////// LAUNCH DEFINITIONS //////////////////////////////
def generate_launch_description():
    
    # Paths to consider
    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare('orion_control'),
            'config',
            'controllers.yaml',
        ]
    )

    # Path definitions
    pkg_gz = get_package_share_directory('orion_gz')
    spawn_file = os.path.join(pkg_gz, 'launch', 'spawn_robot.launch.py')
    extra_bridge_path = os.path.join(pkg_gz, 'config', 'ros2_ctl_extra_bridge.yaml')   
    astra_bridge_path = os.path.join(pkg_gz, 'config', 'astra_bridge.yaml')  
    a010_bridge_path = os.path.join(pkg_gz, 'config', 'a010_bridge.yaml')  
    g_mov_bridge_path = os.path.join(pkg_gz, 'config', 'g_mov_short_bridge.yaml')  
    os30a_bridge_path = os.path.join(pkg_gz, 'config', 'os30a_bridge.yaml')  

    # Additional config set up
    extra_bridge_config = replace_entities(extra_bridge_path)
    astra_bridge_config = replace_entities(astra_bridge_path)
    a010_bridge_config = replace_entities(a010_bridge_path)
    g_mov_bridge_config = replace_entities(g_mov_bridge_path)
    os30a_bridge_config = replace_entities(os30a_bridge_path)


    # Generate launch description
    ld = LaunchDescription(ARGS)


    spawn_include = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(spawn_file),
            launch_arguments= {
                "camera": LaunchConfiguration('camera'),
                "servo": LaunchConfiguration('servo'),
                "g_mov": LaunchConfiguration('g_mov'), 
                "rasp": LaunchConfiguration('rasp'),
                "ros2_control": "true",
                "x": LaunchConfiguration('x'), 
                "y": LaunchConfiguration('y'), 
                "z": LaunchConfiguration('z'),
                "roll": LaunchConfiguration('R'), 
                "pitch": LaunchConfiguration('P'), 
                "yaw": LaunchConfiguration('Y'),
                "world": LaunchConfiguration('world'),
                "entity": LaunchConfiguration('entity'), 
                "ros_bridge": "true",
            }.items(),
        )
    
    # General bridge for tfs and joint state
    ld.add_action(
       Node(
               package='ros_gz_bridge',
               name="ros_gz_bridge_base",
               executable='parameter_bridge',
               parameters=[{
                'config_file': extra_bridge_config
                }],
                output='screen',
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

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    diff_drive_base_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_drive_base_controller',
            '--param-file',
            robot_controllers,
            ],
    )

    ld.add_action(spawn_include)

    # Timer to delay the execution of diff_drive_base_controller_spawner
    ld.add_action( TimerAction(
        period=15.0,  # 30 seconds delay
        actions=[diff_drive_base_controller_spawner]
    ))

    ld.add_action(RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=diff_drive_base_controller_spawner,
                on_exit=[joint_state_broadcaster_spawner],
            )
        )
    )
    
    return ld