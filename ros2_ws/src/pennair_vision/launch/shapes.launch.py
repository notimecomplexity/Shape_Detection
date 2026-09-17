from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('video_path', description='Absolute video path inside Ubuntu'),
        DeclareLaunchArgument('fps', default_value='0.0', description='0 uses source FPS; lower for slower playback'),
        DeclareLaunchArgument('loop', default_value='false'),
        DeclareLaunchArgument('show_debug', default_value='false'),
        DeclareLaunchArgument('depth_in', default_value='239.25346088310212'),
        Node(package='pennair_vision', executable='shape_detector', output='screen',
             parameters=[{'show_debug': ParameterValue(LaunchConfiguration('show_debug'), value_type=bool),
                          'depth_in': ParameterValue(LaunchConfiguration('depth_in'), value_type=float)}]),
        Node(package='pennair_vision', executable='video_publisher', output='screen',
             parameters=[{'video_path': ParameterValue(LaunchConfiguration('video_path'), value_type=str),
                          'fps': ParameterValue(LaunchConfiguration('fps'), value_type=float),
                          'loop': ParameterValue(LaunchConfiguration('loop'), value_type=bool)}]),
    ])
