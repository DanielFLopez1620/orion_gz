#pragma once

#include <atomic>
#include <string>

#include <gz/gui/Plugin.hh>
#include <gz/msgs/int32.pb.h>
#include <gz/rendering/RenderTypes.hh>
#include <gz/transport/Node.hh>

namespace orion_gz_plugins
{

/// GUI plugin that maps /emotion/int (Int32 [0-7]) to a solid color on the
/// "screen_visual" visual inside the ORION model.
///
/// Colors are converted from the RGB565 table in orion_interaction_micro_ros
/// (emotions.hpp). The mapping is:
///   0 angry    0xFA88  1 disgust  0x87E0  2 fear     0xBB98  3 happy    0xFEA4
///   4 neutral  0xFFFF  5 sad      0x5DDF  6 surprise 0x07F8  7 wink     0xFFFF
///
/// GUI config usage (world SDF <gui> section):
///   <plugin name="EmotionColorPlugin" filename="libEmotionColorPlugin.so">
///     <!-- optional: override target visual name (substring match) -->
///     <visual_name>screen_visual</visual_name>
///   </plugin>
class EmotionColorPlugin : public gz::gui::Plugin
{
public:
    EmotionColorPlugin();
    ~EmotionColorPlugin() override;

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

    static constexpr int NUM_EMOTIONS = 8;
    static const float EMOTION_COLORS[NUM_EMOTIONS][3];
};

}  // namespace orion_gz_plugins
