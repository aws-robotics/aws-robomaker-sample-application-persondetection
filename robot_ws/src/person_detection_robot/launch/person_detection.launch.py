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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'launch'))  # noqa


def generate_launch_description():

    ######################################
    # Turtlebot3 Person Detection Launch #
    ######################################
    use_sim_time_false = launch.actions.DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use sim time')

    use_polly = launch.actions.DeclareLaunchArgument(
        'use_polly',
        default_value='false',
        description='Use AWS Polly Service')

    ################################################
    # TTS Polly Server and rekognition Node Launch #
    ################################################
    rekognize_node = launch_ros.actions.Node(
        package='person_detection_robot', node_executable='rekognize', output='screen',
        node_name='rekognize',
        name='rekognize',
        parameters=[{'use_sim_time': launch.substitutions.LaunchConfiguration('use_sim_time')}]
    )

    tts_dir = get_package_share_directory('tts')
    tts_launch = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(tts_dir, 'tts.launch.py')),
        condition=launch.conditions.IfCondition(
            launch.substitutions.LaunchConfiguration('use_polly'))
    )

    rekognize_tts_node = launch_ros.actions.Node(
        package='person_detection_robot', node_executable='rekognize_tts', output='screen',
        node_name='rekognize_tts',
        name='rekognize_tts',
        parameters=[{'use_sim_time': launch.substitutions.LaunchConfiguration('use_sim_time')}],
        condition=launch.conditions.IfCondition(
            launch.substitutions.LaunchConfiguration('use_polly'))
    )

    #########################
    # AWS Monitoring Launch #
    #########################
    person_detection_robot_dir = get_package_share_directory('person_detection_robot')
    monitoring_launch = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(person_detection_robot_dir, 'launch', 'monitoring.launch.py')))

    #############################
    # AWS Kinesis Stream Launch #
    #############################
    kinesis_launch = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(person_detection_robot_dir, 'launch', 'kinesis.launch.py')))

    ld = LaunchDescription([use_sim_time_false,
                            use_polly,
                            rekognize_node,
                            rekognize_tts_node,
                            tts_launch,
                            monitoring_launch,
                            kinesis_launch])

    return ld

if __name__ == '__main__':
    generate_launch_description()
