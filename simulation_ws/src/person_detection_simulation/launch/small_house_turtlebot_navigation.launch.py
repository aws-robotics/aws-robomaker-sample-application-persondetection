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

'''
A small house with a Turtlebot navigating to pre-determined
goals in a random order endlessly.
Note that navigation nodes are in the simulation application
as it uses a virtual map and should not be deployed to
the real robot.
'''
import os
import sys

import launch
import launch_ros.actions
from ament_index_python.packages import get_package_share_directory

TURTLEBOT3_MODEL = os.environ.get('TURTLEBOT3_MODEL', 'burger')

def generate_launch_description():
    turtlebot_urdf_file_name = 'turtlebot3_' + TURTLEBOT3_MODEL + '.urdf'
    turtlebot_urdf_file_path = os.path.join(get_package_share_directory('turtlebot3_description_reduced_mesh'), 'urdf', turtlebot_urdf_file_name)

    ld = launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(
            name='x_pos',
            default_value='3.5'
        ),
        launch.actions.DeclareLaunchArgument(
            name='y_pos',
            default_value='1.0'
        ),
        launch.actions.DeclareLaunchArgument(
            name='z_pos',
            default_value='0.0'
        ),
        launch.actions.DeclareLaunchArgument(
            name='yaw',
            default_value='0.0'
        ),
        launch.actions.DeclareLaunchArgument(
            name='gui',
            default_value='false'
        ),
        launch.actions.DeclareLaunchArgument(
            name='follow_route',
            default_value='true'
        ),
        launch.actions.DeclareLaunchArgument(
            name='use_sim_time',
            default_value='true'
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('person_detection_simulation'), 
                    'launch', 
                    'small_house.launch.py'
                )
            ),
            launch_arguments={
                'gui': launch.substitutions.LaunchConfiguration('gui'),
                'gazebo_model_path': os.path.split(get_package_share_directory('turtlebot3_description_reduced_mesh'))[0],
            }.items()
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('turtlebot3_bringup'),
                    'launch',
                    'turtlebot3_state_publisher.launch.py'
                )
            ),
            launch_arguments={'use_sim_time': launch.substitutions.LaunchConfiguration('use_sim_time')}.items()
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('person_detection_simulation'), 
                    'launch', 
                    'turtlebot3_navigation.launch.py'
                )
            ),
            launch_arguments={
                ## map_file path is set in turtlebot3_navigation.launch.py as '/tmp/maps' instead of "<package_name>.<relative path in install space>" due to limitations on string parameter size. 
                #'map_file': os.path.join(get_package_share_directory('person_detection_simulation'), 'maps', 'map.yaml'),
                'params': os.path.join(get_package_share_directory('person_detection_simulation'), 'param', TURTLEBOT3_MODEL + ".yaml"),
                'use_sim_time': launch.substitutions.LaunchConfiguration('use_sim_time')
            }.items()
        ),
        launch_ros.actions.Node(
            package='aws_robomaker_simulation_common',
            node_executable='route_manager',
            node_name='route_manager',
            output='screen',
            parameters=[{
                # Route file is passed as "<package_name>.<relative path in install space>" due to limitations on string parameter size.
                'route_file': '.'.join(['person_detection_simulation', os.path.join('routes', 'route.yaml')])
            }],
            condition=launch.conditions.IfCondition(
                launch.substitutions.LaunchConfiguration('follow_route'))
        )
    ])
    return ld


if __name__ == '__main__':
    generate_launch_description()
