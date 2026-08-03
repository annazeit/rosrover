#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

try:
    import Jetson.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

# Direction pins only — ENA/ENB jumpers stay ON for full speed
# L298N #1: IN1/IN2 (pins 29/31) → OUT1/OUT2 → RL motor
#           IN3/IN4 (pins 37/38) → OUT3/OUT4 → FL motor
# L298N #2: IN1/IN2 (pins 35/40) → OUT1/OUT2 → FR motor
#           IN3/IN4 (pins 11/13) → OUT3/OUT4 → RR motor
FL_IN1 = 37
FL_IN2 = 38
RL_IN3 = 29
RL_IN4 = 31
FR_IN1 = 35
FR_IN2 = 40
RR_IN3 = 11
RR_IN4 = 13


class MecanumController(Node):
    def __init__(self):
        super().__init__('mecanum_controller')
        self._setup_gpio()
        self.subscription = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.get_logger().info('Mecanum controller ready')

    def _setup_gpio(self):
        if not GPIO_AVAILABLE:
            self.get_logger().warn('Jetson.GPIO not found — running without motors')
            return
        GPIO.setmode(GPIO.BOARD)
        for pin in [FL_IN1, FL_IN2, RL_IN3, RL_IN4,
                    FR_IN1, FR_IN2, RR_IN3, RR_IN4]:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        self.get_logger().info('GPIO initialised')

    def _set_motor(self, in_a, in_b, speed):
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
        vx = msg.linear.x
        vy = msg.linear.y
        wz = msg.angular.z
        fl = vx - vy - wz
        fr = vx + vy + wz
        rl = vx + vy - wz
        rr = vx - vy + wz
        self.get_logger().debug(f'FL={fl:.2f} FR={fr:.2f} RL={rl:.2f} RR={rr:.2f}')
        self._set_motor(FL_IN1, FL_IN2, fl)
        self._set_motor(FR_IN1, FR_IN2, fr)
        self._set_motor(RL_IN3, RL_IN4, rl)
        self._set_motor(RR_IN3, RR_IN4, rr)

    def _stop_all(self):
        if not GPIO_AVAILABLE:
            return
        for pin in [FL_IN1, FL_IN2, RL_IN3, RL_IN4,
                    FR_IN1, FR_IN2, RR_IN3, RR_IN4]:
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
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()