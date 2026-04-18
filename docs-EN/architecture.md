# System Architecture

```text
Livox MID360 + IMU
        |
        v
  livox_ros_driver2 / imu driver
        |
        v
      FAST-LIO2 ------------------> odom / TF(odom -> base_link)
        |
        +--> pointcloud_to_laserscan
        |           |
        |           v
        |     slam_toolbox
        |           |
        |           v
        |      TF(map -> odom)
        |
        +-----------------------> Nav2
                                   |
                                   v
                                /cmd_vel
                                   |
                                   v
                            go2_cmd_bridge
                                   |
                                   v
                            Unitree Go2 SDK
```

## Package Roles

- `bringup`: shared launch, parameters, runtime entry points
- `go2_cmd_bridge`: safe `/cmd_vel` handling, watchdog, Unitree SDK adapter
- `museum_guide_manager`: waypoint mission control for museum tours
- `perception`: FAST-LIO2 and 3D-to-2D navigation input integration
- `sensor_drivers`: Livox and IMU bringup
