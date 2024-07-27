import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, PoseStamped
import math
from math import *
import time
from nav_msgs.msg import Odometry

import tf2_ros
from geometry_msgs.msg import Quaternion
from tf2_geometry_msgs import do_transform_pose

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
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10)
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        self.initial_orientation = None
        self.target_orientation = None

        # For quaternion calculations
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer,self)

    def turn_90_degrees(self):
        # Create a quaternion representing a 90-degree rotation around Z
        q_rot = Quaternion(x=0.0, y=0.0, z=sin(pi/4), w=cos(pi/4))

        # Calculate target orientation
        target_pose = PoseStamped()
        target_pose.header.frame_id = 'base_link'  # Replace with your base frame
        target_pose.pose.orientation = self.initial_orientation

        try:
            transformed_pose = self.tf_buffer.transform(target_pose, 'odom')
            self.target_orientation = transformed_pose.pose.orientation
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            self.get_logger().error(f"Transform error: {e}")
            return

        # Control loop using quaternion difference and error
        while True:
            # Calculate quaternion error
            error_quaternion = quaternion_multiply(self.target_orientation, quaternion_inverse(self.current_orientation))

            # Convert quaternion error to angle
            _, _, error_angle = euler_from_quaternion(error_quaternion.x, error_quaternion.y, error_quaternion.z, error_quaternion.w)

            # Create Twist message
            twist = Twist()
            twist.angular.z = error_angle * 0.5  # Adjust angular speed as needed

            self.publisher.publish(twist)

            # Check if the robot is close enough to the target orientation
            if abs(error_angle) < 0.1:  # Adjust tolerance as needed
                break

        # Stop the robot
        twist.angular.z = 0.0
        self.publisher.publish(twist)

    def odom_callback(self, msg):
        # Extract position and orientation from odometry message
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        
        # Store current orientation
        self.current_orientation = orientation

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

def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1.w, q1.x, q1.y, q1.z
    w2, x2, y2, z2 = q2.w, q2.x, q2.y, q2.z
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return Quaternion(w=w, x=x, y=y, z=z)

def quaternion_inverse(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    norm = w*w + x*x + y*y + z*z
    return Quaternion(w=w/norm, x=-x/norm, y=-y/norm, z=-z/norm)

def euler_from_quaternion(x, y, z, w):
    t = 2.0  # 2.0 for the following calculation
    roll = math.atan2(t * (w * x + y * z), 1 - t * (x * x + y * y))
    pitch = math.asin(t * (w * y - x * z))
    yaw = math.atan2(t * (w * z + x * y), 1 - t * (y * y + z * z))
    return roll, pitch, yaw
