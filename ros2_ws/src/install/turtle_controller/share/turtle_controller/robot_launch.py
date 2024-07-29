from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtle_controller',
            executable='wall_finder_server',
            name='wall_finder_server'
        ),
        Node(
            package='turtle_controller',
            executable='lap_action_srv',
            name='lap_action_srv'
        ),
        Node(
            package='turtle_controller',
            executable='lap_action_client',
            name='lap_action_client'
        ),
        Node(
            package='turtle_controller',
            executable='driver_node',
            name='driver_node'
        )
    ])