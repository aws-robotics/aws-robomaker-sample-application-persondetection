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
import yaml

from ament_index_python.packages import get_package_share_directory

import launch
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PythonExpression


def generate_launch_description():
    default_metrics_config = os.path.join(get_package_share_directory('person_detection_robot'),
                                          'config', 'cloudwatch_metrics_config.yaml')
    default_logs_config = os.path.join(get_package_share_directory('person_detection_robot'),
                                       'config', 'cloudwatch_logs_config.yaml')

    with open(default_metrics_config, 'r') as f:
      config_text = f.read()
    config_yaml = yaml.safe_load(config_text)
    default_aws_metrics_namespace = config_yaml['cloudwatch_metrics_collector']['ros__parameters']['aws_metrics_namespace']
    default_aws_region = config_yaml['cloudwatch_metrics_collector']['ros__parameters']['aws_client_configuration']['region']

    with open(default_logs_config, 'r') as f:
      config_text = f.read()
    config_yaml = yaml.safe_load(config_text)
    default_log_group_name = config_yaml['cloudwatch_logger']['ros__parameters']['log_group_name']

    default_aws_region = os.environ.get('ROS_AWS_REGION', default_aws_region)

    launch_actions = [
        launch.actions.DeclareLaunchArgument(
            name='aws_region',
            description='AWS region override, defaults to config .yaml if unset',
            default_value=default_aws_region
        ),
        launch.actions.DeclareLaunchArgument(
            name='launch_id',
            description='Used for resource name suffix if specified',
            default_value=launch.substitutions.EnvironmentVariable('LAUNCH_ID')
        ),
        launch.actions.DeclareLaunchArgument(
            name='metrics_node_name',
            default_value="cloudwatch_metrics_collector"
        ),
        launch.actions.DeclareLaunchArgument(
            name='aws_metrics_namespace',
            default_value=default_aws_metrics_namespace
        ),
        launch.actions.DeclareLaunchArgument(
            name='logger_node_name',
            default_value='cloudwatch_logger'
        ),
        launch.actions.DeclareLaunchArgument(
            name='log_group_name',
            default_value=default_log_group_name
        ),
        launch.actions.SetLaunchConfiguration(
            name='aws_metrics_namespace',
            value=PythonExpression(["'", LaunchConfiguration('aws_metrics_namespace'), "-", LaunchConfiguration('launch_id'), "'"]),
            condition=IfCondition(PythonExpression(["'true' if '", LaunchConfiguration('launch_id'), "' else 'false'"]))
        ),
        launch.actions.SetLaunchConfiguration(
            name='log_group_name',
            value=PythonExpression(["'", LaunchConfiguration('log_group_name'), "-", LaunchConfiguration('launch_id'), "'"]),
            condition=IfCondition(PythonExpression(["'true' if '", LaunchConfiguration('launch_id'), "' else 'false'"]))
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('health_metric_collector'), 'launch', 'health_metric_collector.launch.py')
            ),
            launch_arguments={
                'config_file': os.path.join(get_package_share_directory('person_detection_robot'), 'config', 'health_metrics_config.yaml')
            }.items()
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('cloudwatch_metrics_collector'), 'launch', 'cloudwatch_metrics_collector.launch.py')
            ),
            launch_arguments={
                'node_name': launch.substitutions.LaunchConfiguration('metrics_node_name'),
                'config_file': os.path.join(get_package_share_directory('person_detection_robot'), 'config', 'cloudwatch_metrics_config.yaml'),
                'aws_region': launch.substitutions.LaunchConfiguration('aws_region'),
                'aws_metrics_namespace': launch.substitutions.LaunchConfiguration('aws_metrics_namespace'),
            }.items()
        ),
        launch.actions.IncludeLaunchDescription(
            launch.launch_description_sources.PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('cloudwatch_logger'), 'launch', 'cloudwatch_logger.launch.py')
            ),
            launch_arguments={
                'node_name': launch.substitutions.LaunchConfiguration('logger_node_name'),
                'config_file': os.path.join(get_package_share_directory('person_detection_robot'), 'config', 'cloudwatch_logs_config.yaml'),
                'aws_region': launch.substitutions.LaunchConfiguration('aws_region'),
                'log_group_name': launch.substitutions.LaunchConfiguration('log_group_name'),
            }.items()
        ),
    ]
    ld = launch.LaunchDescription(launch_actions)
    return ld


if __name__ == '__main__':
    generate_launch_description()
