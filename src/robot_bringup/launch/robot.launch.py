"""
robot.launch.py — starts the full mecanum RC robot
Launches: mecanum_controller + teleop_twist_keyboard

TODO: teleop node to be enabled once GPIO logic is confirmed working (Prompt 3)
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    mecanum_node = Node(
        package='mecanum_controller',
        executable='mecanum_node',
        name='mecanum_controller',
        output='screen',
    )

    # Uncomment when ready to control with keyboard:
    # teleop_node = Node(
    #     package='teleop_twist_keyboard',
    #     executable='teleop_twist_keyboard',
    #     name='teleop_twist_keyboard',
    #     output='screen',
    #     prefix='xterm -e',
    # )

    return LaunchDescription([
        mecanum_node,
        # teleop_node,
    ])
