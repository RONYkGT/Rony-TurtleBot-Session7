import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from turtle_controller_interfaces.action import MeasureLapTime
import time

class LapTimeActionServer(Node):

    def __init__(self):
        super().__init__('lap_time_action_server')
        self._action_server = ActionServer(
            self,
            MeasureLapTime,
            'measure_lap_time',
            self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
            )

        self.subscription = self.create_subscription(String,'start_timer',self.timer_callback,10)
        self.turns = 0
        self.timer_started = False
        self.latest_lap_turn = 0

    def goal_callback(self, goal_request):
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    def timer_callback(self, msg):
        self.get_logger().info('Received timer')
        self.turns += 1

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        self.get_logger().info(f'Turns: {self.turns}')
        self.get_logger().info(f'timer started: {self.timer_started}')
        start_time = time.time()
        self.latest_lap_turn = self.turns
        while rclpy.ok():
            if self.turns_completed():
                self.timer_started = False
                total_time = time.time() - start_time
                result = MeasureLapTime.Result()
                result.total_time = total_time
                goal_handle.result = result
                goal_handle.succeed()
                
                self.get_logger().info(f'Lap completed, Time = {total_time} seconds')
                rclpy.spin_once(self)
                return result
            self.get_logger().info(f'Turns: {self.turns}')
            self.get_logger().info(f'Latest Turns: {self.latest_lap_turn}')
            self.get_logger().info(f'timer started: {self.timer_started}')
            self.timer_started = True
            elapsed_time = time.time() - start_time
            feedback = MeasureLapTime.Feedback()
            feedback.elapsed_time = elapsed_time
            goal_handle.publish_feedback(feedback)

            rclpy.spin_once(self)

    def turns_completed(self):
        return self.turns%4 == 2 and self.timer_started and self.turns != self.latest_lap_turn


def main(args=None):
    print("Node started")
    rclpy.init(args=args)
    node = LapTimeActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    print("Node stopped")

if __name__ == '__main__':
    main()