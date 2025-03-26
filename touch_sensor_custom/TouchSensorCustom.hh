#ifndef TOUCH_SENSOR_CUSTOM_HH
#define TOUCH_SENSOR_CUSTOM_HH

#include<gz/sensors/Sensor.hh>
#include<gz/sensors/SensorTypes.hh>
#include<gz/transport/Node.hh>

namespace touch_sensor
{
    class TouchSensor : public gz::sensors::Sensor
    {
        public: virtual bool Load(const sdf::Sensor &_sdf) override;

        public: virtual bool Update(
            const std::chrono::steady_clock::duration &_now) override;
        
        public: bool getContact() const;

        private: bool contact {false};

        private: gz::transport::Node node;

        private: gz::transport::Node::Publisher pub;
    }
}

#endif