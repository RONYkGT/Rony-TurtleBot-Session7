import rclpy
from rclpy.node import Node
from turtle_controller_interfaces.srv import FindClosestWall
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class WallFinderServer(Node):
    def __init__(self):
        super().__init__("wall_finder_server")
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.DEBUG)
        self.get_logger().info("running node")
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self._service = self.create_service(FindClosestWall, 'find_closest_wall', self.handle_wall_request)
        self._subscriber = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        self.lidar_data = None

    def turn_to_angle(self, target_angle):
        self.get_logger().info("turning")
        if target_angle is None:
            return False

        # Calculate the angular velocity required
        twist_msg = Twist()
        twist_msg.angular.z = 0.3  # Adjust this value as needed
        self.publisher.publish(twist_msg)
        
        # Determine the threshold for stopping
        tolerance = 0.07  # Angle tolerance in radians
        start_time = self.get_clock().now()
        timeout = 20.0  # Maximum time to wait for the robot to turn (seconds)

        while rclpy.ok():
            current_time = self.get_clock().now()
            elapsed_time = (current_time - start_time).nanoseconds / 1e9
            closest_angle = self.get_closest_wall_angle()
            # Stop condition
            if elapsed_time >= timeout:
                self.get_logger().info("turning timeout")
                break

            # Check the current robot orientation
            # This is a simplified example; integrate actual feedback if available
            if abs(target_angle - self.get_closest_wall_angle) < tolerance:
                self.get_logger().info("turning point reached")
                break
        
        # Stop the robot
        twist_msg.angular.z = 0.0
        self.publisher.publish(twist_msg)
        
        self.get_logger().info(f'Turned to angle: {target_angle} radians')
        return True

    def get_closest_wall_angle(self):
        self.get_logger().info("getting closest angle")
        if self.lidar_data is None:
            self.get_logger().warn("LIDAR data not available")
            return 0.0

        ranges = self.lidar_data.ranges
        angle_min = self.lidar_data.angle_min
        angle_increment = self.lidar_data.angle_increment

        # Find the index of the minimum range
        min_index = min(
            (i for i in range(len(ranges)) if ranges[i] > self.lidar_data.range_min and ranges[i] < self.lidar_data.range_max),
            key=lambda i: ranges[i],
            default=None
        )

        if min_index is None:
            self.get_logger().warn("No valid wall detected")
            return 0.0

        # Calculate the angle of the minimum range
        min_angle = angle_min + min_index * angle_increment
        self.get_logger().info(f"min angle: {min_angle}")
        return min_angle

    def scan_callback(self, msg):
        #self.get_logger().info("getting lidar info")
        self.lidar_data = msg

    def handle_wall_request(self, request, response):
        angle = self.get_closest_wall_angle()
        self.turn_to_angle(angle)
        response.success = True
        return response

def main(args=None):

    rclpy.init(args=args)
    server_node = WallFinderServer()
    rclpy.spin(server_node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
