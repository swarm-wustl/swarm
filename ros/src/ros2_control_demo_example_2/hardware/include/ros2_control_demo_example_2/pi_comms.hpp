#ifndef ROS2_CONTROL_DEMO_EXAMPLE_2__PI_COMMS_HPP_
#define ROS2_CONTROL_DEMO_EXAMPLE_2__PI_COMMS_HPP_

#include <string>
#include <sstream>
#include <iostream>
#include <pigpiod_if2.h>
#include <ros2_control_demo_example_2/encoder.hpp>
#include <vector>
#include "rclcpp/rclcpp.hpp"

class PiComms {
  private:
    int pi_code = -1;

    const int ENABLE = 17;

    const int MOTOR_FWD_A = 27;
    const int MOTOR_FWD_B = 22;
    
    const int MOTOR_REV_A = 20;
    const int MOTOR_REV_B = 19;

    const int ENC_1_A = 5;
    const int ENC_1_B = 6;

    const int ENC_2_A = 7;
    const int ENC_2_B = 8;

    Encoder enc1;
    Encoder enc2;
    
  public:
    PiComms() = default;
    
    void connect() {
      std::cout << "Connecting to Pi... " << std::flush;

      pi_code = pigpio_start(NULL, NULL);
      if (pi_code < 0) {
        std::cout << "ERROR: Failed to connect to Pi" << std::endl;
        return;
      }

      set_mode(pi_code, ENABLE, PI_INPUT);

      set_mode(pi_code, MOTOR_FWD_A, PI_INPUT);
      set_mode(pi_code, MOTOR_FWD_B, PI_INPUT);

      set_mode(pi_code, MOTOR_REV_A, PI_INPUT);
      set_mode(pi_code, MOTOR_REV_B, PI_INPUT);

      enc1 = Encoder(pi_code, ENC_1_A, ENC_1_B);
      enc2 = Encoder(pi_code, ENC_2_A, ENC_2_B);

      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set pin modes");

      std::cout << "done!" << std::endl;
    }

    void disconnect() {
      std::cout << "Disconnecting from Pi... " << std::flush;

      pigpio_stop(pi_code);
      pi_code = -1;

      std::cout << "done!" << std::endl;
    }

    bool connected() const {
      return pi_code >= 0;
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
      if (val_1 > 0) {
        set_PWM_dutycycle(pi_code, MOTOR_FWD_A, val_1);
        set_PWM_dutycycle(pi_code, MOTOR_FWD_B, 0);
      } else if (val_1 < 0) {
        set_PWM_dutycycle(pi_code, MOTOR_FWD_A, 0);
        set_PWM_dutycycle(pi_code, MOTOR_FWD_B, -val_1);
      } else {
        set_PWM_dutycycle(pi_code, MOTOR_FWD_A, 0);
        set_PWM_dutycycle(pi_code, MOTOR_FWD_B, 0);
      }

      gpio_write(pi_code, ENABLE, 1);

      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set motor values");
    }

    void set_pid_values(int k_p, int k_d, int k_i, int k_o)
    {
      RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Set PID constants");
    }
};

#endif