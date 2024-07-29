import rclpy
from rclpy.node import Node
from turtle_controller_interfaces.srv import FindClosestWall
from sensor_msgs.msg import LaserScan



class WallFinderServer(Node):
    def __init__(self):
        super().__init__("wall_finder_server")
        self.get_logger().info("running node")
        self._service = self.create_service(FindClosestWall, 'find_closest_wall', self.handle_wall_request)
        self._subscriber = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        self.lidar_data = None

    

    def scan_callback(self, msg):
        
        self.lidar_data = msg

    def handle_wall_request(self, request, response):
        response.angle = self.lidar_data.ranges.index(min(self.lidar_data.ranges))
        response.success = True
        self.get_logger().info(f"sent {response.angle}")
        return response

def main(args=None):

    rclpy.init(args=args)
    server_node = WallFinderServer()
    rclpy.spin(server_node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
