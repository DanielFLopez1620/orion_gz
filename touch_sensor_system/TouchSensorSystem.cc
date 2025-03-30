#include <gz/msgs/boolean.pb.h>

#include <string>
#include <utility>
#include <unordered_map>

#include <gz/common/Profiler.hh>
#include <gz/plugin/Register.hh>
#include <gz/sensors/SensorFactory.hh>

#include <sdf/Sensor.hh>

#include <gz/sim/components/CustomSensor.hh>
#include <gz/sim/components/Name.hh>
#include <gz/sim/components/ParentEntity.hh>
#include <gz/sim/components/Sensor.hh>
#include <gz/sim/components/World.hh>
#include <gz/sim/EntityComponentManager.hh>
#include <gz/sim/Util.hh>

#include "TouchSensorCustom.hh"
#include "TouchSensorSystem.hh"

// This is required to register the plugin. Make sure the interfaces match
// what's in the header.


using namespace custom;

void TouchSensorSystem::PreUpdate(const gz::sim::UpdateInfo &,
	gz::sim::EntityComponentManager &_ecm)
{
	_ecm.EachNew<gz::sim::components::CustomSensor,
		gz::sim::components::ParentEntity>(
			[&](const gz::sim::Entity &_entity,
				const gz::sim::components::CustomSensor *_custom,
				const gz::sim::components::ParentEntity *_parent)-> bool
			{
				auto sensorScopedName = gz::sim::removeParentScope(
					gz::sim::scopedName(_entity, _ecm, "::", false), "::");
				sdf::Sensor data = _custom->Data();
				data.SetName(sensorScopedName);

				if(data.Topic().empty())
				{
					std::string topic = scopedName(_entity, _ecm) + "/touch_sensor";
					data.SetTopic(topic);
				}
				
				gz::sensors::SensorFactory sensorFactory;
				auto sensor = sensorFactory.CreateSensor<custom::TouchSensor>(data);
				if (nullptr == sensor)
				{
					gzerr << "Failed to create touch sensor [" << sensorScopedName << "]"
						  << std::endl;
					return false;
				}

				auto parentName = _ecm.Component<gz::sim::components::Name>(
					_parent->Data())->Data();
				sensor->SetParent(parentName);

				_ecm.CreateComponent(
					_entity, gz::sim::components::SensorTopic(sensor->Topic()));

				this->entitySensorMap.insert(std::make_pair(_entity, std::move(sensor)));

				return true;
			});
}

// Here we implement the PostUpdate function, which is called at every
// iteration.
void TouchSensorSystem::PostUpdate(const gz::sim::UpdateInfo &_info,
    const gz::sim::EntityComponentManager &_ecm)
{
	// This is a simple example of how to get information from UpdateInfo.
	std::string msg = "Hello, world! Simulation is ";		
	if(!_info.paused)
	{
		for(auto &[entity, sensor] : this->entitySensorMap)
		{
			sensor->NewContact(true);
			sensor->Update(_info.simTime);
		}
		msg += "not ";
	}
	else
	{
		msg += "paused.";
		// Messages printed with gzmsg only show when running with verbosity 3 or
		// higher (i.e. gz sim -v 3)
		gzmsg << msg << std::endl;
	}
}

void TouchSensorSystem::RemoveSensorEntities(
	const gz::sim::EntityComponentManager &_ecm)
{
	_ecm.EachRemoved<gz::sim::components::CustomSensor>(
		[&](const gz::sim::Entity &_entity,
			const gz::sim::components::CustomSensor *)->bool
		{
			if(this->entitySensorMap.erase(_entity) == 0)
			{
				gzerr << "internal erro, missing touch sensor entity ["
					  << _entity << "]" << std::endl;
			}
			return true;
		});
}

GZ_ADD_PLUGIN(
    TouchSensorSystem,
    gz::sim::System,
	TouchSensorSystem::ISystemPreUpdate,
    TouchSensorSystem::ISystemPostUpdate)

GZ_ADD_PLUGIN_ALIAS(TouchSensorSystem, "custom::TouchSensorSytem")