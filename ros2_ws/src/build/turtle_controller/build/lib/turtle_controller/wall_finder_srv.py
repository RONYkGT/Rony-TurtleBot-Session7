import rclpy
from rclpy.node import Node
from turtle_controller_interfaces.srv import FindClosestWall
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import matplotlib.pyplot as plt
import threading

class WallFinderServer(Node):

    def __init__(self):
        super().__init__("wall_finder_server")
        self.get_logger().info("Running node")

        self._service = self.create_service(FindClosestWall, 'find_closest_wall', self.handle_wall_request)
        self._scan_subscriber = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        self._odom_subscriber = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)

        self.lidar_data = None
        self.positions = []  # To store the robot's positions
        self.plot_thread = threading.Thread(target=self.plot_data)
        self.plot_thread.start()

    def scan_callback(self, msg):
        self.lidar_data = msg

    def odom_callback(self, msg):
        position = msg.pose.pose.position
        self.positions.append((position.x, position.y))

    def handle_wall_request(self, request, response):
        if self.lidar_data:
            closest_distance = min(self.lidar_data.ranges)
            response.angle = self.lidar_data.ranges.index(closest_distance)
            response.success = True
            self.get_logger().info(f"Closest wall angle: {response.angle}, Distance: {closest_distance}")
        else:
            response.success = False
            self.get_logger().info("No LIDAR data available.")
        return response

    def plot_data(self):
        plt.ion()
        fig, ax1 = plt.subplots(1, 1)

        while rclpy.ok():
            if len(self.positions) > 0:
                x_data, y_data = zip(*self.positions)
                ax1.clear()
                ax1.plot(x_data, y_data, 'b-')
                ax1.set_title('Robot Path')
                ax1.set_xlabel('X position')
                ax1.set_ylabel('Y position')

                plt.draw()
                plt.pause(0.1)

        plt.ioff()
        plt.show()

def main(args=None):
    rclpy.init(args=args)
    server_node = WallFinderServer()
    rclpy.spin(server_node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
