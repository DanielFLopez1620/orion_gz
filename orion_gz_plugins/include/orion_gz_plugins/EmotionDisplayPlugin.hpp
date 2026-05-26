#pragma once

#include <array>
#include <atomic>
#include <string>

#include <gz/gui/Plugin.hh>
#include <gz/msgs/int32.pb.h>
#include <gz/rendering/RenderTypes.hh>
#include <gz/transport/Node.hh>

namespace orion_gz_plugins
{

/// GUI plugin that renders the ORION emotion face bitmaps as textures on the
/// "screen_visual" visual inside the GZ rendering scene.
///
/// Textures are generated at build time from the 176×220 1-bit bitmaps in
/// orion_interaction_micro_ros/emotions.hpp (bit=1 → emotion color, bit=0 → black).
/// At runtime the plugin uses ament_index to locate the installed PNGs and
/// applies them via gz::rendering::Material::SetTexture().
///
/// Index → emotion mapping (matches emotion_color[] in emotions.hpp):
///   0 angry  1 disgust  2 fear  3 happy  4 neutral  5 sad  6 surprise  7 wink
///
/// GUI config usage (world SDF <gui> section):
///   <plugin name="EmotionDisplayPlugin" filename="libEmotionDisplayPlugin.so">
///     <!-- optional: override target visual (substring match on scoped name) -->
///     <visual_name>screen_visual</visual_name>
///     <!-- optional: override texture directory -->
///     <texture_dir>/absolute/path/to/textures</texture_dir>
///   </plugin>
class EmotionDisplayPlugin : public gz::gui::Plugin
{
public:
    EmotionDisplayPlugin();
    ~EmotionDisplayPlugin() override;

    void LoadConfig(const tinyxml2::XMLElement *_pluginElem) override;

protected:
    bool eventFilter(QObject *_obj, QEvent *_event) override;

private:
    void OnEmotion(const gz::msgs::Int32 &_msg);
    void OnRender();

    gz::rendering::ScenePtr scene;
    gz::rendering::VisualPtr screenVisual;

    gz::transport::Node node;

    std::atomic<int> pendingEmotion{-1};
    int lastEmotion{-1};

    std::string visualName{"screen_visual"};
    std::string textureDir;

    static constexpr int NUM_EMOTIONS = 8;
    std::array<gz::rendering::MaterialPtr, NUM_EMOTIONS> emotionMaterials;
    bool materialsLoaded{false};
};

}  // namespace orion_gz_plugins
