import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from turtle_controller_interfaces.srv import FindClosestWall
import time

class RobotDriver(Node):
    FRONT_INDEX = 355
    LEFT_INDEX = 90
    def __init__(self):
        super().__init__('driver')
        self.turning = False
        self.firstTime = True
        self.closest_angle = 0
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10)
        self.cli = self.create_client(FindClosestWall, 'find_closest_wall')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.publisher2 = self.create_publisher(String, 'start_timer', 10)


    def send_request(self):
        req = FindClosestWall.Request()
        # Populate request fields if necessary
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


    def turn_90_degrees(self, msg):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = -0.5
        self.get_logger().info("Turning right")
        if not(95 <= msg.ranges.index(min(msg.ranges)) <= 105): #Repeats until the closest wall is on the left side
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
        
        
    def turn_to_angle(self,msg):
        if (msg.ranges[self.closest_angle] - msg.ranges[0]) < 0.2: # angle is almost the same as front
            self.firstTime = False
            return
        twist = Twist()
        twist.linear.x = 0.0
        self.get_logger().info("Turning to closest angle")
        if 355 > self.closest_angle >= 90:
            twist.angular.z = 0.5 # turn left
            self.get_logger().info("Turning left")

        elif 90 > self.closest_angle > 5:
            twist.angular.z = -0.5 # turn right
            self.get_logger().info("Turning right1")
            
        else:
            self.firstTime = False
            return
        
        min_range_idx = msg.ranges.index(min(msg.ranges))
        if not(min_range_idx <= 5 or min_range_idx >= 355): #Repeats until the closest wall is on the left side
            self.publisher.publish(twist)
            self.get_logger().info(f"index of min range: {msg.ranges.index(min(msg.ranges))}" )
        else:
            twist.angular.z = 0.0
            twist.linear.x = 0.0
            self.get_logger().info("Stopping initial turn")
            self.publisher.publish(twist)
            self.firstTime = False


        
        pass

    def scan_callback(self, msg):
        if self.firstTime:
            self.turn_to_angle(msg)
            return
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
            twist.linear.x = 0.4
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
    response = node.send_request()
    if response.success:
        print('Object success:', response.success)
        print('Object angle:', response.angle)
        node.closest_angle = response.angle
    else:
        print('Service call failed')
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
