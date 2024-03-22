#ifndef ROS2_CONTROL_DEMO_EXAMPLE_2__ENCODER_HPP
#define ROS2_CONTROL_DEMO_EXAMPLE_2__ENCODER_HPP

#include <pigpiod_if2.h>
#include "rclcpp/rclcpp.hpp"

void updateEncoder(int pi_code, unsigned gpio, unsigned level, uint32_t tick, void *data);

class Encoder {
    public:
        int pi_code;

        int enc_a;
        int enc_b;

        int encoderValue = 0;
        int lastEncoded = 0;

        Encoder() = default;

        Encoder(const int& pi_code, const int &enc_a, const int &enc_b) {
            this->pi_code = pi_code;

            this->enc_a = enc_a;
            this->enc_b = enc_b;

            set_mode(pi_code, enc_a, PI_INPUT);
            set_mode(pi_code, enc_b, PI_INPUT);

            set_pull_up_down(pi_code, enc_a, PI_PUD_UP);
            set_pull_up_down(pi_code, enc_b, PI_PUD_UP);

            std::cout << "in encoders..." << std::flush;

            callback_ex(pi_code, enc_a, EITHER_EDGE, updateEncoder, this);
            callback_ex(pi_code, enc_b, EITHER_EDGE, updateEncoder, this);

            std::cout << "past callbacks..." << std::flush;
            
            RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Init encoders");
        };

        int read() {
            return encoderValue;
        }
};

void updateEncoder(int pi_code, unsigned gpio, unsigned level, uint32_t tick, void *data) {
    std::cout << "in callback..." << std::flush;
    Encoder *enc = static_cast<Encoder *>(data);

    int msb = gpio_read(pi_code, enc->enc_a);
    int lsb = gpio_read(pi_code, enc->enc_b);
    int encoded = (msb << 1) | lsb;
    int sum = (enc->lastEncoded << 2) | encoded;

    if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011)
        enc->encoderValue--;

    if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000)
        enc->encoderValue++;

    enc->lastEncoded = encoded;

    std::cout << "past callback..." << std::flush;

    RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Updated encoder");
}

#endif