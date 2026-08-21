#!/usr/bin/env python3
"""
dead_reckoning_odom.py  -  dead-reckoning odometry for a mecanum drive robot.

Replaces fake_odom.py. Instead of always publishing position (0, 0, 0),
this node subscribes to /cmd_vel and integrates the velocity commands over
time to estimate where the robot actually is.

--- Why this is better than fake odometry ---
fake_odom.py told SLAM "the robot hasn't moved" on every tick. SLAM then had
to figure out the robot's position purely from LiDAR scan-matching, which
drifts over time and causes ghosting/smearing in the map.

This node gives SLAM a second source of information: "based on what commands
were sent to the motors, the robot is probably around here." SLAM then fuses
that estimate with scan-matching to produce a cleaner map.

--- Limitation ---
Dead-reckoning is not perfect. It assumes the motors actually achieved the
commanded speed, and that the wheels don't slip. In practice there's error.
But even an imperfect estimate is much better than always publishing zero.

--- What is published ---
1. TF transform: odom -> base_link (required by SLAM Toolbox)
2. nav_msgs/Odometry on /odom (standard ROS odometry topic)

--- How position is estimated ---
Every tick (50 Hz), we look at the last velocity command received on /cmd_vel:
  vx    = linear.x   (forward/backward speed in m/s, robot frame)
  vy    = linear.y   (strafe speed in m/s, robot frame  -  always 0 for arrow_teleop)
  omega = angular.z  (rotation speed in rad/s)

We convert from robot frame to world frame:
  x_dot = vx * cos(heading) - vy * sin(heading)
  y_dot = vx * sin(heading) + vy * cos(heading)

Then integrate:
  x       += x_dot * dt
  y       += y_dot * dt
  heading += omega * dt

--- Speed calibration ---
The LINEAR_SPEED and ANGULAR_SPEED values below should match the actual robot
speed in m/s and rad/s. If the map still drifts a lot, these may need tuning.
Measure roughly: time how long it takes the robot to travel 1 metre forward,
then LINEAR_SPEED ≈ 1.0 / that_time_in_seconds.

--- Usage ---
  python3 ~/dead_reckoning_odom.py

  (Run this instead of fake_odom.py  -  same place in the startup sequence)
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped


# ---------------------------------------------------------------------------
# Tunable parameters  -  adjust if the map still drifts badly
# ---------------------------------------------------------------------------

PUBLISH_HZ = 50           # how often to integrate and publish (Hz)
CMD_VEL_TIMEOUT = 0.5     # seconds  -  if no cmd_vel received in this time,
                          # treat velocity as zero (robot has stopped)


class DeadReckoningOdom(Node):
    def __init__(self):
        super().__init__('dead_reckoning_odom')

        # Current position estimate in the odom frame
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0   # radians, positive = counter-clockwise

        # Last velocity command received
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0
        self.last_cmd_time = self.get_clock().now()

        # Last time we integrated
        self.last_tick = self.get_clock().now()

        # Subscribe to velocity commands from teleop / nav
        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel', self._cmd_vel_callback, 10)

        # Publisher for the odometry topic
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        # TF broadcaster for odom -> base_link
        self.tf_broadcaster = TransformBroadcaster(self)

        # Integration timer
        self.timer = self.create_timer(1.0 / PUBLISH_HZ, self._tick)

        self.get_logger().info(
            'Dead-reckoning odometry ready  -  publishing odom -> base_link TF')

    def _cmd_vel_callback(self, msg: Twist):
        """Store the latest velocity command."""
        self.vx = msg.linear.x
        self.vy = msg.linear.y
        self.omega = msg.angular.z
        self.last_cmd_time = self.get_clock().now()

    def _tick(self):
        """Integrate velocity and publish TF + odometry."""
        now = self.get_clock().now()
        dt = (now - self.last_tick).nanoseconds / 1e9
        self.last_tick = now

        # If no cmd_vel has arrived recently, treat velocity as zero
        time_since_cmd = (now - self.last_cmd_time).nanoseconds / 1e9
        if time_since_cmd > CMD_VEL_TIMEOUT:
            vx, vy, omega = 0.0, 0.0, 0.0
        else:
            vx, vy, omega = self.vx, self.vy, self.omega

        # Integrate: convert robot-frame velocity to world-frame displacement
        cos_h = math.cos(self.heading)
        sin_h = math.sin(self.heading)

        self.x       += (vx * cos_h - vy * sin_h) * dt
        self.y       += (vx * sin_h + vy * cos_h) * dt
        self.heading += omega * dt

        # Keep heading in [-pi, pi] to avoid it growing forever
        self.heading = math.atan2(math.sin(self.heading), math.cos(self.heading))

        # Build quaternion from heading (rotation around Z axis only)
        qz = math.sin(self.heading / 2.0)
        qw = math.cos(self.heading / 2.0)

        # --- Publish TF: odom -> base_link ---
        tf_msg = TransformStamped()
        tf_msg.header.stamp = now.to_msg()
        tf_msg.header.frame_id = 'odom'
        tf_msg.child_frame_id = 'base_link'
        tf_msg.transform.translation.x = self.x
        tf_msg.transform.translation.y = self.y
        tf_msg.transform.translation.z = 0.0
        tf_msg.transform.rotation.x = 0.0
        tf_msg.transform.rotation.y = 0.0
        tf_msg.transform.rotation.z = qz
        tf_msg.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(tf_msg)

        # --- Publish /odom topic ---
        odom_msg = Odometry()
        odom_msg.header.stamp = now.to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'

        # Position
        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0
        odom_msg.pose.pose.orientation.z = qz
        odom_msg.pose.pose.orientation.w = qw

        # Velocity (in robot frame)
        odom_msg.twist.twist.linear.x = vx
        odom_msg.twist.twist.linear.y = vy
        odom_msg.twist.twist.angular.z = omega

        self.odom_pub.publish(odom_msg)


def main(args=None):
    rclpy.init(args=args)
    node = DeadReckoningOdom()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
