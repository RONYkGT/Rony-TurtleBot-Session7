import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import time

class RobotDriver(Node):
    FRONT_INDEX = 355
    LEFT_INDEX = 90
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
        self.publisher2 = self.create_publisher(String, 'start_timer', 10)



    def turn_90_degrees(self, msg):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = -0.5
        self.get_logger().info("Turning right")
        if not(90 <= msg.ranges.index(min(msg.ranges)) <= 105): #Repeats until the closest wall is on the left side
            self.publisher.publish(twist)
            self.get_logger().info(f"index of min range: {msg.ranges.index(min(msg.ranges))}" )
        else:
            twist.angular.z = 0.0
            twist.linear.x = 0.0
            self.get_logger().info("Stopping turn")
            self.publisher.publish(twist)
            self.turning = False
            emptymsg = String()
            emptymsg.data = ""
            self.publisher2.publish(emptymsg)
        
        
        

    def scan_callback(self, msg):
        if not self.turning:
            self.control_robot(msg)
        else:
            self.turn_90_degrees(msg)

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
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.publisher.publish(twist)
            self.turning = True

def main(args=None):
    rclpy.init(args=args)
    node = RobotDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
