# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/apache2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import os
import yaml
import launch

import launch_ros.actions
from launch.substitutions import PythonExpression
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    kvs_config_file_path = os.path.join(get_package_share_directory('person_detection_robot'),
        'config', 'kvs_config.yaml')
    h264_encoder_config_file_path = os.path.join(get_package_share_directory('person_detection_robot'),
        'config', 'h264_encoder_config.yaml')

    with open(kvs_config_file_path, 'r') as f:
        config_text = f.read()
    config_yaml = yaml.safe_load(config_text)

    default_aws_region = config_yaml['kinesis_video_streamer']['ros__parameters']['aws_client_configuration']['region']
    default_stream_name = config_yaml['kinesis_video_streamer']['ros__parameters']['kinesis_video']['stream0']['stream_name']
    default_rekognition_data_stream = config_yaml['kinesis_video_streamer']['ros__parameters']['kinesis_video']['stream0']['rekognition_data_stream']

    default_aws_region = os.environ.get('ROS_AWS_REGION', default_aws_region)

    launch_actions = [
        launch.actions.DeclareLaunchArgument(
            name='aws_region',
            description='AWS region override, defaults to config .yaml if not set',
            default_value=default_aws_region
        ),
        launch.actions.DeclareLaunchArgument(
            name='launch_id',
            description='Used for resource name suffix if specified',
            default_value=launch.substitutions.EnvironmentVariable('LAUNCH_ID')
        ),
        launch.actions.DeclareLaunchArgument(
            name='stream_name',
            default_value=default_stream_name
        ),
        launch.actions.DeclareLaunchArgument(
            name='rekognition_data_stream',
            default_value=default_rekognition_data_stream
        ),
        launch.actions.DeclareLaunchArgument(
            name='kinesis_node_name',
            default_value='kinesis_video_streamer'
        ),
        launch.actions.DeclareLaunchArgument(
            name='h264_node_name',
            default_value='h264_video_encoder'
        ),
        launch.actions.DeclareLaunchArgument(
            name='image_transport',
            default_value='raw'
        ),
        launch.actions.SetLaunchConfiguration(
            name='stream_name',
            value=PythonExpression(["'", LaunchConfiguration('stream_name'), "-", LaunchConfiguration('launch_id'), "'"]),
            condition=IfCondition(PythonExpression(["'true' if '", LaunchConfiguration('launch_id'), "' else 'false'"]))
        ),
        launch.actions.SetLaunchConfiguration(
            name='rekognition_data_stream',
            value=PythonExpression(["'", LaunchConfiguration('rekognition_data_stream'), "-", LaunchConfiguration('launch_id'), "'"]),
            condition=IfCondition(PythonExpression(["'true' if '", LaunchConfiguration('launch_id'), "' else 'false'"]))
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('h264_video_encoder'), 'launch', 'h264_video_encoder_launch.py')
            ),
            launch_arguments={
                'node_name': launch.substitutions.LaunchConfiguration('h264_node_name'),
                'config': h264_encoder_config_file_path, 
                'image_transport': launch.substitutions.LaunchConfiguration('image_transport'),
            }.items()
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('kinesis_video_streamer'), 'launch', 'kinesis_video_streamer.launch.py')
            ),
            launch_arguments={
                'node_name': launch.substitutions.LaunchConfiguration('kinesis_node_name'),
                'config': kvs_config_file_path,
                'aws_region': launch.substitutions.LaunchConfiguration('aws_region'),
                'stream_name': launch.substitutions.LaunchConfiguration('stream_name'),
                'rekognition_data_stream': launch.substitutions.LaunchConfiguration('rekognition_data_stream')
            }.items()
        )
    ]

    ld = launch.LaunchDescription(launch_actions)

    return ld


if __name__ == "__main__":
    generate_launch_description()
