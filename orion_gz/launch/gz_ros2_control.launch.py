# ///////////////////////////// REQUIRED LIBRARIES //////////////////////////////
# .............................. Python libraries ...............................
import os
import xacro

# ............................ Launch dependencies .............................
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

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
]

# /////////////////////////// FUNCTIONS DEFINITIONS ////////////////////////////
def get_argument(context, arg):
    """
    Get the context when performing the Launch Configuration
    """
    return LaunchConfiguration(arg).perform(context)

def generate_robot_description(context):
    """
    For generating the robot description, consider the URDF/Xacro file provided,
    but modifying the meshes source path in order to make it available to
    Gazebo Harmonic.
    """
    # Paths to consider
    pkg_gmov = get_package_share_directory('g_mov_description')
    pkg_description = get_package_share_directory('orion_description')
    xacro_file = os.path.join(pkg_description, 'urdf', 'orion.urdf.xacro')

    # Generating mapping in order to allow xacro modularity
    mappings = {
        'camera': get_argument(context, "camera"),
        'servo': get_argument(context, "servo"),
        'g_mov': get_argument(context, "g_mov"),
        'rasp': get_argument(context, "rasp"),
        'gazebo': get_argument(context, "gazebo")
    }

    # Obtaining robot description and making the substitution
    robot_description_config = xacro.process_file(xacro_file, mappings=mappings)
    robot_desc = robot_description_config.toprettyxml(indent='  ')
    robot_desc = robot_desc.replace(
        'package://orion_description/', f'file://{pkg_description}/'
    )
    robot_desc = robot_desc.replace(
        'package://g_mov_description/', f'file://{pkg_gmov}/'
    )

    # Launch node for robot state publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name="robot_state_publisher",
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'rate': 200,
        }]
    )

    # Return configuration as a set
    return [rsp_node]

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

    # Generate launch description
    ld = LaunchDescription(ARGS)


    # Node for GZ
    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', '-name',
                   'orion', '-allow_renaming', 'true', '-z', '0.1'],
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

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    ld.add_action(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [PathJoinSubstitution([FindPackageShare('ros_gz_sim'),
                                       'launch',
                                       'gz_sim.launch.py'])]),
            launch_arguments=[('gz_args', [' -r -v 3 empty.sdf'])])
    )
    ld.add_action(
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gz_spawn_entity,
                on_exit=[diff_drive_base_controller_spawner],
            )
        )
    )

    ld.add_action(RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=diff_drive_base_controller_spawner,
                on_exit=[joint_state_broadcaster_spawner],
            )
        )
    )

    ld.add_action(bridge)
    ld.add_action(gz_spawn_entity)
    
    # Add robot description with context
    ld.add_action(OpaqueFunction(function=generate_robot_description))
    
    return ld