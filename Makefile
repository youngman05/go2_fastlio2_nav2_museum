SHELL := /bin/bash

.PHONY: setup build test launch-slam launch-nav launch-guide clean

setup:
	vcs import src < dependencies.repos || true
	rosdep install --from-paths src --ignore-src -y

build:
	source /opt/ros/humble/setup.bash && \
	colcon build --symlink-install --parallel-workers 1

test:
	source /opt/ros/humble/setup.bash && \
	colcon test && colcon test-result --verbose

launch-slam:
	source /opt/ros/humble/setup.bash && \
	source install/setup.bash && \
	ros2 launch bringup system_slam.launch.py

launch-nav:
	source /opt/ros/humble/setup.bash && \
	source install/setup.bash && \
	ros2 launch bringup system_nav.launch.py

launch-guide:
	source /opt/ros/humble/setup.bash && \
	source install/setup.bash && \
	ros2 launch bringup system_guide.launch.py

clean:
	rm -rf build/ install/ log/
