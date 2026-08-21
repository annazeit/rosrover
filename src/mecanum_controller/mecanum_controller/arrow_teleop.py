#!/usr/bin/env python3
"""
arrow_teleop.py  -  keyboard teleoperation using arrow keys.

Publishes geometry_msgs/Twist messages to /cmd_vel, which mecanum_node
subscribes to and translates into motor commands.

--- Controls ---
UP/DOWN arrows control the forward/backward axis (linear.x).
LEFT/RIGHT arrows control the rotation axis (angular.z).
Both axes are tracked independently, so holding UP while tapping LEFT/RIGHT
will drive the robot forward while turning  -  like WASD controls in a game.

--- How the key input works ---
The `curses` library puts the terminal into raw mode, meaning keypresses are
read immediately (no need to press Enter) and special keys like the arrows
are available as named constants (curses.KEY_UP etc.).

stdscr.nodelay(True) makes getch() non-blocking  -  it returns immediately
with -1 if no key is pressed, rather than waiting.

--- The HOLD_TIMEOUT ---
Over SSH, key-repeat events have small gaps between them. Without a hold
timeout, the node would send a stop command during each gap, making the
robot stutter. The fix: when a key is pressed, record the time. Keep sending
that command until HOLD_TIMEOUT seconds have passed with no new keypress.
Only then does that axis stop. Each axis has its own independent timer.

--- How this connects to the rest of the robot ---
This node only publishes to /cmd_vel. mecanum_node subscribes to /cmd_vel.
ROS2's topic system connects them automatically  -  neither node knows or cares
about the other directly.
"""

import curses
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


# ---------------------------------------------------------------------------
# Tunable parameters
# ---------------------------------------------------------------------------

LINEAR_SPEED  = 0.5  # m/s    -  negated because chassis is mounted reversed
ANGULAR_SPEED = 0.5   # rad/s  -  rotation speed (half of linear so turning is manageable)
HOLD_TIMEOUT  = 0.6   # s      -  how long to keep an axis active after last keypress
                      #         needs to be longer than SSH's initial key-repeat delay (~500ms)


class ArrowTeleop(Node):
    def __init__(self):
        super().__init__('arrow_teleop')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Arrow teleop ready  -  arrow keys to drive, q to quit')

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
        curses.curs_set(0)    # hide the blinking cursor
        stdscr.nodelay(True)  # getch() returns -1 immediately if no key pressed
        stdscr.timeout(50)    # unblock every 50 ms to drive the hold-timeout check

        stdscr.addstr(0, 0, 'Arrow Teleop  -  arrow keys to drive, q to quit')
        stdscr.addstr(2, 0, '  UP / DOWN        = forward / backward')
        stdscr.addstr(3, 0, '  LEFT / RIGHT     = rotate (combine with UP/DOWN to curve)')
        stdscr.addstr(4, 0, '  q                = quit')

        # Each axis is tracked independently so both can be active at once.
        # linear  : UP / DOWN  -> linear.x  (forward/backward)
        # angular : LEFT / RIGHT -> angular.z (rotation)
        linear_speed     = 0.0   # current value on the linear axis
        angular_speed    = 0.0   # current value on the angular axis
        linear_last_time  = 0.0  # last time an UP/DOWN key was seen
        angular_last_time = 0.0  # last time a LEFT/RIGHT key was seen

        while rclpy.ok():
            key = stdscr.getch()
            now = time.time()

            # Update whichever axis the key belongs to
            if key == curses.KEY_UP:
                linear_speed     = LINEAR_SPEED
                linear_last_time  = now
            elif key == curses.KEY_DOWN:
                linear_speed     = -LINEAR_SPEED
                linear_last_time  = now
            elif key == curses.KEY_LEFT:
                angular_speed    = ANGULAR_SPEED
                angular_last_time = now
            elif key == curses.KEY_RIGHT:
                angular_speed    = -ANGULAR_SPEED
                angular_last_time = now
            elif key == ord('q'):
                break

            # Each axis expires independently when its hold window runs out
            active_linear  = (now - linear_last_time)  < HOLD_TIMEOUT
            active_angular = (now - angular_last_time) < HOLD_TIMEOUT

            out_linear  = linear_speed  if active_linear  else 0.0
            out_angular = angular_speed if active_angular else 0.0

            node.publish(linear_x=out_linear, angular_z=out_angular)

            # Update the status line
            parts = []
            if active_linear:
                parts.append('FORWARD' if out_linear > 0 else 'BACKWARD')
            if active_angular:
                parts.append('LEFT' if out_angular > 0 else 'RIGHT')
            status = ' + '.join(parts) if parts else 'STOPPED'
            stdscr.addstr(6, 0, f'  {status:<25}')

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
