#ifndef SYSTEM_PLUGIN_TOUCH_SENSOR_HH_
#define SYSTEM_PLUGIN_TOUCH_SENSOR_HH_

// The only required include in the header is this one.
// All others will depend on what your plugin does.
#include <gz/sim/System.hh>
#include <gz/sensors/Noise.hh>
#include <gz/transport/Node.hh>

// It's good practice to use a custom namespace for your project.
namespace custom
{
  // This is the main plugin's class. It must inherit from System and at least
  // one other interface.
  // Here we use `ISystemPostUpdate`, which is used to get results after
  // physics runs. The opposite of that, `ISystemPreUpdate`, would be used by
  // plugins that want to send commands.
	class TouchSensorSystem:
		public gz::sim::System,
		public gz::sim::ISystemPreUpdate,
		public gz::sim::ISystemPostUpdate
		{
			public: 
			
			void PreUpdate(const gz::sim::UpdateInfo &_info,
				gz::sim::EntityComponentManager &_ecm) final;
			
			// Plugins inheriting ISystemPostUpdate must implement the PostUpdate
			// callback. This is called at every simulation iteration after the physics
			// updates the world. The _info variable provides information such as time,
			// while the _ecm provides an interface to all entities and components in
			// simulation.
			void PostUpdate(const gz::sim::UpdateInfo &_info,
				const gz::sim::EntityComponentManager &_ecm) final;

			private: 
			
			void RemoveSensorEntities(
				const gz::sim::EntityComponentManager &_ecm);

			std::unordered_map<gz::sim::Entity, std::shared_ptr<TouchSensor>> entitySensorMap;

			
		};
}
#endif