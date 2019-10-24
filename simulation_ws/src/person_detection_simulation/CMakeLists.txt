cmake_minimum_required(VERSION 3.5)
project(person_detection_simulation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch routes param
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
