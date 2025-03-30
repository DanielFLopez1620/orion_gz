cmake_minimum_required(VERSION 3.11.1 FATAL_ERROR)

find_package(gz-cmake3 REQUIRED)

project(TouchSensorSystem)

gz_find_package(gz-plugin2 REQUIRED COMPONENTS register)
set(GZ_PLUGIN_VER ${gz-plugin2_VERSION_MAJOR})

gz_find_package(gz-sim8 REQUIRED)
set(GZ_SIM_VER ${gz-sim8_VERSION_MAJOR})

find_package(gz-sensors8 REQUIRED)
set(GZ_SENSORS_VER ${gz-sensors8_VERSION_MAJOR})

add_subdirectory(touch_sensor_custom)

add_library(TouchSensorSystem SHARED TouchSensorSystem.cc)
set_property(TARGET TouchSensorSystem PROPERTY CXX_STANDARD 17)
target_link_libraries(TouchSensorSystem
  PUBLIC gz-plugin${GZ_PLUGIN_VER}::gz-plugin${GZ_PLUGIN_VER}
  PUBLIC gz-sim${GZ_SIM_VER}::gz-sim${GZ_SIM_VER}
  PUBLIC gz-sensors${GZ_SENSORS_VER}::gz-sensors${GZ_SENSORS_VER}
  PUBLIC TouchSensorCustom
)

target_include_directories(TouchSensorSystem
  PUBLIC touch_sensor_custom)

  