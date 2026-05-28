#include "orion_gz_plugins/TouchSensorPlugin.hpp"

#include <gz/gui/Application.hh>
#include <gz/gui/GuiEvents.hh>
#include <gz/gui/MainWindow.hh>
#include <gz/math/Vector2.hh>
#include <gz/plugin/Register.hh>
#include <gz/rendering/RenderingIface.hh>

GZ_ADD_PLUGIN(
    orion_gz_plugins::TouchSensorPlugin,
    gz::gui::Plugin)

GZ_ADD_PLUGIN_ALIAS(
    orion_gz_plugins::TouchSensorPlugin,
    "orion_gz_plugins::TouchSensorPlugin")

namespace orion_gz_plugins
{

// Default sensor configuration matching the ORION firmware topics
static const std::vector<TouchSensorPlugin::SensorConfig> DEFAULT_SENSORS = {
    {"touch_ul", "/interaction/touch_ul"},
    {"touch_ur", "/interaction/touch_ur"},
    {"touch_ll", "/interaction/touch_ll"},
    {"touch_lr", "/interaction/touch_lr"},
};

TouchSensorPlugin::TouchSensorPlugin()
    : gz::gui::Plugin()
{
}

TouchSensorPlugin::~TouchSensorPlugin() = default;

void TouchSensorPlugin::LoadConfig(const tinyxml2::XMLElement *_pluginElem)
{
    // Sensor list: SDF <sensor> entries fully replace the defaults so the
    // same topic isn't advertised twice (once by a default and once by an
    // override targeting a different visualName). The defaults are only
    // applied when the SDF block has no <sensor> children at all.
    this->sensors.clear();

    if (_pluginElem)
    {
        // Optional debounce override
        if (auto *elem = _pluginElem->FirstChildElement("debounce_ms"))
        {
            int ms = 250;
            elem->QueryIntText(&ms);
            this->debounceDuration = std::chrono::milliseconds(ms);
        }

        // Sensor list from SDF
        for (auto *elem = _pluginElem->FirstChildElement("sensor");
             elem != nullptr;
             elem = elem->NextSiblingElement("sensor"))
        {
            const char *name  = elem->Attribute("name");
            const char *topic = elem->Attribute("topic");
            if (!name || !topic)
                continue;
            this->sensors.push_back({name, topic});
        }
    }

    if (this->sensors.empty())
        this->sensors = DEFAULT_SENSORS;

    // Advertise publishers
    for (const auto &s : this->sensors)
    {
        this->publishers[s.visualName] =
            this->node.Advertise<gz::msgs::Boolean>(s.topic);
        gzmsg << "[TouchSensorPlugin] Sensor '" << s.visualName
              << "' → " << s.topic << "\n";
    }

    // Install event filter to intercept render and mouse events
    gz::gui::App()
        ->findChild<gz::gui::MainWindow *>()
        ->installEventFilter(this);

    gzmsg << "[TouchSensorPlugin] Ready. Debounce "
          << this->debounceDuration.count() << " ms.\n";
}

bool TouchSensorPlugin::eventFilter(QObject *_obj, QEvent *_event)
{
    // Render thread: initialise scene / process pending click
    if (_event->type() == gz::gui::events::Render::kType)
    {
        this->OnRender();
        return false;
    }

    // UI thread: capture left-click on the 3D scene
    if (_event->type() == gz::gui::events::LeftClickOnScene::kType)
    {
        auto *click = reinterpret_cast<gz::gui::events::LeftClickOnScene *>(_event);
        std::lock_guard<std::mutex> lock(this->mouseMutex);
        this->pendingMouse = click->Mouse();
        return false;
    }

    return QObject::eventFilter(_obj, _event);
}

void TouchSensorPlugin::OnRender()
{
    // One-time scene + camera + ray-query setup
    if (!this->scene)
    {
        this->scene = gz::rendering::sceneFromFirstRenderEngine();
        if (!this->scene)
            return;

        // Use the first available camera (the user viewport camera)
        for (unsigned int i = 0; i < this->scene->SensorCount(); ++i)
        {
            auto sensor = this->scene->SensorByIndex(i);
            this->camera = std::dynamic_pointer_cast<gz::rendering::Camera>(sensor);
            if (this->camera)
                break;
        }

        if (!this->camera)
        {
            gzwarn << "[TouchSensorPlugin] No camera found in scene.\n";
            return;
        }

        this->rayQuery = this->scene->CreateRayQuery();
        gzmsg << "[TouchSensorPlugin] Scene and camera initialised.\n";
    }

    if (!this->camera || !this->rayQuery)
        return;

    // Consume pending mouse click
    std::optional<gz::common::MouseEvent> mouseEvt;
    {
        std::lock_guard<std::mutex> lock(this->mouseMutex);
        mouseEvt = this->pendingMouse;
        this->pendingMouse.reset();
    }

    if (!mouseEvt.has_value())
        return;

    this->ProcessMouseClick(*mouseEvt);
}

void TouchSensorPlugin::ProcessMouseClick(
    const gz::common::MouseEvent &_mouse)
{
    // Convert pixel coords to normalised device coords [-1, 1]
    unsigned int w = this->camera->ImageWidth();
    unsigned int h = this->camera->ImageHeight();
    if (w == 0 || h == 0)
        return;

    double nx =  2.0 * static_cast<double>(_mouse.Pos().X()) / w - 1.0;
    double ny = -2.0 * static_cast<double>(_mouse.Pos().Y()) / h + 1.0;

    this->rayQuery->SetFromCamera(
        this->camera, gz::math::Vector2d(nx, ny));

    gz::rendering::RayQueryResult result = this->rayQuery->ClosestPoint();
    if (!result)
        return;

    // Identify the hit visual by its scene name
    auto visual = this->scene->VisualById(result.objectId);
    if (!visual)
        return;

    // Visual names in GZ include the full scoped path; match on suffix
    std::string visualName = visual->Name();

    for (const auto &s : this->sensors)
    {
        if (visualName.find(s.visualName) == std::string::npos)
            continue;

        // Debounce check
        auto now = std::chrono::steady_clock::now();
        auto it  = this->lastTrigger.find(s.visualName);
        if (it != this->lastTrigger.end() &&
            (now - it->second) < this->debounceDuration)
        {
            return;
        }
        this->lastTrigger[s.visualName] = now;

        // Publish
        gz::msgs::Boolean msg;
        msg.set_data(true);
        this->publishers[s.visualName].Publish(msg);

        gzmsg << "[TouchSensorPlugin] " << s.visualName << " triggered → "
              << s.topic << "\n";
        return;
    }
}

}  // namespace orion_gz_plugins
