#!/usr/bin/env python3
"""
arrow_teleop.py — keyboard teleoperation using arrow keys.

Publishes geometry_msgs/Twist messages to /cmd_vel, which mecanum_node
subscribes to and translates into motor commands.

--- How the key input works ---
The `curses` library puts the terminal into raw mode, meaning keypresses are
read immediately (no need to press Enter) and special keys like the arrows
are available as named constants (curses.KEY_UP etc.).

stdscr.nodelay(True) makes getch() non-blocking — it returns immediately
with -1 if no key is pressed, rather than waiting.

--- The HOLD_TIMEOUT ---
Over SSH, key-repeat events have small gaps between them. Without a hold
timeout, the node would send a stop command during each gap, making the
robot stutter. The fix: when a key is pressed, record the time. Keep sending
that command until HOLD_TIMEOUT seconds have passed with no new keypress.
Only then do we actually stop. 400ms is long enough to bridge SSH key-repeat
gaps but short enough that the robot stops promptly when you lift your finger.

--- How this connects to the rest of the robot ---
This node only publishes to /cmd_vel. mecanum_node subscribes to /cmd_vel.
ROS2's topic system connects them automatically — neither node knows or cares
about the other directly. You could swap this for any other controller
(a joystick node, an autonomous planner, etc.) and mecanum_node would work
unchanged.
"""

import curses
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


# ---------------------------------------------------------------------------
# Tunable parameters
# ---------------------------------------------------------------------------

LINEAR_SPEED  = 0.5   # m/s  — forward / backward speed
ANGULAR_SPEED = 1.0   # rad/s — rotation speed
HOLD_TIMEOUT  = 0.4   # s    — how long to keep driving after last keypress


class ArrowTeleop(Node):
    def __init__(self):
        super().__init__('arrow_teleop')
        # Queue size 10: if the subscriber is slow, up to 10 messages buffer
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Arrow teleop ready — arrow keys to drive, q to quit')

    def publish(self, linear_x=0.0, angular_z=0.0):
        """Send a velocity command. Omitted fields default to zero."""
        msg = Twist()
        msg.linear.x  = linear_x
        msg.angular.z = angular_z
        self.pub.publish(msg)

    def stop(self):
        """Publish an all-zero Twist so the motors stop."""
        self.publish(0.0, 0.0)


def main(args=None):
    rclpy.init(args=args)
    node = ArrowTeleop()

    def run(stdscr):
        curses.curs_set(0)       # hide the blinking cursor
        stdscr.nodelay(True)     # getch() returns -1 immediately if no key pressed
        stdscr.timeout(50)       # also unblock every 50 ms (drives the hold-timeout check)

        # Print the key reference once — curses redraws only what changes after this
        stdscr.addstr(0, 0, 'Arrow Teleop — arrow keys to drive, q to quit')
        stdscr.addstr(2, 0, '  UP    = forward')
        stdscr.addstr(3, 0, '  DOWN  = backward')
        stdscr.addstr(4, 0, '  LEFT  = rotate left')
        stdscr.addstr(5, 0, '  RIGHT = rotate right')

        last_key      = None   # most recent arrow key pressed
        last_key_time = 0.0    # timestamp of that keypress

        while rclpy.ok():
            key = stdscr.getch()   # returns -1 if nothing pressed
            now = time.time()

            if key in (curses.KEY_UP, curses.KEY_DOWN,
                       curses.KEY_LEFT, curses.KEY_RIGHT):
                # A new arrow key — update what we're holding
                last_key      = key
                last_key_time = now
            elif key == ord('q'):
                break   # quit cleanly

            # Decide whether we're still within the hold window
            holding = (last_key is not None) and (now - last_key_time < HOLD_TIMEOUT)

            if holding:
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

            # Process any pending ROS2 callbacks (keeps the node alive)
            rclpy.spin_once(node, timeout_sec=0)

        node.stop()

    try:
        curses.wrapper(run)   # wrapper handles terminal setup/teardown automatically
    except KeyboardInterrupt:
        pass                  # Ctrl+C is a normal way to exit — not an error
    finally:
        node.stop()
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass   # rclpy may already be shut down if Ctrl+C hit at the wrong moment


if __name__ == '__main__':
    main()
