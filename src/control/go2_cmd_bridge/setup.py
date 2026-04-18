from setuptools import setup

package_name = "go2_cmd_bridge"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="user",
    maintainer_email="user@example.com",
    description="Safe ROS 2 cmd_vel bridge scaffold for Unitree Go2.",
    license="Proprietary",
    entry_points={
        "console_scripts": [
            "cmd_bridge_node = go2_cmd_bridge.cmd_bridge_node:main",
        ],
    },
)
