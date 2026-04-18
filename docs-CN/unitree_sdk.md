# Unitree SDK 接入

当前项目的 Go2 控制桥基于官方 Python SDK：

- 仓库：`https://github.com/unitreerobotics/unitree_sdk2_python`
- Python 包名：`unitree_sdk2py`

## 当前接入方式

`go2_cmd_bridge` 在 `dry_run: false` 时会尝试：

1. 调用 `ChannelFactoryInitialize(0, <network_interface>)`
2. 创建 `SportClient`
3. 调用 `SportClient.Init()`
4. 把 ROS2 `/cmd_vel` 转成 `SportClient.Move(vx, vy, wz)`
5. watchdog 超时时调用 `StopMove()`

## 安装

推荐在 Jetson 上执行：

```bash
cd ~/go2_fastlio2_nav2_museum
make setup
make setup-unitree-sdk
```

脚本会：

- 拉取 `third_party/unitree_sdk2_python`
- 如果需要，提示安装 `cyclonedds`
- 安装 `unitree_sdk2py`

## 参数

在 `src/bringup/config/master_params.yaml` 中：

- `dry_run`: 本机调试时保持 `true`
- `network_interface`: 连接 Go2 的网卡名，例如 `eth0`
- `startup_mode`: 建议先用 `none`

可选启动模式：

- `none`
- `stand_up`
- `free_walk`
- `recovery_stand`
- `recovery_and_free_walk`

## 注意

- 首次真机联调时，不要自动启用激进启动动作。
- 建议先 `dry_run: true` 验证 Nav2 和 `/cmd_vel` 流程，再切换真机。
- 启动前保证机器人周围空旷。
