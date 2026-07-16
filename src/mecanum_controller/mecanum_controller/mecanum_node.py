#!/usr/bin/env python3
"""
mecanum_node.py — Mecanum wheel motor controller
Subscribes to /cmd_vel and drives 4 motors via 2x L298N using Jetson.GPIO

TODO: GPIO logic to be filled in (Prompt 2)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MecanumController(Node):
    def __init__(self):
        super().__init__('mecanum_controller')
        self.get_logger().info('Mecanum controller node started — GPIO not yet configured')

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

    def cmd_vel_callback(self, msg: Twist):
        vx = msg.linear.x
        vy = msg.linear.y
        wz = msg.angular.z
        self.get_logger().info(f'cmd_vel received: vx={vx:.2f} vy={vy:.2f} wz={wz:.2f}')
        # Motor drive logic goes here (Prompt 2)

    def destroy_node(self):
        self.get_logger().info('Shutting down — motors stopped')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MecanumController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
