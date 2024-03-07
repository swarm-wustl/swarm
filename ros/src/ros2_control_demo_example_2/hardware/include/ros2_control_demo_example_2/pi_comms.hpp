#include <string>
#include <sstream>
#include <iostream>
// #include <pigpio.h>
#include <ros2_control_demo_example_2/encoder.hpp>
#include <vector>
#include "rclcpp/rclcpp.hpp"

class PiComms {
  private:
    bool is_connected = false;

    const int MOTOR_FWD = 17;
    const int MOTOR_REV = 22;

    const int ENC_1_A = 5;
    const int ENC_1_B = 6;

    const int ENC_2_A = 7;
    const int ENC_2_B = 8;

    Encoder enc1;
    Encoder enc2;
    
  public:
    PiComms();
    ~PiComms();
    
    void connect() {
      std::cout << "Connecting to Pi... " << std::flush;

      int status = 1; // gpioInitialise();
      if (status < 0) {
        std::cout << "ERROR: Failed to connect to Pi" << std::endl;
      }

      // gpioSetMode(MOTOR_FWD, PI_OUTPUT);
      // gpioSetMode(MOTOR_REV, PI_OUTPUT);

      enc1 = Encoder(ENC_1_A, ENC_1_B);
      enc2 = Encoder(ENC_2_A, ENC_2_B);
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set pin modes");

      is_connected = true;

      std::cout << "done!" << std::endl;
    }

    void disconnect() {
      std::cout << "Disconnecting from Pi... " << std::flush;

      // gpioTerminate();
      is_connected = false;

      std::cout << "done!" << std::endl;
    }

    bool connected() const {
      return is_connected;
    }

    void read_encoder_values(int &val_1, int &val_2)
    {
      val_1 = enc1.read();
      val_2 = enc2.read();
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Read encoder values");
    }

    void set_motor_values(int val_1, int val_2)
    {
      // TODO: change this to integrate with PID
      // gpioPWM(PIN_LEFT, val_1);
      // gpioPWM(PIN_RIGHT, val_2);
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set motor values");
    }

    void set_pid_values(int k_p, int k_d, int k_i, int k_o)
    {
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set PID constants");
    }
};

