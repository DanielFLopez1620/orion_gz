#include <gz/msgs/boolean.pb.h>

#include <gz/common/Console.hh>
#include <gz/msgs/Utility.hh>
#include <gz/sensors/Util.hh>

#include "TouchSensorCustom.hh"

using namespace touch_sensor;

bool TouchSensor::Load(const sdf::Sensor &_sdf)
{
    auto type = gz::sensors::customType(_sdf);
    if ("touch" != type)
    {
        gzerr << "Trying to load [touch] sensor, but got type["
              << type << "] instaed." << std::endl;
        return false;
    }

    gz::sensors::Sensor::Load(_sdf);

    this->pub = this->node.Advertise<gz::msgs::Boolean>(this->Topic());

    if (!_sdf.Element()->HasElement("gz:touch"))
    {
        gzerr << "No custom configuration for [" << this->Topic() << "]"
              << std::endl;
        return false;
    }

    auto customElement = _sdf.Element()->GetElement("gz:touch");
    if (!customElement->HasElement("contact_link_name"))
    {
        gzerr << "Failed to load contact link" << std::endl;
        return false;
    }

    gzmsg << "Found contact for touch sensor..."<< std::endl;
    return true;
}

bool TouchSensor::Update(const std::chrono::steady_clock::duration &_now)
{
    gz::msgs::Boolean msg;
    *msg.mutable_header()->mutable_stamp() = gz::msgs::Convert(_now);
    auto frame = msg.mutable_header()->add_data();
    frame->set_key("frame_id");
    frame->add_value(this->Name());

    msg.set_data(this->contact);
    this->AddSequence(msg.mutable_header());
    this->pub.Publish(msg);

    return true;

}

void TouchSensor::NewContact(bool contact)
{
    this->contact = contact;
}