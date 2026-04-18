from __future__ import annotations

from pathlib import Path
from typing import Any

import rclpy
import yaml
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import String


class MuseumGuideManager(Node):
    def __init__(self) -> None:
        super().__init__("museum_guide_manager")

        self.declare_parameter("waypoints_file", "")
        self.declare_parameter("navigate_to_pose_action", "/navigate_to_pose")
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("loop_route", False)

        self.map_frame = str(self.get_parameter("map_frame").value)
        self.loop_route = bool(self.get_parameter("loop_route").value)
        self.waypoints_file = str(self.get_parameter("waypoints_file").value)

        self.status_pub = self.create_publisher(String, "/guide/status", 10)
        self.action_client = ActionClient(
            self,
            NavigateToPose,
            str(self.get_parameter("navigate_to_pose_action").value),
        )

        self.waypoints = self._load_waypoints(self.waypoints_file)
        self.current_index = 0

        self.get_logger().info(f"Loaded {len(self.waypoints)} waypoints from {self.waypoints_file or 'default config'}")
        self.create_timer(2.0, self._start_if_idle)
        self.goal_in_flight = False

    def _start_if_idle(self) -> None:
        if self.goal_in_flight or not self.waypoints:
            return
        self._send_current_goal()

    def _send_current_goal(self) -> None:
        waypoint = self.waypoints[self.current_index]
        pose = PoseStamped()
        pose.header.frame_id = self.map_frame
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(waypoint["pose"][0])
        pose.pose.position.y = float(waypoint["pose"][1])
        pose.pose.orientation.z = float(waypoint["pose"][2])
        pose.pose.orientation.w = float(waypoint["pose"][3])

        goal = NavigateToPose.Goal()
        goal.pose = pose

        if not self.action_client.wait_for_server(timeout_sec=1.0):
            self._publish_status("NavigateToPose action server not available yet")
            return

        self.goal_in_flight = True
        self._publish_status(f"Sending goal: {waypoint['name']}")
        future = self.action_client.send_goal_async(goal)
        future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future: Any) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.goal_in_flight = False
            self._publish_status("Goal rejected by Nav2")
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._goal_result_callback)

    def _goal_result_callback(self, future: Any) -> None:
        self.goal_in_flight = False
        self._publish_status(f"Goal completed for {self.waypoints[self.current_index]['name']}")

        self.current_index += 1
        if self.current_index >= len(self.waypoints):
            if self.loop_route:
                self.current_index = 0
            else:
                self._publish_status("Guide route finished")
                return

        self._send_current_goal()

    def _load_waypoints(self, path_str: str) -> list[dict[str, Any]]:
        if not path_str:
            return []

        path = Path(path_str)
        if not path.exists():
            self._publish_status(f"Waypoint file not found: {path}")
            return []

        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return list(data.get("waypoints", []))

    def _publish_status(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.status_pub.publish(msg)
        self.get_logger().info(text)


def main() -> None:
    rclpy.init()
    node = MuseumGuideManager()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
