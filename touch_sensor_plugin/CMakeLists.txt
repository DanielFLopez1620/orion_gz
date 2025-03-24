cmake_minimum_required(VERSION 3.22.1)
project(touch_sensor_plugin)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(gz-cmake3 REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Add Gazebo dependencies
gz_find_package(gz-plugin3 REQUIRED COMPONENTS register)
set(GZ_PLUGIN_VER ${gz-plugin3_VERSION_MAJOR})

gz_find_package(gz-sim9 REQUIRED)
set(GZ_SIM_VER ${gz-sim9_VERSION_MAJOR})


add_library(TouchSensor SHARED src/touch_sensor.cc)
set_property(TARGET TouchSensor PROPERTY CXX_STANDARD 17)

target_link_libraries(TouchSensor 
    gz-plugin${GZ_PLUGIN_VER}::gz-plugin${GZ_PLUGIN_VER}
    gz-sim${GZ_SIM_VER}::gz-sim${GZ_SIM_VER})


ament_target_dependencies(${PROJECT_NAME}
  rclcpp
  std_msgs
)

install(TARGETS
  ${PROJECT_NAME}
  DESTINATION lib)

ament_package()
