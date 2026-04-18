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
        Node(
            package="museum_guide_manager",
            executable="guide_manager_node",
            name="museum_guide_manager",
            output="screen",
            parameters=[
                PathJoinSubstitution([
                    FindPackageShare("bringup"),
                    "config",
                    "master_params.yaml",
                ]),
                {
                    "waypoints_file": PathJoinSubstitution([
                        FindPackageShare("museum_guide_manager"),
                        "config",
                        "waypoints.example.yaml",
                    ]),
                },
            ],
        ),
    ])
