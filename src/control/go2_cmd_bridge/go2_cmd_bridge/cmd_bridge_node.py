from __future__ import annotations

from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String


@dataclass
class VelocityLimit:
    max_linear_x: float
    max_linear_y: float
    max_angular_z: float


class Go2CmdBridge(Node):
    def __init__(self) -> None:
        super().__init__("go2_cmd_bridge")

        self.declare_parameter("max_linear_x", 0.6)
        self.declare_parameter("max_linear_y", 0.3)
        self.declare_parameter("max_angular_z", 0.8)
        self.declare_parameter("command_timeout_sec", 0.5)
        self.declare_parameter("publish_safe_cmd_vel", True)
        self.declare_parameter("dry_run", True)

        self.limits = VelocityLimit(
            max_linear_x=float(self.get_parameter("max_linear_x").value),
            max_linear_y=float(self.get_parameter("max_linear_y").value),
            max_angular_z=float(self.get_parameter("max_angular_z").value),
        )
        self.command_timeout_sec = float(self.get_parameter("command_timeout_sec").value)
        self.publish_safe_cmd_vel = bool(self.get_parameter("publish_safe_cmd_vel").value)
        self.dry_run = bool(self.get_parameter("dry_run").value)

        self.last_command_time = self.get_clock().now()
        self.is_stopped = True

        self.status_pub = self.create_publisher(String, "/go2_cmd_bridge/status", 10)
        self.safe_cmd_pub = self.create_publisher(Twist, "/cmd_vel_safe", 10)
        self.sub = self.create_subscription(Twist, "/cmd_vel", self.on_cmd_vel, 20)
        self.timer = self.create_timer(0.05, self.watchdog_tick)

        self.get_logger().info("Go2 command bridge started in dry-run mode." if self.dry_run else "Go2 command bridge started.")

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
        # TODO: replace this with the Unitree ROS 2 SDK adapter on the Jetson target.
        self.get_logger().info(
            "Unitree SDK stub vx=%.2f vy=%.2f wz=%.2f"
            % (cmd.linear.x, cmd.linear.y, cmd.angular.z)
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
        node.destroy_node()
        rclpy.shutdown()
