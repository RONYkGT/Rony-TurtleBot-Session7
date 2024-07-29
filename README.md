# Robot Control and Wall Following Project
## Introduction
This project is the assignment for session07 at inmind. It is based on Gazebo and serves the purpose of making the robot go to the nearest wall, and start moving along the walls, timing each lap and plotting the robots position
## Nodes
- `wall_finder_server`: Responsible for answering requests and sending the closest wall angle as a response to the client. It also manages matplotlib and plots the robot's position.

- `lap_action_srv`: Starts the timer after 2 turns initially and then every 4 turns and passes the time to the client.

- `lap_action_client`: Sends timer request after 2 turns initially and then every 4 turns and logs the timer in a text file in `src` every result.

- `robot_driver`: Responsible for turning to the closest wall initially then moving forward and turning right on each wall, while publishing each turn to the timers.
 
## Features
- Timer for each lap and logging it in a text file.
- Correctly finds the closest wall and turns to it efficiently
- Plots the position in a chart

## Usage
- **Prerequisites:** Gazebo and turtlebot simulation
- **Set up turtle model:**
    ```bash
    export TURTLEBOT3_MODEL=burger
    ```
- **Run Turtle Bot simulation:**
    ```bash
    ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage1.launch.py
    ```
- **Clone the repository**:
    ```bash
    git clone https://github.com/RONYkGT/Rony-TurtleBot-Session7.git
    ```
    then
    ```bash
    cd Rony-TurtleBot-Session7/ros2_ws/src/
    ```
- **Set up source**:
    ```bash
    source /opt/ros/humble/setup.bash 
    source install/setup.bash
    ```
- **Launch the nodes**:
     ```bash
    ros2 launch turtle_controller robot_launch.py
    ```
