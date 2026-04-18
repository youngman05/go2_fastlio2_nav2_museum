# Perception Integration Notes

This folder is reserved for:

- FAST-LIO2 integration
- `pointcloud_to_laserscan`
- optional localizer or relocalization layer
- pointcloud preprocessing for Nav2 obstacle layers

Recommended first integration path:

1. bring in the ROS 2 FAST-LIO2 package
2. validate `odom -> base_link`
3. add `pointcloud_to_laserscan`
4. add `slam_toolbox` for `map -> odom`
