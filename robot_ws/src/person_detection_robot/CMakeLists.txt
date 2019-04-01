################################################################################
# Set minimum required version of cmake, project name and compile options
################################################################################
cmake_minimum_required(VERSION 2.8.3)
project(person_detection_robot)

################################################################################
# Find catkin packages and libraries for catkin and system dependencies
################################################################################
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  geometry_msgs
  nav_msgs
  message_generation
  cloudwatch_logger
  kinesis_video_streamer
  kinesis_video_msgs
  h264_video_encoder
)

################################################################################
# Setup for python modules and scripts
################################################################################
catkin_python_setup()

################################################################################
# Declare ROS messages, services and actions
################################################################################
#add_action_files(
#  FILES
#  Turtlebot3.action
#)

#generate_messages(
#  DEPENDENCIES
#  std_msgs
#  geometry_msgs
#  nav_msgs
#)

################################################################################
# Declare ROS dynamic reconfigure parameters
################################################################################

################################################################################
# Declare catkin specific configuration to be passed to dependent projects
################################################################################
catkin_package(
  DEPENDS
    rospy
    std_msgs
    geometry_msgs
    nav_msgs
    message_runtime
    cloudwatch_logger
    kinesis_video_streamer
    kinesis_video_msgs
    h264_video_encoder
)

################################################################################
# Build
################################################################################
include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)

################################################################################
# Install
################################################################################
catkin_install_python(PROGRAMS 
  nodes/rotate
  nodes/rekognize
  nodes/rekognize_tts
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch config
	DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

################################################################################
# Test
################################################################################

