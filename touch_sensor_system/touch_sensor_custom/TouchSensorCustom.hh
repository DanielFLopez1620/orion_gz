#ifndef TOUCH_SENSOR_CUSTOM_HH
#define TOUCH_SENSOR_CUSTOM_HH

#include<gz/sensors/Sensor.hh>
#include<gz/sensors/SensorTypes.hh>
#include<gz/transport/Node.hh>

namespace custom
{
    class TouchSensor : public gz::sensors::Sensor
    {
    public: 
        virtual bool Load(const sdf::Sensor &_sdf) override;

        virtual bool Update(
            const std::chrono::steady_clock::duration &_now) override;
        
        void NewContact(bool contact);

    private: 
        bool contact {false};

        gz::transport::Node node;

        gz::transport::Node::Publisher pub;
    };
}

#endif