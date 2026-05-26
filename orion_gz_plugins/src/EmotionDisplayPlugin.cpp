#include "orion_gz_plugins/EmotionDisplayPlugin.hpp"

#include <gz/gui/Application.hh>
#include <gz/gui/GuiEvents.hh>
#include <gz/gui/MainWindow.hh>
#include <gz/math/Color.hh>
#include <gz/plugin/Register.hh>
#include <gz/rendering/Material.hh>
#include <gz/rendering/RenderEngine.hh>
#include <gz/rendering/RenderingIface.hh>
#include <gz/rendering/Scene.hh>
#include <gz/rendering/Visual.hh>

#include <ament_index_cpp/get_package_share_directory.hpp>

GZ_ADD_PLUGIN(
    orion_gz_plugins::EmotionDisplayPlugin,
    gz::gui::Plugin)

GZ_ADD_PLUGIN_ALIAS(
    orion_gz_plugins::EmotionDisplayPlugin,
    "orion_gz_plugins::EmotionDisplayPlugin",
    "EmotionDisplayPlugin")

namespace orion_gz_plugins
{

EmotionDisplayPlugin::EmotionDisplayPlugin() = default;
EmotionDisplayPlugin::~EmotionDisplayPlugin() = default;

void EmotionDisplayPlugin::LoadConfig(const tinyxml2::XMLElement *_pluginElem)
{
    // Resolve texture directory via ament_index (overrideable from SDF)
    try
    {
        auto share = ament_index_cpp::get_package_share_directory("orion_gz_plugins");
        this->textureDir = share + "/textures";
    }
    catch (const std::exception &e)
    {
        gzerr << "[EmotionDisplayPlugin] ament_index lookup failed: " << e.what()
              << " — set <texture_dir> in SDF as fallback\n";
    }

    if (_pluginElem)
    {
        if (auto *e = _pluginElem->FirstChildElement("visual_name"))
            if (e->GetText()) this->visualName = e->GetText();
        if (auto *e = _pluginElem->FirstChildElement("texture_dir"))
            if (e->GetText()) this->textureDir = e->GetText();
    }

    this->node.Subscribe(
        "/emotion/int",
        &EmotionDisplayPlugin::OnEmotion,
        this);

    gz::gui::App()
        ->findChild<gz::gui::MainWindow *>()
        ->installEventFilter(this);

    gzmsg << "[EmotionDisplayPlugin] Subscribed to /emotion/int"
          << "  texture_dir='" << this->textureDir << "'\n";
}

void EmotionDisplayPlugin::OnEmotion(const gz::msgs::Int32 &_msg)
{
    int value = _msg.data();
    if (value < 0 || value >= NUM_EMOTIONS)
    {
        gzwarn << "[EmotionDisplayPlugin] Invalid emotion index: "
               << value << " (valid: 0-" << NUM_EMOTIONS - 1 << ")\n";
        return;
    }
    this->pendingEmotion.store(value);
}

bool EmotionDisplayPlugin::eventFilter(QObject *_obj, QEvent *_event)
{
    if (_event->type() == gz::gui::events::Render::kType)
        this->OnRender();
    return gz::gui::Plugin::eventFilter(_obj, _event);
}

void EmotionDisplayPlugin::OnRender()
{
    // ── Acquire scene ─────────────────────────────────────────────────────────
    if (!this->scene)
    {
        this->scene = gz::rendering::sceneFromFirstRenderEngine();
        if (!this->scene)
            return;
        gzmsg << "[EmotionDisplayPlugin] Acquired rendering scene\n";
    }

    // ── Locate screen visual (once) ───────────────────────────────────────────
    // Use suffix matching ("::visualName") to avoid matching longer names that
    // contain visualName as a substring (e.g. "screen_color_visual" ⊃ "screen_visual").
    if (!this->screenVisual)
    {
        const std::string suffix = "::" + this->visualName;
        for (unsigned int i = 0; i < this->scene->VisualCount(); ++i)
        {
            auto vis = this->scene->VisualByIndex(i);
            if (!vis) continue;
            const auto &n = vis->Name();
            if (n.size() >= suffix.size() &&
                n.compare(n.size() - suffix.size(), suffix.size(), suffix) == 0)
            {
                this->screenVisual = vis;
                gzmsg << "[EmotionDisplayPlugin] Screen visual found: '"
                      << n << "'\n";
                break;
            }
        }
        if (!this->screenVisual)
            return;
    }

    // ── Pre-load all 8 materials once the scene and visual are ready ──────────
    if (!this->materialsLoaded)
    {
        for (int i = 0; i < NUM_EMOTIONS; ++i)
        {
            // Use the absolute path — same approach gz-sim uses internally
            // when loading textured visuals from SDF (via common::findFile).
            const std::string texPath =
                this->textureDir + "/emotion_" + std::to_string(i) + ".png";
            auto mat = this->scene->CreateMaterial();
            if (!mat)
            {
                gzerr << "[EmotionDisplayPlugin] CreateMaterial() returned null for index "
                      << i << "\n";
                continue;
            }

            // Use the texture as BOTH albedo and emissive map:
            // - Albedo: standard diffuse texture (responds to lighting)
            // - Emissive map: self-illuminated copy of the bitmap, so the face
            //   pattern is fully visible regardless of scene lighting/shadows.
            mat->SetTexture(texPath);
            mat->SetEmissiveMap(texPath);
            mat->SetAmbient(gz::math::Color::White);
            mat->SetDiffuse(gz::math::Color::White);
            mat->SetEmissive(gz::math::Color::White);

            this->emotionMaterials[i] = mat;
            gzmsg << "[EmotionDisplayPlugin] Material[" << i << "]"
                  << " hasTex=" << mat->HasTexture()
                  << " path='" << texPath << "'\n";
        }
        this->materialsLoaded = true;
    }

    // ── Apply pending emotion ─────────────────────────────────────────────────
    int emotion = this->pendingEmotion.load();
    if (emotion < 0 || emotion == this->lastEmotion)
        return;

    this->lastEmotion = emotion;
    this->screenVisual->SetMaterial(this->emotionMaterials[emotion], false);

    gzmsg << "[EmotionDisplayPlugin] Applied emotion " << emotion << "\n";
}

}  // namespace orion_gz_plugins
