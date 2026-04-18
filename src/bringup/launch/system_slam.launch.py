from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="go2_cmd_bridge",
            executable="cmd_bridge_node",
            name="go2_cmd_bridge",
            output="screen",
            parameters=[
                PathJoinSubstitution([
                    FindPackageShare("bringup"),
                    "config",
                    "master_params.yaml",
                ]),
            ],
        ),
    ])
