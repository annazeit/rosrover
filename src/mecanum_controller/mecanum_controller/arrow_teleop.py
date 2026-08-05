#!/usr/bin/env python3

import curses
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


LINEAR_SPEED  = 0.5   # m/s (forward / backward)
ANGULAR_SPEED = 1.0   # rad/s (rotate)
HOLD_TIMEOUT  = 0.4   # seconds — keep last command alive this long after keypress


class ArrowTeleop(Node):
    def __init__(self):
        super().__init__('arrow_teleop')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Arrow teleop ready')

    def publish(self, linear_x=0.0, angular_z=0.0):
        msg = Twist()
        msg.linear.x  = linear_x
        msg.angular.z = angular_z
        self.pub.publish(msg)

    def stop(self):
        self.publish(0.0, 0.0)


def main(args=None):
    rclpy.init(args=args)
    node = ArrowTeleop()

    def run(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)          # check keys every 50 ms

        stdscr.addstr(0, 0, 'Arrow Teleop — arrow keys to drive, q to quit')
        stdscr.addstr(2, 0, '  UP    = forward')
        stdscr.addstr(3, 0, '  DOWN  = backward')
        stdscr.addstr(4, 0, '  LEFT  = rotate left')
        stdscr.addstr(5, 0, '  RIGHT = rotate right')

        last_key      = None
        last_key_time = 0.0

        while rclpy.ok():
            key = stdscr.getch()
            now = time.time()

            if key in (curses.KEY_UP, curses.KEY_DOWN,
                       curses.KEY_LEFT, curses.KEY_RIGHT):
                last_key      = key
                last_key_time = now
            elif key == ord('q'):
                break

            # drive if a key was pressed recently, stop if the window expired
            if now - last_key_time < HOLD_TIMEOUT and last_key is not None:
                if last_key == curses.KEY_UP:
                    node.publish(linear_x=LINEAR_SPEED)
                    stdscr.addstr(7, 0, 'FORWARD      ')
                elif last_key == curses.KEY_DOWN:
                    node.publish(linear_x=-LINEAR_SPEED)
                    stdscr.addstr(7, 0, 'BACKWARD     ')
                elif last_key == curses.KEY_LEFT:
                    node.publish(angular_z=ANGULAR_SPEED)
                    stdscr.addstr(7, 0, 'ROTATE LEFT  ')
                elif last_key == curses.KEY_RIGHT:
                    node.publish(angular_z=-ANGULAR_SPEED)
                    stdscr.addstr(7, 0, 'ROTATE RIGHT ')
            else:
                node.stop()
                stdscr.addstr(7, 0, 'STOPPED      ')

            rclpy.spin_once(node, timeout_sec=0)

        node.stop()

    try:
        curses.wrapper(run)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
