import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/rony/Rony-TurtleBot-Session7/ros2_ws/src/install/turtle_controller'
