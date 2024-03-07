// #include <pigpio.h>
#include "rclcpp/rclcpp.hpp"

class Encoder {
    private:
        int enc_a;
        int enc_b;

        int encoderValue = 0;
        int lastEncoded = 0;

        void updateEncoder(int gpio, int level, int tick) {
            int msb = 1; //gpioRead(enc_a);
            int lsb = 1; //gpioRead(enc_b);

            int encoded = (msb << 1) | lsb;
            int sum = (lastEncoded << 2) | encoded;

            if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011)
                encoderValue--;

            if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000)
                encoderValue++;

            lastEncoded = encoded;

            RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Updated encoder");
        }

    public:
        Encoder(const int &enc_a, const int &enc_b) {
            this->enc_a = enc_a;
            this->enc_b = enc_b;

            /*gpioSetMode(enc_a, PI_INPUT);
            gpioSetMode(enc_b, PI_INPUT);

            gpioSetPullUpDown(enc_a, PI_PUD_UP);
            gpioSetPullUpDown(enc_b, PI_PUD_UP);

            gpioSetISRFunc(enc_a, EITHER_EDGE, 0, updateEncoder);
            gpioSetISRFunc(enc_b, EITHER_EDGE, 0, updateEncoder);*/
            RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Init encoders");
        };

        ~Encoder();

        int read() {
            return encoderValue;
        }
};