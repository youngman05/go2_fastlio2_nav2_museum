from setuptools import setup

package_name = "museum_guide_manager"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/config", ["config/waypoints.example.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="user",
    maintainer_email="user@example.com",
    description="Waypoint mission manager scaffold for the Go2 museum guide robot.",
    license="Proprietary",
    entry_points={
        "console_scripts": [
            "guide_manager_node = museum_guide_manager.guide_manager_node:main",
        ],
    },
)
