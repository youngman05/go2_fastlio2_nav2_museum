from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String

try:
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize
    from unitree_sdk2py.go2.sport.sport_client import SportClient

    UNITREE_SDK_AVAILABLE = True
except ImportError:
    ChannelFactoryInitialize = None
    SportClient = None
    UNITREE_SDK_AVAILABLE = False


@dataclass
class VelocityLimit:
    max_linear_x: float
    max_linear_y: float
    max_angular_z: float


class UnitreeSportAdapter:
    def __init__(self, interface: str, startup_mode: str) -> None:
        if not UNITREE_SDK_AVAILABLE:
            raise RuntimeError(
                "unitree_sdk2py is not installed. Run 'make setup-unitree-sdk' on the target machine."
            )

        if interface:
            ChannelFactoryInitialize(0, interface)
        else:
            ChannelFactoryInitialize(0)

        self.client = SportClient()
        self.client.SetTimeout(10.0)
        self.client.Init()
        self._apply_startup_mode(startup_mode)

    def send_velocity(self, vx: float, vy: float, wz: float) -> int:
        return int(self.client.Move(vx, vy, wz))

    def stop(self) -> None:
        self.client.StopMove()
        self.client.Move(0.0, 0.0, 0.0)

    def _apply_startup_mode(self, startup_mode: str) -> None:
        if startup_mode == "none":
            return
        if startup_mode == "stand_up":
            self.client.StandUp()
            return
        if startup_mode == "free_walk":
            self.client.FreeWalk()
            return
        if startup_mode == "recovery_stand":
            self.client.RecoveryStand()
            return
        if startup_mode == "recovery_and_free_walk":
            self.client.RecoveryStand()
            self.client.FreeWalk()
            return
        raise RuntimeError(f"Unsupported startup_mode: {startup_mode}")


class Go2CmdBridge(Node):
    def __init__(self) -> None:
        super().__init__("go2_cmd_bridge")

        self.declare_parameter("max_linear_x", 0.6)
        self.declare_parameter("max_linear_y", 0.3)
        self.declare_parameter("max_angular_z", 0.8)
        self.declare_parameter("command_timeout_sec", 0.5)
        self.declare_parameter("publish_safe_cmd_vel", True)
        self.declare_parameter("dry_run", True)
        self.declare_parameter("network_interface", "")
        self.declare_parameter("startup_mode", "none")

        self.limits = VelocityLimit(
            max_linear_x=float(self.get_parameter("max_linear_x").value),
            max_linear_y=float(self.get_parameter("max_linear_y").value),
            max_angular_z=float(self.get_parameter("max_angular_z").value),
        )
        self.command_timeout_sec = float(self.get_parameter("command_timeout_sec").value)
        self.publish_safe_cmd_vel = bool(self.get_parameter("publish_safe_cmd_vel").value)
        self.dry_run = bool(self.get_parameter("dry_run").value)
        self.network_interface = str(self.get_parameter("network_interface").value)
        self.startup_mode = str(self.get_parameter("startup_mode").value)

        self.last_command_time = self.get_clock().now()
        self.is_stopped = True
        self.adapter: Optional[UnitreeSportAdapter] = None

        self.status_pub = self.create_publisher(String, "/go2_cmd_bridge/status", 10)
        self.safe_cmd_pub = self.create_publisher(Twist, "/cmd_vel_safe", 10)
        self.sub = self.create_subscription(Twist, "/cmd_vel", self.on_cmd_vel, 20)
        self.timer = self.create_timer(0.05, self.watchdog_tick)

        if self.dry_run:
            self.get_logger().info("Go2 command bridge started in dry-run mode.")
        else:
            self.adapter = UnitreeSportAdapter(
                interface=self.network_interface,
                startup_mode=self.startup_mode,
            )
            self.get_logger().info(
                "Go2 command bridge connected to Unitree SDK on interface '%s' with startup_mode='%s'."
                % (self.network_interface or "<default>", self.startup_mode)
            )

    def on_cmd_vel(self, msg: Twist) -> None:
        safe = Twist()
        safe.linear.x = self._clamp(msg.linear.x, self.limits.max_linear_x)
        safe.linear.y = self._clamp(msg.linear.y, self.limits.max_linear_y)
        safe.angular.z = self._clamp(msg.angular.z, self.limits.max_angular_z)

        self.last_command_time = self.get_clock().now()
        self.is_stopped = False

        if self.publish_safe_cmd_vel:
            self.safe_cmd_pub.publish(safe)

        self._publish_status(
            f"cmd accepted vx={safe.linear.x:.2f} vy={safe.linear.y:.2f} wz={safe.angular.z:.2f}"
        )

        if not self.dry_run:
            self._send_to_unitree_sdk(safe)

    def watchdog_tick(self) -> None:
        age = (self.get_clock().now() - self.last_command_time).nanoseconds / 1e9
        if self.is_stopped or age <= self.command_timeout_sec:
            return

        stop_msg = Twist()
        if self.publish_safe_cmd_vel:
            self.safe_cmd_pub.publish(stop_msg)

        if not self.dry_run:
            self._send_to_unitree_sdk(stop_msg)

        self.is_stopped = True
        self._publish_status("watchdog timeout, robot stop command issued")

    def _send_to_unitree_sdk(self, cmd: Twist) -> None:
        if self.adapter is None:
            raise RuntimeError("Unitree adapter is not initialized")
        ret = self.adapter.send_velocity(cmd.linear.x, cmd.linear.y, cmd.angular.z)
        self.get_logger().debug(
            "Unitree SDK Move returned %s for vx=%.2f vy=%.2f wz=%.2f"
            % (ret, cmd.linear.x, cmd.linear.y, cmd.angular.z)
        )

    def _publish_status(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.status_pub.publish(msg)
        self.get_logger().info(text)

    @staticmethod
    def _clamp(value: float, limit: float) -> float:
        return max(min(value, limit), -limit)


def main() -> None:
    rclpy.init()
    node = Go2CmdBridge()
    try:
        rclpy.spin(node)
    finally:
        if node.adapter is not None:
            try:
                node.adapter.stop()
            except Exception as exc:  # pragma: no cover - hardware shutdown best effort
                node.get_logger().warning(f"Failed to stop Unitree motion cleanly: {exc}")
        node.destroy_node()
        rclpy.shutdown()
