#pragma once

#include <chrono>
#include <map>
#include <mutex>
#include <optional>
#include <string>
#include <vector>

#include <gz/common/MouseEvent.hh>
#include <gz/gui/Plugin.hh>
#include <gz/msgs/boolean.pb.h>
#include <gz/rendering/RayQuery.hh>
#include <gz/rendering/Scene.hh>
#include <gz/transport/Node.hh>

namespace orion_gz_plugins
{

/// GUI plugin that publishes a Bool(true) on the matching GZ transport topic
/// when the user left-clicks on one of the four ORION touch-sensor visuals.
///
/// Detection: ray-query from the rendering camera at the mouse screen position.
/// Each sensor is identified by the name of its visual in the scene graph.
/// A 250 ms per-sensor debounce prevents duplicate publications.
///
/// Default sensor → topic mapping (override via SDF <sensor> elements):
///   touch_ul → /interaction/touch_ul
///   touch_ur → /interaction/touch_ur
///   touch_ll → /interaction/touch_ll
///   touch_lr → /interaction/touch_lr
///
/// GUI config usage (world SDF <gui> section):
///   <plugin name="TouchSensorPlugin" filename="libTouchSensorPlugin.so">
///     <!-- optional: override debounce (ms) -->
///     <debounce_ms>250</debounce_ms>
///     <!-- optional: add / rename sensors -->
///     <sensor name="touch_ul" topic="/interaction/touch_ul"/>
///   </plugin>
class TouchSensorPlugin : public gz::gui::Plugin
{
public:
    TouchSensorPlugin();
    ~TouchSensorPlugin() override;

    void LoadConfig(const tinyxml2::XMLElement *_pluginElem) override;

protected:
    bool eventFilter(QObject *_obj, QEvent *_event) override;

private:
    void OnRender();
    void ProcessMouseClick(const gz::common::MouseEvent &_mouse);

    // Rendering
    gz::rendering::ScenePtr scene;
    gz::rendering::CameraPtr camera;
    gz::rendering::RayQueryPtr rayQuery;

    // Pending click (set from Qt thread, consumed in render thread)
    std::mutex mouseMutex;
    std::optional<gz::common::MouseEvent> pendingMouse;

    // Transport
    gz::transport::Node node;
    std::map<std::string, gz::transport::Node::Publisher> publishers;

public:
    struct SensorConfig
    {
        std::string visualName;
        std::string topic;
    };

private:
    std::vector<SensorConfig> sensors;
    std::chrono::milliseconds debounceDuration{250};

    // Debounce: last trigger time per visual name
    std::map<std::string, std::chrono::steady_clock::time_point> lastTrigger;
};

}  // namespace orion_gz_plugins
