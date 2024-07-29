import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from turtle_controller_interfaces.action import MeasureLapTime
import time
import os

class LapTimeActionClient(Node):

    def __init__(self):
        super().__init__('lap_time_action_client')
        self._action_client = ActionClient(self, MeasureLapTime, 'measure_lap_time')
        self.subscription = self.create_subscription(String, 'start_timer', self.timer_callback, 10)
        self.turns = 0
        self.laps = 0
        self.log_file_path = 'lap_times.log'  # Define the log file path

        # Ensure the log file exists
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w') as f:
                f.write("Lap Times:\n")

    def timer_callback(self, msg):
        self.turns += 1
        self.get_logger().info(f'Turns: {self.turns}')
        if self.turns == 2 or self.turns % 4 == 2:
            self.send_goal()

    def send_goal(self):
        self.get_logger().info('Sending goal request...')
        goal_msg = MeasureLapTime.Goal()
        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)
        self.get_logger().info('Waited for server...')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback received: Elapsed time = {feedback.elapsed_time} seconds')

    def get_result_callback(self, future):
        result = future.result().result
        total_time = result.total_time
        self.get_logger().info(f'Result received: Total lap time = {total_time} seconds')

        self.laps += 1
        # Log the result to a file
        self.log_result(total_time)

    def log_result(self, total_time):
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(f'Lap {self.laps}: {total_time} seconds\n')

def main(args=None):
    rclpy.init(args=args)
    node = LapTimeActionClient()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
