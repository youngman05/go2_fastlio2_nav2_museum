# 系统架构

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

## 包职责

- `bringup`: 统一 launch、参数、运行入口
- `go2_cmd_bridge`: `/cmd_vel` 安全限幅、超时停车、接 Unitree SDK
- `museum_guide_manager`: 导览 waypoint 任务管理
- `perception`: FAST-LIO2 及点云导航输入整合
- `sensor_drivers`: Livox 和 IMU 驱动接入
