cmake_minimum_required(VERSION 3.11.1 FATAL_ERROR)

find_package(gz-cmake3 REQUIRED)

project(Touch_sensor)

gz_find_package(gz-plugin2 REQUIRED COMPONENTS register)
set(GZ_PLUGIN_VER ${gz-plugin2_VERSION_MAJOR})

gz_find_package(gz-sim8 REQUIRED)
set(GZ_SIM_VER ${gz-sim8_VERSION_MAJOR})

add_library(TouchSensor SHARED TouchSensor.cc)
set_property(TARGET TouchSensor PROPERTY CXX_STANDARD 17)
target_link_libraries(TouchSensor
  gz-plugin${GZ_PLUGIN_VER}::gz-plugin${GZ_PLUGIN_VER}
  gz-sim${GZ_SIM_VER}::gz-sim${GZ_SIM_VER})