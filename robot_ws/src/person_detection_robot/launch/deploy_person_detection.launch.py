# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys

import launch_ros.actions
from ament_index_python.packages import get_package_share_directory

import launch
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'launch'))  # noqa


def generate_launch_description():

    #############################################
    # Turtlebot3 Deploy Person Detection Launch #
    #############################################

    #####################
    # TurtleBot3 Launch #
    #####################
    turtlebot3_bringup_dir = get_package_share_directory('turtlebot3_bringup')
    turtlebot3_bringup_launch = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(turtlebot3_bringup_dir, 'launch', 'robot.launch.py')))

    #################################
    # Get Raspicam Params from YAML #
    #################################
    #raspicam_params = os.path.join(
    #    get_package_share_directory('object_tracker_robot'),
    #    'config', 'raspicam_config.yaml'
    #)

    ########################################
    # Start getting images from the camera #
    ########################################
    run_pi_cam = DeclareLaunchArgument(
        name="run_pi_cam",
        default_value="False",
        description="Launch PI CAM")

    run_usb_cam = DeclareLaunchArgument(
        name="run_usb_cam",
        default_value="False",
        description="Launch USB CAM")

    raspicam_node = launch_ros.actions.Node(
        package='ros2_raspicam_node', node_executable='service', output='screen',
        node_name='ros2_raspicam_node',
        condition=launch.conditions.IfCondition(LaunchConfiguration("run_pi_cam")),
        name='ros2_raspicam_node',
        remappings=[('/raspicam_node/image', '/camera/image_raw')])

    usbcam_node = launch_ros.actions.Node(
        package='image_tools', node_executable='cam2image', output='screen',
        node_name='cam2image',
        condition=launch.conditions.IfCondition(LaunchConfiguration("run_usb_cam")),
        name='cam2image',
        remappings=[('/image', '/camera/image_raw')])

    ##############################
    # Start the Person Detection #
    ##############################
    person_detection_robot_dir = get_package_share_directory('person_detection_robot')
    person_detection_robot_launch = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(person_detection_robot_dir, 'launch', 'person_detection.launch.py')),
        launch_arguments={
            'use_sim_time': 'false',
            'use_polly': 'true'
        }.items())

    ld = LaunchDescription([
        turtlebot3_bringup_launch,
        person_detection_robot_launch,
        run_usb_cam,
        usbcam_node,
        run_pi_cam,
        raspicam_node
    ])

    return ld

if __name__ == '__main__':
    generate_launch_description()
