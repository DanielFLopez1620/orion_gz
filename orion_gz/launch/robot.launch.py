import os
import xacro
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    # Define paths
    pkg_description = get_package_share_directory('orion_description')
    xacro_file = os.path.join(pkg_description, 'urdf', 'orion.urdf.xacro')

    # --------------------------- Configurations -----------------------------
    use_gui = LaunchConfiguration('use_gui')
    camera = LaunchConfiguration('camera')
    servo = LaunchConfiguration('servo')
    g_mov = LaunchConfiguration('g_mov')
    rasp = LaunchConfiguration('rasp')

    # -------------------------- Launch arguments -----------------------------
    gui_arg = DeclareLaunchArgument(
        "use_gui", 
        default_value="true", 
        description="Use joint_state_publisher_gui"
    )

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


    # -------------------------- Nodes ----------------------------------------
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name="robot_state_publisher",
        output='screen',
        parameters=[{
            'robot_description': Command([
                'xacro ', xacro_file, 
                ' camera:=', camera,
                ' servo:=', servo,
                ' g_mov:=', g_mov,
                ' rasp:=', rasp,
                ' gazebo:=true',
            ])
        }]
    )

    jsp_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    rviz_config_file = os.path.join(pkg_description, 'rviz', 'model_viz.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen'
    )

    # Define the robot's name and package name
    robot_name = "orion"
    package_name = "orion_description"

    # Define a launch argument for the world file, defaulting to "empty.sdf"
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='Specify the world file for Gazebo (e.g., empty.sdf)'
    )

    # Define launch arguments for initial pose
    x_arg = DeclareLaunchArgument(
        'x', default_value='0.0', description='Initial X position')

    y_arg = DeclareLaunchArgument(
        'y', default_value='0.0', description='Initial Y position')

    z_arg = DeclareLaunchArgument(
        'z', default_value='0.5', description='Initial Z position')

    roll_arg = DeclareLaunchArgument(
        'R', default_value='0.0', description='Initial Roll')

    pitch_arg = DeclareLaunchArgument(
        'P', default_value='0.0', description='Initial Pitch')

    yaw_arg = DeclareLaunchArgument(
        'Y', default_value='0.0', description='Initial Yaw')

    # Retrieve launch configurations
    world_file = LaunchConfiguration('world')
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    roll = LaunchConfiguration('R')
    pitch = LaunchConfiguration('P')
    yaw = LaunchConfiguration('Y')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='Specify the world file for Gazebo (e.g., empty.sdf)'
    )

    # Prepare to include the Gazebo simulation launch file
    gazebo_pkg_launch = PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory('ros_gz_sim'),
            'launch',
            'gz_sim.launch.py'
        )
    )

    # Include the Gazebo launch description with specific arguments
    gazebo_launch = IncludeLaunchDescription(
        gazebo_pkg_launch,
        launch_arguments={
            'gz_args': [f'-r -v 4 ', world_file],
            'on_exit_shutdown': 'true'}
    )

    robot_model_path = os.path.join(
        get_package_share_directory(package_name),
        'urdf',
        'orion.urdf.xacro'
    )

    mappings = {'camera:=': camera.perform({}),
                'servo:=': servo.perform({}),
                'g_mov:=': g_mov.perform({}),
                'rasp:=': rasp.perform({}),
                'gazebo': 'true'}
    
    robot_description = xacro.process_file(robot_model_path, mappings=mappings).toxml()

    # Create a node to spawn the robot model in the Gazebo environment
    spawn_model_gazebo_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robot_name,
            '-string', robot_description,
            '-x', x,
            '-y', y,
            '-z', z,
            '-R', roll,
            '-P', pitch,
            '-Y', yaw,
            '-allow_renaming', 'false'
        ],
        output='screen',
    )


    return LaunchDescription([
        camera_arg,
        use_servo_arg,
        use_g_mov_arg,
        rasp_arg,
        gui_arg,
        rsp_node,
        jsp_gui_node,
        rviz_node,
        world_arg,
        gazebo_launch,
        x_arg,
        y_arg,
        z_arg,
        roll_arg,
        pitch_arg,
        yaw_arg,
        spawn_model_gazebo_node
    ])
