# ///////////////////////////// REQUIRED LIBRARIES //////////////////////////////
# .............................. Python libraries ...............................
import os

# ............................ Launch dependencies .............................
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, GroupAction, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression

from launch_ros.actions import Node

# ........................... Additional packages dependencies ..................
from nav2_common.launch import ReplaceString
from controller_manager.launch_utils import generate_load_controller_launch_description

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
    DeclareLaunchArgument('world', default_value='custom_empty.sdf',
        description='Specify the world file for Gazebo',
        choices=['custom_empty.sdf', 'simple_obstacles.sdf', 'more_obstacles.sdf']),
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

def load_controllers(context):
    """
    Build the ros2_control_node and controller spawners dynamically, using
    conditional activation and keeping the structure clean and scalable.

    This function is compatible with OpaqueFunction.
    """

    pkg_ctl = get_package_share_directory('orion_control')
    mobile_base_path = os.path.join(pkg_ctl, 'config', 'mobile_base_controller.yaml')
    left_arm_path = os.path.join(pkg_ctl, 'config', 'simple_left_arm_controller.yaml')
    right_arm_path = os.path.join(pkg_ctl, 'config', 'simple_right_arm_controller.yaml')
    joint_broad_path = os.path.join(pkg_ctl, 'config', 'joint_state_broadcaster.yaml')
    g_mov_path = os.path.join(pkg_ctl, 'config', 'g_mov_servo_controller.yaml')

    controllers = [
        generate_load_controller_launch_description(
            controller_name="mobile_base_controller",
            controller_params_file=mobile_base_path)
    ]

    # Check if the servo argument is true
    if LaunchConfiguration('servo').perform(context) == 'true':
        controllers.append(generate_load_controller_launch_description(
            controller_name="simple_left_arm_controller",
            controller_params_file=left_arm_path
        ))

        controllers.append(generate_load_controller_launch_description(
            controller_name="simple_right_arm_controller",
            controller_params_file=right_arm_path
        ))
    if (LaunchConfiguration('camera').perform(context) == 'a010' and
        LaunchConfiguration('g_mov').perform(context) == 'true'):
        controllers.append(generate_load_controller_launch_description(
            controller_name="g_mov_servo_controller",
            controller_params_file=g_mov_path
        ))

    controllers.append(generate_load_controller_launch_description(
        controller_name="joint_state_broadcaster",
        controller_params_file=joint_broad_path
    ))

    return controllers

# /////////////////////////// LAUNCH DEFINITIONS //////////////////////////////
def generate_launch_description():
    """
    Launch configuration oriented to load a robot state, load it to spawn a
    robot in Gazebo and configure the ros-gz bridge for making possible
    the exchange fo information of the sensor, while also connecting and loading
    the ros2_controllers that were set up in the GZ simulation.
    """

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
                "simplified": LaunchConfiguration('simplified'),
                "motor": LaunchConfiguration('motor')
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
                condition=IfCondition(PythonExpression(
                    ["'", LaunchConfiguration('camera'), "' == 'astra_s' and ",
                    LaunchConfiguration('g_mov')])),
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

    # Include spawn
    ld.add_action(spawn_include)

    # Load controllers by using opaque functions
    controllers_loader = TimerAction(
        period=10.0,
        actions=[OpaqueFunction(function=load_controllers)]
    )

    ld.add_action(controllers_loader)

    # Laser filter related to prevent considering self as obstacle
    ld.add_action(Node(
        package='orion_utils_py',
        executable='laser_filter',
        name='laser_filter',
        output='screen'
    ))

    # Return launch description
    return ld