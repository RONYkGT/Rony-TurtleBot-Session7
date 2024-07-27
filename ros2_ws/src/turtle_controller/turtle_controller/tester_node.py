import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import time

class TesterNode(Node):
    FRONT_INDEX = 355
    def __init__(self):
        super().__init__('tester')
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10)
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        
   

    def scan_callback(self, msg):
        min_range = msg.ranges.index(min(msg.ranges))
        max_range = msg.ranges.index(max(msg.ranges))
        print(f"Index of min range: {min_range}")
        print(f"Index of max range: {max_range}")
        

def main(args=None):
    rclpy.init(args=args)
    node = TesterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
