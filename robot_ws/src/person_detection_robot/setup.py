## ! DO NOT MANUALLY INVOKE THIS setup.py, USE CATKIN INSTEAD
## See http://ros.org/doc/api/catkin/html/user_guide/setup_dot_py.html

from distutils.core import setup
from setuptools import setup, find_packages

package_name = 'person_detection_robot'

setup(
    name=package_name,
    version='2.0.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    data_files=[
        ('share/' + package_name + '/launch', ['launch/person_detection.launch.py']),
        ('share/' + package_name + '/launch', ['launch/deploy_person_detection.launch.py']),
        ('share/' + package_name + '/launch', ['launch/monitoring.launch.py']),
        ('share/' + package_name + '/launch', ['launch/person_detection.launch.py']),
        ('share/' + package_name + '/launch', ['launch/kinesis.launch.py']),
        ('share/' + package_name + '/config', ['config/kvs_config.yaml']),
        ('share/' + package_name + '/config', ['config/h264_encoder_config.yaml']),
        ('share/' + package_name + '/config', ['config/cloudwatch_logs_config.yaml']),
        ('share/' + package_name + '/config', ['config/cloudwatch_metrics_config.yaml']),
        ('share/' + package_name + '/config', ['config/health_metrics_config.yaml']),
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='AWS RoboMaker',
    author_email='ros-contributions@amazon.com',
    maintainer='AWS RoboMaker',
    maintainer_email='ros-contributions@amazon.com',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description=(
        'AWS RoboMaker robot package with a rotating Turtlebot3'
    ),
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rotate = person_detection_robot.rotate:main',
            'rekognize = person_detection_robot.rekognize:main',
            'rekognize_tts = person_detection_robot.rekognize_tts:main'         
        ],
    },
)
