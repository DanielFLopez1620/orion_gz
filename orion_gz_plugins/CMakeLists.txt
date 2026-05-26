cmake_minimum_required(VERSION 3.8)
project(orion_gz_plugins)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)

find_package(gz-transport13 REQUIRED)
find_package(gz-msgs10 REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)
find_package(gz-gui8 REQUIRED)
find_package(gz-rendering8 REQUIRED)
find_package(gz-common5 REQUIRED COMPONENTS events)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

# Locate Qt6's rcc compiler directly (provided by qt6-base-dev).
# We avoid find_package(Qt6) here because gz-gui8 already loaded Qt6
# internally and a second find_package would cause duplicate-target errors.
find_program(QT6_RCC
    NAMES rcc rcc6
    HINTS /usr/lib/qt6/libexec
          /usr/lib/x86_64-linux-gnu/qt6/libexec
    REQUIRED)
message(STATUS "Found Qt6 rcc: ${QT6_RCC}")

# ── Emotion texture generation ────────────────────────────────────────────────
set(EMOTIONS_HPP
    ${CMAKE_CURRENT_SOURCE_DIR}/../../orion_common/orion_base/orion_interaction_micro_ros/lib/screen/emotions.hpp)
set(TEXTURES_DIR ${CMAKE_CURRENT_BINARY_DIR}/textures)

set(TEXTURE_OUTPUTS "")
foreach(i RANGE 0 7)
    list(APPEND TEXTURE_OUTPUTS ${TEXTURES_DIR}/emotion_${i}.png)
endforeach()

add_custom_command(
    OUTPUT  ${TEXTURE_OUTPUTS}
    COMMAND ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/scripts/gen_emotion_textures.py
            ${EMOTIONS_HPP}
            ${TEXTURES_DIR}
    DEPENDS ${EMOTIONS_HPP}
            ${CMAKE_CURRENT_SOURCE_DIR}/scripts/gen_emotion_textures.py
    COMMENT "Generating emotion textures from emotions.hpp"
)
add_custom_target(emotion_textures ALL DEPENDS ${TEXTURE_OUTPUTS})

install(
    FILES   ${TEXTURE_OUTPUTS}
    DESTINATION share/${PROJECT_NAME}/textures
)

# ── EmotionColorPlugin (GUI Plugin) ───────────────────────────────────────────
set(COLOR_QRC_IN  ${CMAKE_CURRENT_SOURCE_DIR}/res/EmotionColorPlugin.qrc)
set(COLOR_QRC_OUT ${CMAKE_CURRENT_BINARY_DIR}/qrc_EmotionColorPlugin.cpp)

add_custom_command(
  OUTPUT  ${COLOR_QRC_OUT}
  COMMAND ${QT6_RCC} --output ${COLOR_QRC_OUT} ${COLOR_QRC_IN}
  DEPENDS ${COLOR_QRC_IN}
          ${CMAKE_CURRENT_SOURCE_DIR}/res/EmotionColorPlugin.qml
  COMMENT "Compiling Qt resources for EmotionColorPlugin"
)

add_library(EmotionColorPlugin SHARED
  src/EmotionColorPlugin.cpp
  ${COLOR_QRC_OUT}
)
target_include_directories(EmotionColorPlugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(EmotionColorPlugin
  gz-gui8::gz-gui8
  gz-rendering8::gz-rendering8
  gz-transport13::gz-transport13
  gz-msgs10::gz-msgs10
  gz-plugin2::register
)

# ── EmotionDisplayPlugin (GUI Plugin, texture-based) ─────────────────────────
set(DISPLAY_QRC_IN  ${CMAKE_CURRENT_SOURCE_DIR}/res/EmotionDisplayPlugin.qrc)
set(DISPLAY_QRC_OUT ${CMAKE_CURRENT_BINARY_DIR}/qrc_EmotionDisplayPlugin.cpp)

add_custom_command(
  OUTPUT  ${DISPLAY_QRC_OUT}
  COMMAND ${QT6_RCC} --output ${DISPLAY_QRC_OUT} ${DISPLAY_QRC_IN}
  DEPENDS ${DISPLAY_QRC_IN}
          ${CMAKE_CURRENT_SOURCE_DIR}/res/EmotionDisplayPlugin.qml
  COMMENT "Compiling Qt resources for EmotionDisplayPlugin"
)

add_library(EmotionDisplayPlugin SHARED
  src/EmotionDisplayPlugin.cpp
  ${DISPLAY_QRC_OUT}
)
target_include_directories(EmotionDisplayPlugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(EmotionDisplayPlugin
  gz-gui8::gz-gui8
  gz-rendering8::gz-rendering8
  gz-transport13::gz-transport13
  gz-msgs10::gz-msgs10
  gz-plugin2::register
  ament_index_cpp::ament_index_cpp
)
add_dependencies(EmotionDisplayPlugin emotion_textures)

# ── TouchSensorPlugin (GUI Plugin) ────────────────────────────────────────────
# gz::gui::Plugin requires a QML file embedded as a Qt resource.
# We compile the .qrc manually with rcc to avoid find_package(Qt6) conflicts.
set(TOUCH_QRC_IN  ${CMAKE_CURRENT_SOURCE_DIR}/res/TouchSensorPlugin.qrc)
set(TOUCH_QRC_OUT ${CMAKE_CURRENT_BINARY_DIR}/qrc_TouchSensorPlugin.cpp)

add_custom_command(
  OUTPUT  ${TOUCH_QRC_OUT}
  COMMAND ${QT6_RCC} --output ${TOUCH_QRC_OUT} ${TOUCH_QRC_IN}
  DEPENDS ${TOUCH_QRC_IN}
          ${CMAKE_CURRENT_SOURCE_DIR}/res/TouchSensorPlugin.qml
  COMMENT "Compiling Qt resources for TouchSensorPlugin"
)

add_library(TouchSensorPlugin SHARED
  src/TouchSensorPlugin.cpp
  ${TOUCH_QRC_OUT}
)
target_include_directories(TouchSensorPlugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(TouchSensorPlugin
  gz-gui8::gz-gui8
  gz-rendering8::gz-rendering8
  gz-transport13::gz-transport13
  gz-msgs10::gz-msgs10
  gz-plugin2::register
  gz-common5::gz-common5-events
)

# ── Install ───────────────────────────────────────────────────────────────────
install(
  TARGETS EmotionColorPlugin EmotionDisplayPlugin TouchSensorPlugin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin
)

install(
  DIRECTORY include/
  DESTINATION include
)

install(
  DIRECTORY models/
  DESTINATION share/${PROJECT_NAME}/models
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
