cmake_minimum_required(VERSION 3.5)
project(person_detection_simulation)

find_package(cloudwatch_logger REQUIRED)
find_package(kinesis_video_streamer REQUIRED)
find_package(kinesis_video_msgs REQUIRED)
find_package(h264_video_encoder REQUIRED)
find_package(health_metric_collector REQUIRED)

install(DIRECTORY launch routes param
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
