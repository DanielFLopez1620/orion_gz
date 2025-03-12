import os
import xacro

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # ------------------------ Paths definitions ----------------------------
    pkg_description = get_package_share_directory('orion_description')
    pkg_gz = get_package_share_directory('ros_gz_sim')
    rsp_file = os.path.join(pkg_description, 'launch', 'rsp.launch.py')
    gz_file = os.path.join(pkg_gz, 'launch', 'gz_sim.launch.py')
    xacro_file = os.path.join(pkg_description, 'urdf', 'orion.urdf.xacro')


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

    # -------------------------- Includes --------------------------------------
    rsp_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rsp_file),
        launch_arguments= {"camera": camera, "servo": servo,
                            "g_mov": g_mov, "rasp": rasp,
                            "gazebo": 'true'}.items(),
    )

    gazebo_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_file),
        launch_arguments={
            'gz_args': [f'-r -v 4 ', world],
            'on_exit_shutdown': 'true'
        }.items()
    )

    # ------------------------ Nodes --------------------------------------------
    spawn_model_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'orion',
            '-x', x,
            '-y', y,
            '-z', z,
            '-R', roll,
            '-P', pitch,
            '-Y', yaw,
            '-topic', 'robot_description',
            '-allow_renaming', 'false',
        ],
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
        rsp_include,
        gazebo_include,
        spawn_model_node,
    ])