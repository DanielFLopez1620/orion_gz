cmake_minimum_required(VERSION 3.8)
project(orion_gz_plugins)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

find_package(gz-sim8 REQUIRED)
find_package(gz-transport13 REQUIRED)
find_package(gz-msgs10 REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)
find_package(gz-gui8 REQUIRED)
find_package(gz-rendering8 REQUIRED)
find_package(gz-common5 REQUIRED COMPONENTS events)

# Locate Qt6's rcc compiler directly (provided by qt6-base-dev).
# We avoid find_package(Qt6) here because gz-gui8 already loaded Qt6
# internally and a second find_package would cause duplicate-target errors.
find_program(QT6_RCC
    NAMES rcc rcc6
    HINTS /usr/lib/qt6/libexec
          /usr/lib/x86_64-linux-gnu/qt6/libexec
    REQUIRED)
message(STATUS "Found Qt6 rcc: ${QT6_RCC}")

# ── EmotionDisplayPlugin (GUI Plugin) ────────────────────────────────────────
set(EMOTION_QRC_IN  ${CMAKE_CURRENT_SOURCE_DIR}/res/EmotionDisplayPlugin.qrc)
set(EMOTION_QRC_OUT ${CMAKE_CURRENT_BINARY_DIR}/qrc_EmotionDisplayPlugin.cpp)

add_custom_command(
  OUTPUT  ${EMOTION_QRC_OUT}
  COMMAND ${QT6_RCC} --output ${EMOTION_QRC_OUT} ${EMOTION_QRC_IN}
  DEPENDS ${EMOTION_QRC_IN}
          ${CMAKE_CURRENT_SOURCE_DIR}/res/EmotionDisplayPlugin.qml
  COMMENT "Compiling Qt resources for EmotionDisplayPlugin"
)

add_library(EmotionDisplayPlugin SHARED
  src/EmotionDisplayPlugin.cpp
  ${EMOTION_QRC_OUT}
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
)

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
  TARGETS EmotionDisplayPlugin TouchSensorPlugin
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
