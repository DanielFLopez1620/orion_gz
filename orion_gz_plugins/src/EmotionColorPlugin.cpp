#include "orion_gz_plugins/EmotionColorPlugin.hpp"

#include <gz/gui/Application.hh>
#include <gz/gui/GuiEvents.hh>
#include <gz/gui/MainWindow.hh>
#include <gz/plugin/Register.hh>
#include <gz/rendering/Material.hh>
#include <gz/rendering/RenderingIface.hh>
#include <gz/rendering/Scene.hh>
#include <gz/rendering/Visual.hh>

GZ_ADD_PLUGIN(
    orion_gz_plugins::EmotionColorPlugin,
    gz::gui::Plugin)

GZ_ADD_PLUGIN_ALIAS(
    orion_gz_plugins::EmotionColorPlugin,
    "orion_gz_plugins::EmotionColorPlugin",
    "EmotionColorPlugin")

namespace orion_gz_plugins
{

// Converted from RGB565 (emotions.hpp → emotion_color[8]):
//   R = bits[15:11]/31   G = bits[10:5]/63   B = bits[4:0]/31
const float EmotionColorPlugin::EMOTION_COLORS[NUM_EMOTIONS][3] = {
    {31.f/31, 20.f/63,  8.f/31},  // 0 angry    0xFA88  orange-red
    {16.f/31, 63.f/63,  0.f/31},  // 1 disgust  0x87E0  green
    {23.f/31, 28.f/63, 24.f/31},  // 2 fear     0xBB98  purple
    {31.f/31, 53.f/63,  4.f/31},  // 3 happy    0xFEA4  yellow
    { 1.f,     1.f,     1.f   },  // 4 neutral  0xFFFF  white
    {11.f/31, 46.f/63,  1.f   },  // 5 sad      0x5DDF  light-blue
    { 0.f,     1.f,    24.f/31},  // 6 surprise 0x07F8  teal
    { 1.f,     1.f,     1.f   },  // 7 wink     0xFFFF  white
};

EmotionColorPlugin::EmotionColorPlugin() = default;
EmotionColorPlugin::~EmotionColorPlugin() = default;

void EmotionColorPlugin::LoadConfig(const tinyxml2::XMLElement *_pluginElem)
{
    if (_pluginElem)
    {
        auto *elem = _pluginElem->FirstChildElement("visual_name");
        if (elem && elem->GetText())
            this->visualName = elem->GetText();
    }

    this->node.Subscribe(
        "/emotion/int",
        &EmotionColorPlugin::OnEmotion,
        this);

    gz::gui::App()
        ->findChild<gz::gui::MainWindow *>()
        ->installEventFilter(this);

    gzmsg << "[EmotionColorPlugin] Subscribed to /emotion/int"
          << " (target visual: '" << this->visualName << "')\n";
}

void EmotionColorPlugin::OnEmotion(const gz::msgs::Int32 &_msg)
{
    int value = _msg.data();
    if (value < 0 || value >= NUM_EMOTIONS)
    {
        gzwarn << "[EmotionColorPlugin] Invalid emotion index: "
               << value << " (valid: 0-" << NUM_EMOTIONS - 1 << ")\n";
        return;
    }
    this->pendingEmotion.store(value);
}

bool EmotionColorPlugin::eventFilter(QObject *_obj, QEvent *_event)
{
    if (_event->type() == gz::gui::events::Render::kType)
        this->OnRender();
    return gz::gui::Plugin::eventFilter(_obj, _event);
}

void EmotionColorPlugin::OnRender()
{
    if (!this->scene)
    {
        this->scene = gz::rendering::sceneFromFirstRenderEngine();
        if (!this->scene)
            return;
        gzmsg << "[EmotionColorPlugin] Acquired rendering scene\n";
    }

    if (!this->screenVisual)
    {
        // Substring match on the scoped visual name. URDF→SDF lumping renames
        // visuals to e.g. "base_link_fixed_joint_lump__screen_visual_108" with
        // a volatile trailing index, so a suffix match against the authored
        // name fails. Pick a substring that is stable and unique across the
        // scene (e.g. "screen_visual", which excludes "screen_sup_visual").
        for (unsigned int i = 0; i < this->scene->VisualCount(); ++i)
        {
            auto vis = this->scene->VisualByIndex(i);
            if (!vis) continue;
            const auto &n = vis->Name();
            if (n.find(this->visualName) != std::string::npos)
            {
                this->screenVisual = vis;
                gzmsg << "[EmotionColorPlugin] Screen visual found: '"
                      << n << "'\n";
                break;
            }
        }
        if (!this->screenVisual)
            return;
    }

    int emotion = this->pendingEmotion.load();
    if (emotion < 0 || emotion == this->lastEmotion)
        return;

    this->lastEmotion = emotion;
    const float *c = EMOTION_COLORS[emotion];

    auto mat = this->scene->CreateMaterial();
    mat->SetAmbient(c[0], c[1], c[2], 1.0f);
    mat->SetDiffuse(c[0], c[1], c[2], 1.0f);
    mat->SetEmissive(c[0] * 0.25f, c[1] * 0.25f, c[2] * 0.25f, 1.0f);
    this->screenVisual->SetMaterial(mat, false);

    gzmsg << "[EmotionColorPlugin] Applied emotion " << emotion
          << " (R=" << c[0] << " G=" << c[1] << " B=" << c[2] << ")\n";
}

}  // namespace orion_gz_plugins
