#!/usr/bin/env python3
"""
mecanum_node.py — ROS2 motor controller for a 4-wheel mecanum drive robot.

Subscribes to /cmd_vel (geometry_msgs/Twist) and drives four motors via two
L298N motor driver boards connected to the Jetson's 40-pin GPIO header.

--- Mecanum wheel kinematics ---
A mecanum wheel has rollers mounted at 45°. By varying the speed and direction
of each wheel independently, the robot can move in any direction (strafe, rotate,
diagonal) without turning first.

Given a Twist command with:
  vx  = linear.x  (forward/backward, m/s)
  vy  = linear.y  (strafe left/right, m/s)
  wz  = angular.z (rotate, rad/s)

Each wheel's required speed is:
  FL =  vx - vy - wz
  FR =  vx + vy + wz
  RL =  vx + vy - wz
  RR =  vx - vy + wz

We only have direction control (no PWM speed), so we use the sign of each
value: positive = forward, negative = backward, near-zero = stop.

--- GPIO setup on the Yahboom Jetson Orin Nano Super ---
The standard Jetson.GPIO library shows a warning on Yahboom's carrier board
and is unreliable. More importantly, the Jetson Orin's PADCTL (pad control)
registers default to a high-impedance state after boot — the GPIO controller
can write a signal, but it won't appear on the physical pin until the pad is
configured.

Fix: before running this node, run setup_gpio.sh (or the 8 busybox devmem
commands manually) to write 0x5 to each GPIO pin's PADCTL register. This
routes the GPIO signal to the physical pad. The setting persists until reboot.

See startup_guide.md for the full startup sequence.

--- L298N wiring ---
ENA and ENB jumpers stay ON on both boards (full speed, no PWM).

L298N #1 (left side motors):
  IN1/IN2 → BOARD pins 29/31 → OUT1/OUT2 → RL (rear left) motor
  IN3/IN4 → BOARD pins 37/38 → OUT3/OUT4 → FL (front left) motor

L298N #2 (right side motors):
  IN1/IN2 → BOARD pins 35/40 → OUT1/OUT2 → FR (front right) motor
  IN3/IN4 → BOARD pins 11/13 → OUT3/OUT4 → RR (rear right) motor

Note: FL and RL motor wires are physically connected with reversed polarity
compared to the right side. This is corrected in software by swapping the
IN_A/IN_B arguments when calling _set_motor() for those two motors.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

try:
    import Jetson.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    # Allows the node to run (without motor output) on a PC for testing
    GPIO_AVAILABLE = False


# ---------------------------------------------------------------------------
# GPIO pin numbers (Jetson BOARD numbering, i.e. physical pin position)
# ---------------------------------------------------------------------------

# L298N #1 — left side
RL_IN1 = 29   # rear left,  direction A
RL_IN2 = 31   # rear left,  direction B
FL_IN1 = 37   # front left, direction A
FL_IN2 = 38   # front left, direction B

# L298N #2 — right side
FR_IN1 = 35   # front right, direction A
FR_IN2 = 40   # front right, direction B
RR_IN1 = 11   # rear right,  direction A
RR_IN2 = 13   # rear right,  direction B

ALL_PINS = [RL_IN1, RL_IN2, FL_IN1, FL_IN2, FR_IN1, FR_IN2, RR_IN1, RR_IN2]


class MecanumController(Node):
    def __init__(self):
        super().__init__('mecanum_controller')
        self._setup_gpio()
        self.subscription = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.get_logger().info('Mecanum controller ready — listening on /cmd_vel')

    # ------------------------------------------------------------------
    # GPIO setup
    # ------------------------------------------------------------------

    def _setup_gpio(self):
        if not GPIO_AVAILABLE:
            self.get_logger().warn(
                'Jetson.GPIO not found — running in simulation mode (no motor output)')
            return
        GPIO.setmode(GPIO.BOARD)          # use physical pin numbers
        for pin in ALL_PINS:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        self.get_logger().info('GPIO initialised')

    # ------------------------------------------------------------------
    # Motor control
    # ------------------------------------------------------------------

    def _set_motor(self, in_a, in_b, speed):
        """
        Drive one motor channel on an L298N.

        in_a, in_b : the two GPIO pins connected to this motor's IN terminals
        speed      : positive = forward, negative = backward, ~0 = coast/stop

        The L298N H-bridge works like this:
          in_a HIGH, in_b LOW  → motor spins one way
          in_a LOW,  in_b HIGH → motor spins the other way
          both LOW             → motor coasts (no power)
        """
        if not GPIO_AVAILABLE:
            return
        if speed > 0.1:
            GPIO.output(in_a, GPIO.HIGH)
            GPIO.output(in_b, GPIO.LOW)
        elif speed < -0.1:
            GPIO.output(in_a, GPIO.LOW)
            GPIO.output(in_b, GPIO.HIGH)
        else:
            GPIO.output(in_a, GPIO.LOW)
            GPIO.output(in_b, GPIO.LOW)

    def cmd_vel_callback(self, msg: Twist):
        """
        Called every time a Twist message arrives on /cmd_vel.
        Converts the velocity command into individual wheel directions.
        """
        vx = msg.linear.x    # forward (+) / backward (-)
        vy = msg.linear.y    # strafe left (+) / right (-)
        wz = msg.angular.z   # rotate counter-clockwise (+) / clockwise (-)

        # Mecanum kinematics — see module docstring for derivation
        fl = vx - vy - wz
        fr = vx + vy + wz
        rl = vx + vy - wz
        rr = vx - vy + wz

        self.get_logger().debug(
            f'cmd_vel → FL={fl:.2f}  FR={fr:.2f}  RL={rl:.2f}  RR={rr:.2f}')

        # FL and RL have reversed polarity wiring, so in_a/in_b are swapped
        self._set_motor(FL_IN2, FL_IN1, fl)   # swapped
        self._set_motor(FR_IN1, FR_IN2, fr)
        self._set_motor(RL_IN2, RL_IN1, rl)   # swapped
        self._set_motor(RR_IN1, RR_IN2, rr)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def _stop_all(self):
        """Set all motor pins LOW so wheels stop immediately."""
        if not GPIO_AVAILABLE:
            return
        for pin in ALL_PINS:
            GPIO.output(pin, GPIO.LOW)

    def destroy_node(self):
        self._stop_all()
        if GPIO_AVAILABLE:
            GPIO.cleanup()
        self.get_logger().info('Shutdown — motors stopped, GPIO cleaned up')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MecanumController()
    try:
        rclpy.spin(node)        # block here, processing callbacks
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
