#ifndef ROS2_CONTROL_DEMO_EXAMPLE_2__ENCODER_HPP
#define ROS2_CONTROL_DEMO_EXAMPLE_2__ENCODER_HPP

#include <pigpio.h>
#include "rclcpp/rclcpp.hpp"

void updateEncoder(int gpio, int level, uint32_t tick, void *data);

class Encoder {
    public:
        int enc_a;
        int enc_b;

        int encoderValue = 0;
        int lastEncoded = 0;

        Encoder() = default;

        Encoder(const int &enc_a, const int &enc_b) {
            this->enc_a = enc_a;
            this->enc_b = enc_b;

            gpioSetMode(enc_a, PI_INPUT);
            gpioSetMode(enc_b, PI_INPUT);

            gpioSetPullUpDown(enc_a, PI_PUD_UP);
            gpioSetPullUpDown(enc_b, PI_PUD_UP);

            gpioSetISRFuncEx(enc_a, EITHER_EDGE, 0, updateEncoder, this);
            gpioSetISRFuncEx(enc_b, EITHER_EDGE, 0, updateEncoder, this);
            
            RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Init encoders");
        };

        ~Encoder();

        int read() {
            return encoderValue;
        }
};

void updateEncoder(int gpio, int level, uint32_t tick, void *data) {
    Encoder *enc = static_cast<Encoder *>(data);

    int msb = gpioRead(enc->enc_a);
    int lsb = gpioRead(enc->enc_b);
    int encoded = (msb << 1) | lsb;
    int sum = (enc->lastEncoded << 2) | encoded;

    if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011)
        enc->encoderValue--;

    if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000)
        enc->encoderValue++;

    enc->lastEncoded = encoded;

    RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Updated encoder");
}

#endif