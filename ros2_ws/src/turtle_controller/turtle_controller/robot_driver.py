import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import time

class RobotDriver(Node):
    FRONT_INDEX = 355
    def __init__(self):
        super().__init__('driver')
        self.turning = False
        self.firstTime = True
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10)
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        
        
    def turn_90_degrees(self):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.5236
        self.publisher.publish(twist)
        self.get_logger().info("Turning right")
        time.sleep(3) 
        twist.angular.z = 0.0
        twist.linear.x = 0.0
        self.get_logger().info("Stopping turn")
        self.publisher.publish(twist)

    def scan_callback(self, msg):
        if not self.turning:
            self.control_robot(msg)

    def control_robot(self, msg):
        twist = Twist()
        distance = msg.ranges[self.FRONT_INDEX]
        self.get_logger().info(f"{distance}")
        if distance > 0.5:
            self.get_logger().info("Moving forward")
            twist.linear.x = 0.6
            twist.angular.z = 0.0
            self.publisher.publish(twist)
        else:
            self.get_logger().info("Close to wall, stopping and turning")
            if self.firstTime:
                self.get_logger().info(f"Index: {msg.ranges.index(distance)}")
                self.firstTime = False
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.publisher.publish(twist)
            self.turning = True
            self.turn_90_degrees()
            self.turning = False
            self.get_logger().info("Pausing after turn")
            time.sleep(1)  # Pause for a short time after turning to avoid immediate re-detection of the wall

def main(args=None):
    rclpy.init(args=args)
    node = RobotDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
