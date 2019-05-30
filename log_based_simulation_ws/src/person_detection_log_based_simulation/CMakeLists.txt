cmake_minimum_required(VERSION 2.8.3)
project(person_detection_log_based_simulation)

find_package(catkin REQUIRED)
catkin_package()
install(PROGRAMS
        script/regression_test.py
        DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch
        DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
